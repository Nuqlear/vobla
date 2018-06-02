import { observable, action, computed } from 'mobx';
import axios from 'axios';


export default class DropStore {
  @observable drops = [];
  @observable drop = undefined;
  @observable inProgress = true;
  @observable previewIsLoading = true;
  @observable cursor = undefined;

  @action async loadDrops() {
    try {
      this.previewIsLoading = true;
      this.inProgress = true;
      let args = '';
      if (this.cursor) {
        args = `?cursor=${this.cursor}`
      }
      const resp = await axios.get(
        `/api/drops${args}`
      );
      this.cursor = resp.data.next_cursor;
      this.drops = this.drops.concat(resp.data.drops);
      this.inProgress = false;
      return true;
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      return false;
    }
  }

  @action previewLoaded() {
    this.previewIsLoading = false;
  }

  @action async loadDrop(dropHash) {
    this.previewIsLoading = true;
    this.inProgress = true;
    this.drop = undefined;
    let drop = this.drops.find(function(el) {
      if (el.hash == dropHash) {
        return el;
      }
    })
    if (!drop) {
      try {
        const resp = await axios.get(
          `/api/drops/${dropHash}`
        );
        this.drop = resp.data;
      }
      catch(e) {
        console.log(e);
        console.log(e.resp)
        this.inProgress = false;
        return false;
      }
    }
    else {
      this.drop = drop;
    }
    this.inProgress = false;
  }

  @action async deleteDrop() {
    this.previewIsLoading = true;
    this.inProgress = true;
    try {
      const resp = await axios.delete(
        `/api/drops/${this.drop.hash}`
      );
      const index = this.drops.findIndex((element) => {
        return element.hash === this.drop.hash;
      });
      if (index > -1) {
        this.drops.splice(index, 1);
      }
      this.drop = undefined;
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      this.inProgress = false;
      return false;
    }
    this.inProgress = false;
  }

  @action async deleteAllDrops(dropHash) {
    this.previewIsLoading = true;
    this.inProgress = true;
    this.drop = undefined;
    this.drops = [];
    try {
      const resp = await axios.delete(
        '/api/drops'
      );
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      this.inProgress = false;
      return false;
    }
    this.inProgress = false;
  }
}
