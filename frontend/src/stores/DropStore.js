import { makeObservable, observable, action, computed } from 'mobx'
import { axios } from '../utils/ApiClient'

export default class DropStore {
  @observable drops = []
  @observable drop = undefined
  @observable inProgress = true
  @observable previewIsLoading = true
  @observable cursor = undefined
  @observable uploadProgress = undefined
  chunkSize = 1048576

  constructor() {
    makeObservable(this)
  }

  @action
  async loadDropFile(dropFileHash) {
    this.inProgress = true
    this.previewIsLoading = true
    const resp = await axios.get(`/api/drops/files/${dropFileHash}`)
    this.drop.dropfiles.push(resp.data)
    this.inProgress = false
  }

  @action
  async uploadDropFile(dropHash, file) {
    this.uploadProgress = 0
    let chunkNumber = 0
    let fileTotalSize = file.size
    let headers = {
      'content-type': 'multipart/form-data',
      'Drop-File-Name': file.name,
      'File-Total-Size': fileTotalSize,
      'Chunk-Size': this.chunkSize,
      'Drop-Hash': dropHash
    }
    while (true) {
      const chunk = file.slice(
        this.chunkSize * chunkNumber,
        Math.min(this.chunkSize * (chunkNumber + 1), fileTotalSize + 1)
      )
      let data = new FormData()
      data.append('chunk', chunk)
      this.uploadProgress =
        (this.chunkSize * (chunkNumber - 1) + chunk.size) / fileTotalSize * 100
      chunkNumber = chunkNumber + 1
      headers['Chunk-Number'] = chunkNumber
      const resp = await axios.post('/api/drops/upload/chunks', data, {
        headers: headers
      })
      if (resp.data) {
        if (resp.data.drop_file_hash) {
          headers['Drop-File-Hash'] = resp.data.drop_file_hash
        }
      }
      if (resp.status === 201) {
        this.uploadProgress = undefined
        break
      }
    }
    return headers['Drop-File-Hash']
  }

  @action
  async uploadDrop(file) {
    this.uploadProgress = 0
    let chunkNumber = 0
    let fileTotalSize = file.size
    let headers = {
      'content-type': 'multipart/form-data',
      'File-Total-Size': fileTotalSize,
      'Drop-File-Name': file.name,
      'Chunk-Size': this.chunkSize
    }
    while (true) {
      const chunk = file.slice(
        this.chunkSize * chunkNumber,
        Math.min(this.chunkSize * (chunkNumber + 1), fileTotalSize + 1)
      )
      let data = new FormData()
      data.append('chunk', chunk)
      this.uploadProgress =
        (this.chunkSize * (chunkNumber - 1) + chunk.size) / fileTotalSize * 100
      chunkNumber = chunkNumber + 1
      headers['Chunk-Number'] = chunkNumber
      const resp = await axios.post('/api/drops/upload/chunks', data, {
        headers: headers
      })
      if (resp.data) {
        if (resp.data.drop_hash) {
          headers['Drop-Hash'] = resp.data.drop_hash
        }
        if (resp.data.drop_file_hash) {
          headers['Drop-File-Hash'] = resp.data.drop_file_hash
        }
      }
      if (resp.status === 201) {
        this.uploadProgress = undefined
        break
      }
    }
    return headers['Drop-Hash']
  }

  @action
  async loadDrops() {
    try {
      this.previewIsLoading = true
      this.inProgress = true
      let args = ''
      if (this.cursor) {
        args = `?cursor=${this.cursor}`
      }
      const resp = await axios.get(`/api/drops${args}`)
      this.cursor = resp.data.next_cursor
      this.drops = this.drops.concat(resp.data.drops)
      this.inProgress = false
      this.dropsToLoadPreview = new Set(this.drops)
      return true
    } catch (e) {
      console.log(e)
      return false
    }
  }

  @action
  dropfilePreviewLoaded(dropfile) {
    this.dropfilesToLoadPreview.delete(dropfile)
    this.previewIsLoading = this.dropfilesToLoadPreview.size !== 0
  }

  @action
  dropPreviewLoaded(drop) {
    this.dropsToLoadPreview.delete(drop)
    this.previewIsLoading = this.dropsToLoadPreview.size !== 0
  }

  @action
  async loadDrop(dropHash) {
    this.previewIsLoading = true
    this.inProgress = true
    this.drop = undefined
    let drop = this.drops.find(function(el) {
      if (el.hash == dropHash) {
        return el
      }
    })
    if (!drop) {
      try {
        const resp = await axios.get(`/api/drops/${dropHash}`)
        this.drop = resp.data
      } catch (e) {
        console.log(e)
        console.log(e.resp)
        this.inProgress = false
        return false
      }
      const index = this.drops.findIndex(element => {
        return element.hash === this.drop.hash
      })
      if (index > -1) {
        this.drops[index] = this.drop
      } else {
        this.drops.unshift(this.drop)
      }
    } else {
      this.drop = drop
    }
    this.dropfilesToLoadPreview = new Set(this.drop.dropfiles)
    this.inProgress = false
  }

  @action
  async deleteDrop() {
    this.previewIsLoading = true
    this.inProgress = true
    try {
      const resp = await axios.delete(`/api/drops/${this.drop.hash}`)
      const index = this.drops.findIndex(element => {
        return element.hash === this.drop.hash
      })
      if (index > -1) {
        this.drops.splice(index, 1)
      }
      this.drop = undefined
    } catch (e) {
      console.log(e)
      console.log(e.resp)
      this.inProgress = false
      return false
    }
    this.inProgress = false
  }

  @action
  async deleteAllDrops(dropHash) {
    this.previewIsLoading = true
    this.inProgress = true
    this.drop = undefined
    this.drops = []
    try {
      const resp = await axios.delete('/api/drops')
    } catch (e) {
      console.log(e)
      console.log(e.resp)
      this.inProgress = false
      return false
    }
    this.inProgress = false
  }
}
