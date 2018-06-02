import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';
import Modal from 'react-bootstrap4-modal';


@inject('store', 'routing')
@observer
class DropFileUploadModal extends Component {

  constructor(props) {
    super(props);
    this.store = this.props.store;
    this.dropStore = this.store.dropStore;
    this.modalStore = this.store.modalStore;
  }

  componentWillMount() {
    this.clearFileInput();
  }

  clearFileInput = () => {
    this.setState({file: undefined});
  }

  hide = () => {
    this.clearFileInput();
    this.fileInputTarget && (this.fileInputTarget.value = null);
    this.modalStore.hideModal('DropFileUpload');
  }

  handleFileChange = (e) => {
    this.fileInputTarget = e.target;
    this.setState({file: e.target.files[0]});
  }

  uploadDropFile = async () => {
    const dropFileHash = await this.dropStore.uploadDropFile(
      this.props.dropHash, this.state.file
    );
    await this.dropStore.loadDropFile(dropFileHash);
    this.hide();
  }

  render() {
    const { visibility, hideModal } = this.modalStore;
    const { uploadProgress } = this.dropStore;
    return (
      <Modal visible={ visibility['DropFileUpload'] } onClickBackdrop={ this.hide }>
      <div className="modal-header">
        <h5 className="modal-title">Upload a DropFile</h5>
      </div>
      <div className="modal-body">
          <input type="file" onChange={ this.handleFileChange } accept="image/*"/>
          { uploadProgress }
      </div>
      <div className="modal-footer">
        <button type="button" className="btn btn-secondary" onClick={ this.hide }>
          Cancel
        </button>
        {
          this.state && this.state.file ?
          <button type="button" className="btn btn-primary" onClick={ this.uploadDropFile }>Upload</button> :
          null
        }
      </div>
    </Modal>
    )
  }
};

export default DropFileUploadModal;
