import React, { Component } from 'react'
import PropTypes from "prop-types";
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'
import { Redirect, withRouter, useHistory } from 'react-router-dom'

import ProgressBar from '../ProgressBar'
import BaseUploadModal from './BaseUploadModal'

@inject('store')
@withRouter
@observer
class DropUpload extends Component {

  static propTypes = {
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props)

    this.store = this.props.store
  }

  uploadDrop = async () => {
    const dropHash = await this.store.dropStore.uploadDrop(this.fileToUpload)
    this.props.history.push(`/d/${dropHash}`)
  }

  handleFileToUploadChange = e => {
    this.fileToUpload = e.target.files[0]
  }

  render() {
    return (
      <BaseUploadModal
        name="DropUpload"
        title="Upload a Drop"
        onUploadClick={this.uploadDrop}
        onFileChange={this.handleFileToUploadChange}
        {...this.props}
      />
    )
  }
}

export default DropUpload
