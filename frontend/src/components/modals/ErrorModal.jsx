import React, { Component } from 'react'
import { inject, observer } from 'mobx-react'
import {Modal, Button} from 'react-bootstrap'


@inject('store')
@observer
class ErrorModal extends Component {
  constructor(props) {
    super(props)
    this.store = this.props.store
    this.modalStore = this.store.modalStore
    this.modalName = "Error"
  }

  componentWillMount() {
  }

  componentWillUnmount() {
    this.hide()
  }

  hide = () => {
    this.modalStore.hideModal(this.modalName)
  }

  render() {
    const { visibility, errorData } = this.modalStore
    return (
      <Modal
      show={visibility[this.modalName]}
      backdrop={ true }
      onHide={() => this.hide()}
      >
        <div className="modal-header">
          <p className="modal-title">{ errorData.name }</p>
        </div>
        <div className="modal-body">
          { errorData.text }
        </div>
        <div className="modal-footer">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => this.hide()}
          >
            Close
          </button>
        </div>
      </Modal>
    )
  }
}

export default ErrorModal
