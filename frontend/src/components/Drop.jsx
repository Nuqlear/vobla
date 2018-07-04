import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Route, Link, Redirect } from 'react-router-dom';
import Moment from 'react-moment';
import TiTrash from 'react-icons/lib/ti/trash';
import TiUpload from 'react-icons/lib/ti/upload';

import Loader from './Loader';
import Header from './Header';
import DropFileUploadModal from './modals/DropFileUpload';


@inject('store', 'routing')
@observer
class Drop extends Component {
  constructor(props) {
    super(props);
    this.dropHash = this.props.match.params.dropHash;
    this.store = this.props.store;
    this.dropStore = this.store.dropStore;
    this.modalStore = this.store.modalStore;
  }

  async componentWillMount() {
    await this.dropStore.loadDrop(this.dropHash);
  }

  checkImagesLoaded = () => {
     const galleryElement = ReactDOM.findDOMNode(this);
     const imgElements = galleryElement.querySelectorAll('img');
     for (const img of imgElements) {
       if (!img.complete) {
         return false;
       }
     }
     this.dropStore.previewLoaded();
   }

  deleteDrop = async () => {
    await this.dropStore.deleteDrop();
    this.props.routing.push('/');
   }

  showModal = () => {
   this.modalStore.showModal('DropFileUpload');
  }

  render() {
    const { inProgress, previewIsLoading, drop, deleteDrop } = this.dropStore;
    const isLoading = inProgress || previewIsLoading;
    const menu = [{
        onClick: () => { this.modalStore.showModal('DropFileUpload') },
        jsx: (
          <span>
            <TiUpload size={25}/><span className="d-none d-md-inline">&nbsp;&nbsp;Upload DropFile</span>
          </span>
        )
      }, {
        onClick: this.deleteDrop,
        jsx: (
          <span>
            <TiTrash size={25}/><span className="d-none d-md-inline">&nbsp;&nbsp;Delete Drop</span>
          </span>
        )
    }];
    const self = this;
    return (
      <div>
        <DropFileUploadModal dropHash={ this.dropHash }/>
        <Header navbarLeft={ menu }/>
        <div className='contaner'>
          { isLoading ? <Loader/> : null }

          <div className={ isLoading ? 'hidden' : '' }>
            <div className="drop-item">
            { !inProgress && drop ? drop.dropfiles.map(function(dropfile, index) {
                return (
                    <img src={ dropfile.url } key={ dropfile.hash }
                      onLoad={ self.checkImagesLoaded.bind(self) }
                      onError={ self.checkImagesLoaded.bind(self) }
                    />
                )
              }
            ) : null }
            </div>
          </div>

        </div>
      </div>
    );
  }
}

export default Drop;
