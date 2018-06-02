import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import Modal from 'react-bootstrap4-modal';
import { Redirect } from 'react-router-dom';


@inject('store', 'routing')
@observer
class UploadModal extends Component {

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
    this.fileinput_target && (this.fileinput_target.value = null);
    this.modalStore.hideModal();
  }

  handleFileChange = (e) => {
    this.fileinput_target = e.target;
    this.setState({file: e.target.files[0]});
  }

  render() {
    const { visible, hideModal } = this.modalStore;
    return (
      <Modal visible={ visible } onClickBackdrop={ this.hide }>
      <div className="modal-header">
        <h5 className="modal-title">Upload a Drop</h5>
      </div>
      <div className="modal-body">
          <input type="file" onChange={ this.handleFileChange }/>
      </div>
      <div className="modal-footer">
        <button type="button" className="btn btn-secondary" onClick={ this.hide }>
          Cancel
        </button>
        {
          this.state && this.state.file ?
          <button type="button" className="btn btn-primary">Upload</button> :
          null
        }
      </div>
    </Modal>
    )
  }
};

export default UploadModal;
