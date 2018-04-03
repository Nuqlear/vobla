import React, { Component } from 'react';
import { inject, observer } from 'mobx-react';
import { Redirect } from 'react-router-dom';


export default function GuestOnly(Component) {

  @inject('store')
  class NonAuthenticatedComponent extends Component {

    constructor(props) {
      super(props);
      this.store = this.props.store.authStore;
    }

    render() {
      const { authenticated, inProgress } = this.store;
      return (
        <div>
          {
            inProgress ? null :
            (
              !authenticated
              ? <Component {...this.props} />
              : <Redirect
                to={{
                    pathname: '/',
                    state: { from: this.props.location }
                  }}
                />
            )
          }
        </div>
      );
    }
  }

  return NonAuthenticatedComponent;
}
