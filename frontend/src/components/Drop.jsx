import React, { Component } from 'react'
import PropTypes from "prop-types";
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'
import { Route, Link, Redirect, withRouter } from 'react-router-dom'
import Moment from 'react-moment'
import {TiTrash, TiUpload} from 'react-icons/ti'

import Loader from './Loader'
import Header from './Header'
import DropFileUploadModal from './modals/DropFileUpload'
import DropFileRenderer from './DropFileRenderer'

@inject('store')
@withRouter
@observer
class Drop extends Component {
  static propTypes = {
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props)
    this.dropHash = this.props.match.params.dropHash
    this.store = this.props.store
    this.dropStore = this.store.dropStore
    this.modalStore = this.store.modalStore
    this.menu = [
      {
        onClick: () => {
          this.modalStore.showModal('DropFileUpload')
        },
        jsx: (
          <span>
            <TiUpload size={25} />
            <span className="d-none d-md-inline">
              &nbsp;&nbsp;Upload DropFile
            </span>
          </span>
        )
      },
      {
        onClick: this.deleteDrop,
        jsx: (
          <span>
            <TiTrash size={25} />
            <span className="d-none d-md-inline">&nbsp;&nbsp;Delete Drop</span>
          </span>
        )
      }
    ]
  }

  async componentWillMount() {
    await this.dropStore.loadDrop(this.dropHash)
  }

  deleteDrop = async () => {
    await this.dropStore.deleteDrop()
    this.props.history.push('/')
  }

  showModal = () => {
    this.modalStore.showModal('DropFileUpload')
  }

  render() {
    const { inProgress, previewIsLoading, drop, deleteDrop } = this.dropStore
    const isLoading = inProgress || previewIsLoading
    const self = this
    return (
      <div>
        <DropFileUploadModal dropHash={this.dropHash} />
        <Header navbarLeft={this.menu} />
        <div className="contaner">
          {isLoading ? <Loader /> : null}
          <div className={isLoading ? 'hidden' : ''}>
            <div className="drop-item">
              {!inProgress && drop
                ? drop.dropfiles.map(function(dropfile, index) {
                    return <DropFileRenderer dropfile={dropfile} key={index} />
                  })
                : null}
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default Drop
