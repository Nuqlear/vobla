import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { inject, observer } from 'mobx-react';
import { Route, Link, Redirect } from 'react-router-dom';
import Moment from 'react-moment';

import Protected from './Protected';
import Header from './Header';
import Loader from './Loader';


@inject('store')
@observer
class Dashboard extends Component {
  constructor(props) {
    super(props);
    this.store = this.props.store;
    this.dropStore = this.store.dropStore;
    this.getDropPreview.bind(this);
  }

  componentDidMount() {
    window.addEventListener('scroll', this.onScroll, false);
  }

  async componentWillMount() {
    if (this.dropStore.drops.length == 0) {
      await this.dropStore.loadDrops();
    }
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.onScroll, false);
  }

  onScroll = () => {
    if (
      (window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 500) &&
      !this.dropStore.inProgress && this.dropStore.cursor != -1
    ) {
      this.dropStore.loadDrops();
    }
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

  deleteAllDrops = async () => {
    await this.dropStore.deleteAllDrops();
  }

  render() {
    const { inProgress, previewIsLoading, drops } = this.dropStore;
    const isLoading = inProgress || (previewIsLoading && drops.length != 0);
    const self = this;
    const menu = [{
        onClick: this.deleteAllDrops,
        jsx: 'Delete all'
      }
    ];
    return (
      <div>
        <Header navbarRight={ menu } key='header'/>
        <div className='contaner'>
          { isLoading ? <Loader/> : null }
          <div className={
            isLoading ? 'dashboard-gallery-items hidden' : 'dashboard-gallery-items'
          }>
            { drops.map(function(drop) {
              return (
                <Link to={ `/d/${drop.hash}` } key={ drop.hash } className='item'>
                  <div className="image-container">
                    <img className="img-thumbnail"
                      src={ self.getDropPreview(drop) } width="100%" alt=""
                      onLoad={ () => self.checkImagesLoaded() }
                      onError={ () => self.checkImagesLoaded() }
                    />
                  </div>
                  <div className='title'>
                    { drop.name }
                    <p className='text-muted'>
                      <Moment format='DD/MM/YYYY'>{ drop.created_at }</Moment>
                      <br/>
                      { drop.dropfiles.length } file{ drop.dropfiles.length === 1 ? '' : 's' }
                    </p>
                  </div>
                </Link>
              );
            }) }
          </div>
        </div>
      </div>
    );
  }
}

export default Protected(Dashboard);
