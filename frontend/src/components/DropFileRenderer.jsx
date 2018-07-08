import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'

import SyntaxHighlighter from './SyntaxHighlighter'
import DownloadRenderer from './DownloadRenderer'

@inject('store')
@observer
class DropFileRenderer extends Component {
  constructor(props) {
    super(props)
    this.dropStore = this.props.store.dropStore
  }

  checkImagesLoaded = () => {
    const galleryElement = ReactDOM.findDOMNode(this)
    const imgElements = galleryElement.querySelectorAll('img')
    for (const img of imgElements) {
      if (!img.complete) {
        return false
      }
    }
    this.dropStore.dropfilePreviewLoaded(this.props.dropfile)
  }

  render() {
    if (this.props.dropfile.mimetype.startsWith('image')) {
      return (
        <img
          src={this.props.dropfile.url}
          onLoad={this.checkImagesLoaded.bind(this)}
          onError={this.checkImagesLoaded.bind(this)}
        />
      )
    }
    if (this.props.dropfile.mimetype.startsWith('text')) {
      return (
        <SyntaxHighlighter
          name={this.props.dropfile.name}
          url={this.props.dropfile.url}
          mimetype={this.props.dropfile.mimetype}
          onLoad={() => {
            this.dropStore.dropfilePreviewLoaded(this.props.dropfile)
          }}
        />
      )
    }
    return (
      <DownloadRenderer
        name={this.props.dropfile.name}
        url={this.props.dropfile.url}
        mimetype={this.props.dropfile.mimetype}
        onLoad={() => {
          this.dropStore.dropfilePreviewLoaded(this.props.dropfile)
        }}
      />
    )
  }
}

export default DropFileRenderer
