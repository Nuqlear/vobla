import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'
import { Route, Link, Redirect } from 'react-router-dom'
import Moment from 'react-moment'
import { TiUpload, TiArrowForward } from 'react-icons/ti'
import drop_icon from '../assets/drop.png'

import Protected from './Protected'
import Header from './Header'
import Loader from './Loader'
import DropUploadModal from './modals/DropUpload'
import ErrorModal from './modals/ErrorModal';

@inject('store')
@observer
class Dashboard extends Component {

  constructor(props) {
    super(props)
    this.store = this.props.store
    this.dropStore = this.store.dropStore
    this.modalStore = this.store.modalStore
    this.getDropPreview.bind(this)
  }

  componentDidMount() {
    window.addEventListener('scroll', this.onScroll, false)
  }

  async componentWillMount() {
    if (this.dropStore.drops.length == 0) {
      await this.dropStore.loadDrops()
    }
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.onScroll, false)
  }

  onScroll = () => {
    if (
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 &&
      !this.dropStore.inProgress &&
      this.dropStore.cursor != -1
    ) {
      this.dropStore.loadDrops()
    }
  }

  getDropPreview(drop) {
    return drop.preview_url || drop_icon
  }

  deleteAllDrops = async () => {
    await this.dropStore.deleteAllDrops()
  }

  render() {
    const { inProgress, drops } = this.dropStore
    const isLoading = inProgress || (this.previewIsLoading && drops.length != 0)
    const self = this
    const navbarRight = [
      {
        onClick: this.deleteAllDrops,
        jsx: 'Delete all Drops'
      }
    ]
    const navbarLeft = [
      {
        onClick: () => {
          this.modalStore.showModal('DropUpload')
        },
        jsx: (
          <span>
            <TiUpload size={25} />
            <span className="d-none d-md-inline">&nbsp;&nbsp;Upload Drop</span>
          </span>
        )
      }
    ]
    return (
      <div>
        <ErrorModal />
        <DropUploadModal />
        <Header
          navbarLeft={navbarLeft}
          navbarRight={navbarRight}
          key="header"
        />
        <div className="contaner">
          {isLoading ? <Loader /> : null}
          <div
            className={
              !isLoading && drops.length == 0
                ? 'dashboard-gallery-empty'
                : 'dashboard-gallery-items'
            }
          >
            {drops.map(function (drop) {
              return (
                <Link to={`/d/${drop.hash}`} key={drop.hash} className="item">
                  <div className="img-container">
                    <img
                      className="img-thumbnail"
                      src={self.getDropPreview(drop)}
                      width="100%"
                      alt=""
                      onLoad={() => self.dropStore.dropPreviewLoaded(drop)}
                      onError={() => self.dropStore.dropPreviewLoaded(drop)}
                    />
                  </div>
                  <div className="title">
                    {drop.name}
                    <p className="text-muted">
                      <Moment format="DD/MM/YYYY">{drop.created_at}</Moment>
                      <br />
                      {drop.dropfiles.length} file{drop.dropfiles.length === 1
                        ? ''
                        : 's'}
                    </p>
                  </div>
                </Link>
              )
            })}
            {!isLoading && drops.length == 0 ? (
              <div>
                <b>Ooops!</b>
                <br />
                <span>Seems like you did not upload any Drops :(</span>
                <br />
                <span>Would you like to download an App?</span>
                <Link to="/getapp">
                  <TiArrowForward />
                </Link>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    )
  }
}

export default Protected(Dashboard)
