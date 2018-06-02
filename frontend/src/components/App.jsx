import React, { Component } from 'react';
import Loadable from 'react-loadable';
import {
  Route, Link, Redirect, DefaultRoute, Switch, withRouter
} from 'react-router-dom';
import { inject, observer } from 'mobx-react';

import Logout from './Logout'
import Loader from './Loader'


const WrappedLoader = () => {
  return (
    <div className='primary-color-background'>
      <Loader alternative/>
    </div>
  );
}


@inject('store', 'routing')
@withRouter
@observer
export default class App extends Component {

  constructor(props) {
    super(props);
    this.store = this.props.store;
  }

  async componentWillMount() {
    await this.store.authStore.jwtcheck();
  }

  render() {
    const Signup = Loadable({
      loader: () => import('./Signup'),
      loading: () => {
        return <WrappedLoader/>;
      }
    })
    const Login = Loadable({
      loader: () => import('./Login'),
      loading: () => {
        return <WrappedLoader/>;
      }
    })
    const Dashboard = Loadable({
      loader: () => import('./Dashboard'),
      loading: () => {
        return <WrappedLoader/>;
      }
    })
    const Drop = Loadable({
      loader: () => import('./Drop'),
      loading: () => {
        return <WrappedLoader/>;
      }
    })
    const GetApp = Loadable({
      loader: () => import('./GetApp'),
      loading: () => {
        return <WrappedLoader/>;
      }
    })
    return (
      <div location={this.props.routing.location}>
        <Switch>
          <Route exact path='/signup' component={ Signup } />
          <Route exact path='/login' component={ Login } />
          <Route exact path='/logout' component={ Logout } />
          <Route exact path='/' component={ Dashboard } />
          <Route exact path='/getapp' component={ GetApp } />
          <Route exact path='/d/:dropHash' component={ Drop } />
          <Redirect to ='/' />
        </Switch>
      </div>
    );
  }
}
