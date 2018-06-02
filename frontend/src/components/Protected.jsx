import React, { Component } from 'react';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';

import Header from './Header'


export default function Protected(Component) {

  @inject('store')
  class AuthenticatedComponent extends Component {

    constructor(props) {
      super(props);
      this.store = this.props.store.authStore;
    }

    render() {
      const { authenticated, inProgress } = this.store;
      const wrapped = authenticated ? [
        <Component {...this.props} key='component'/>
      ] : (
        <Redirect
          to={{
              pathname: '/login',
              state: { from: this.props.location }
            }}
        />
      );
      return (
        <div>
        {
          inProgress ? null : wrapped
        }
        </div>
      );
    }
  }

  return AuthenticatedComponent;
}
