import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';
import Modal from 'react-bootstrap4-modal';


@inject('store', 'routing')
@observer
class DropUploadModal extends Component {

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
    this.modalStore.hideModal('DropUpload');
  }

  handleFileChange = (e) => {
    this.fileInputTarget = e.target;
    this.setState({file: e.target.files[0]});
  }

  uploadDrop = async () => {
    const dropHash = await this.dropStore.uploadDrop(this.state.file);
    this.hide();
    this.props.routing.push(`/d/${dropHash}`);
  }

  render() {
    const { visibility, hideModal } = this.modalStore;
    const { uploadProgress } = this.dropStore;
    return (
      <Modal visible={ visibility['DropUpload'] } onClickBackdrop={ this.hide }>
      <div className="modal-header">
        <h5 className="modal-title">Upload a Drop</h5>
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
          <button type="button" className="btn btn-primary" onClick={ this.uploadDrop }>Upload</button> :
          null
        }
      </div>
    </Modal>
    )
  }
};

export default DropUploadModal;
