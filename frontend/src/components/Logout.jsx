import React, { Component } from 'react';
import { inject, observer } from 'mobx-react';
import { Redirect, Link } from 'react-router-dom';


@inject('store', 'routing')
@observer
class Logout extends Component {

  componentWillMount () {
    this.props.store.authStore.signOut();
    console.log(this.props.routing.history);
    // not quite sure why 3, but whatever, it just works
    if (this.props.routing.history.length > 3) {
      this.props.routing.history.goBack();
    }
    else {
      this.props.routing.history.push('/');
    }
  }

  render() {
    return null;
  }
}

export default Logout;
