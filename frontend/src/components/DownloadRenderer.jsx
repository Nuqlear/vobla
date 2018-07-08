import React, { Component } from 'react'
import axios from 'axios'

export default class DownloadRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    return (
      <div className="text-center download-renderer">
        <img
          className="img-thumbnail"
          src={`/api/mimetypes/${this.props.mimetype}`}
          onLoad={this.props.onLoad}
          onError={this.props.onLoad}
        />
        {this.props.name}
        <a href={this.props.url}>
          <div className="btn btn-default">Download</div>
        </a>
      </div>
    )
  }
}
