import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';
import Modal from 'react-bootstrap4-modal';

import ProgressBar from '../ProgressBar';
import BaseUploadModal from './BaseUploadModal'


@inject('store', 'routing')
@observer
class DropUpload extends Component {

  constructor(props) {
    super(props);
    this.store = this.props.store;
  }

  uploadDrop = async () => {
    const dropHash = await this.store.dropStore.uploadDrop(this.fileToUpload);
    this.props.routing.push(`/d/${dropHash}`);
  }

  handleFileToUploadChange = (e) => {
    this.fileToUpload = e.target.files[0];
  }

  render() {
    return (
      <BaseUploadModal
        name='DropUpload'
        title='Upload a Drop'
        onUploadClick={ this.uploadDrop }
        onFileChange={ this.handleFileToUploadChange }
        {...this.props}
      />
    )
  }
};

export default DropUpload;
