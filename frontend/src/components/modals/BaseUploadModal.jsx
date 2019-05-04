import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'
import { Redirect } from 'react-router-dom'
import Modal from 'react-bootstrap4-modal'

import ProgressBar from '../ProgressBar'

@inject('store')
@observer
class BaseModal extends Component {
  constructor(props) {
    super(props)
    this.store = this.props.store
  }

  componentWillMount() {
    this.clearFileInput()
  }

  componentWillUnmount() {
    this.hide()
  }

  clearFileInput = () => {
    this.setState({ file: undefined })
  }

  hide = () => {
    this.clearFileInput()
    this.fileInputTarget && (this.fileInputTarget.value = null)
    this.store.modalStore.hideModal(this.props.name)
  }

  handleFileChange = e => {
    this.fileInputTarget = e.target
    this.setState({ file: e.target.files[0] })
    this.props.onFileChange(e)
  }

  render() {
    const { visibility } = this.store.modalStore
    const { uploadProgress } = this.store.dropStore
    return (
      <Modal
        visible={visibility[this.props.name]}
        onClickBackdrop={() => {
          !uploadProgress && this.hide()
        }}
      >
        <div className="modal-header">
          <p className="modal-title">{this.props.title}</p>
        </div>
        <div className="modal-body">
          {uploadProgress ? (
            <ProgressBar value={uploadProgress} />
          ) : (
              <input type="file" onChange={this.handleFileChange} />
            )}
        </div>
        {uploadProgress ? null : (
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => this.hide()}
            >
              Cancel
            </button>
            {this.state && this.state.file ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => this.props.onUploadClick()}
              >
                Upload
              </button>
            ) : null}
          </div>
        )}
      </Modal>
    )
  }
}

export default BaseModal
