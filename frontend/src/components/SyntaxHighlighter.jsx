import React, { Component } from 'react'
import PrismSyntaxHighlighter from 'react-syntax-highlighter/prism'
import { light } from 'react-syntax-highlighter/styles/prism/base16-ateliersulphurpool.light'
import axios from 'axios'

const detectLanguage = mimetype => {
  if (!mimetype.startsWith('text/x-')) {
    return 'text'
  }
  return mimetype.slice('text/x-'.length)
}

export default class SyntaxHighlighter extends Component {
  constructor(props) {
    super(props)
  }

  async componentWillMount() {
    const ext = this.props.name.split('.').pop()
    this.lang = detectLanguage(this.props.mimetype)
    await axios.get(this.props.url).then(resp => {
      this.setState({ text: resp.data })
      this.props.onLoad()
    })
  }

  render() {
    return (
      <div className="syntax-highlighter">
        {this.props.name}
        {this.state && this.state.text ? (
          <PrismSyntaxHighlighter
            style={light}
            language={this.lang}
            showLineNumbers={true}
          >
            {this.state.text}
          </PrismSyntaxHighlighter>
        ) : null}
      </div>
    )
  }
}
