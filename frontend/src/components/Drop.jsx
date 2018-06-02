import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Route, Link, Redirect } from 'react-router-dom';
import Moment from 'react-moment';
import TiTrash from 'react-icons/lib/ti/trash';

import Loader from './Loader';
import Header from './Header';


@inject('store', 'routing')
@observer
class Drop extends Component {
  constructor(props) {
    super(props);
    this.store = this.props.store;
    this.dropStore = this.store.dropStore;
    this.getDropPreview.bind(this);
  }

  async componentWillMount() {
    await this.dropStore.loadDrop(this.props.match.params.dropHash);
  }

  generatePreview(file) {
    let previewDiv;
    if (file.mimetype == 'application/octet-stream') {
      <div className="image-container">
        <img className="img-thumbnail" src="" width="100%" alt=""/>
      </div>
    }
    else if (file.mimetype.split('/')[0] == 'image') {
      previewDiv = (
        <div className="image-container">
          <img className="img-thumbnail" src={ getDropFile(file) } width="100%" alt=""
          onLoad={ this.checkImagesLoaded.bind(this) }
          onError={ this.checkImagesLoaded.bind(this) }
          />
        </div>
      );
    }
    return previewDiv;
  }

  getDropPreview(drop) {
    return drop.dropfiles[0].url;
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

  render() {
    const { inProgress, previewIsLoading, drop, deleteDrop } = this.dropStore;
    const isLoading = inProgress || previewIsLoading;
    const menu = [{
        onClick: this.deleteDrop,
        jsx: (
          <span>
            <TiTrash size={25}/><span className="d-none d-md-inline">&nbsp;&nbsp;Delete this Drop</span>
          </span>
        )
      }
    ];
    return (
      <div>
        <Header navbarLeft={ menu }/>
        <div className='contaner'>
          { isLoading ? <Loader/> : null }
          <div className={ isLoading ? 'hidden' : '' }>
            { !inProgress && drop ? (
              <div className="drop-item">
                <img src={ this.getDropPreview(drop) }
                onLoad={ () => this.checkImagesLoaded() } onError={ () => this.checkImagesLoaded() }/>
              </div>
            ) : null }
          </div>
        </div>
      </div>
    );
  }
}

export default Drop;
