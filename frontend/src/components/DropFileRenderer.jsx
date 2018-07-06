import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { inject, observer } from 'mobx-react'

import SyntaxHighlighter from './SyntaxHighlighter'

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
    return this.props.dropfile.mimetype.startsWith('text') ? (
      <SyntaxHighlighter
        name={this.props.dropfile.name}
        url={this.props.dropfile.url}
        mimetype={this.props.dropfile.mimetype}
        onLoad={() => {
          this.dropStore.dropfilePreviewLoaded(this.props.dropfile)
        }}
      />
    ) : (
      <img
        src={this.props.dropfile.url}
        onLoad={this.checkImagesLoaded.bind(this)}
        onError={this.checkImagesLoaded.bind(this)}
      />
    )
  }
}

export default DropFileRenderer
