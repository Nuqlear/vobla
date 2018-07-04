import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';
import Modal from 'react-bootstrap4-modal';

import ProgressBar from '../ProgressBar';
import BaseUploadModal from './BaseUploadModal'


@inject('store')
@observer
class DropFileUploadModal extends Component {

  constructor(props) {
    super(props);
    this.store = this.props.store;
  }

  uploadDropFile = async () => {
    const dropFileHash = await this.store.dropStore.uploadDropFile(
      this.props.dropHash, this.fileToUpload
    );
    await this.store.dropStore.loadDropFile(dropFileHash);
    this.store.modalStore.hideModal("DropFileUpload");
  }

  handleFileToUploadChange = (e) => {
    this.fileToUpload = e.target.files[0];
  }

  render() {
    return (
      <BaseUploadModal
        name='DropFileUpload'
        title='Upload a DropFile'
        onUploadClick={ this.uploadDropFile }
        onFileChange={ this.handleFileToUploadChange }
        {...this.props}
      />
    )
  }
};

export default DropFileUploadModal;
