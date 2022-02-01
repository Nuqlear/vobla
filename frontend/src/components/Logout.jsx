import React, { Component } from 'react'
import PropTypes from "prop-types";
import { inject, observer } from 'mobx-react'
import { Redirect, Link, withRouter } from 'react-router-dom'

@inject('store')
@withRouter
@observer
class Logout extends Component {
  static propTypes = {
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  };

  componentWillMount() {
    this.props.store.authStore.signOut()
    console.log(this.props.history)
    // not quite sure why 3, but whatever, it just works
    if (this.props.history.length > 3) {
      this.props.history.goBack()
    } else {
      this.props.history.push('/')
    }
  }

  render() {
    return null
  }
}

export default Logout
