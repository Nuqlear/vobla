import React, { Component } from 'react'
import PropTypes from "prop-types";
import loadable from "@loadable/component";
import {
  Route,
  Link,
  Redirect,
  DefaultRoute,
  Switch,
  withRouter
} from 'react-router-dom'
import { inject, observer } from 'mobx-react'

import Logout from './Logout'
import Loader from './Loader'
import ErrorModal from './modals/ErrorModal';

const WrappedLoader = () => {
  return (
    <div className="primary-color-background">
      <Loader alternative />
    </div>
  )
}

@inject('store')
@withRouter
@observer
export default class App extends Component {
  static propTypes = {
    location: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props)
    this.store = this.props.store
  }

  async componentWillMount() {
    await this.store.authStore.jwtcheck()
  }

  render() {
    const Signup = loadable(
      () => import('./Signup'), {
        fallback: <WrappedLoader />
    })
    const Login = loadable(
      () => import('./Login'), {
        fallback: <WrappedLoader />
    })
    const Dashboard = loadable(
      () => import('./Dashboard'), {
        fallback: <WrappedLoader />
    })
    const Drop = loadable(
      () => import('./Drop'), {
        fallback: <WrappedLoader />
    })
    const GetApp = loadable(
      () => import('./GetApp'), {
        fallback: <WrappedLoader />
    })
    return (
      <div location={this.props.location}>
        <Switch>
          <Route exact path="/signup" component={Signup} />
          <Route exact path="/login" component={Login} />
          <Route exact path="/logout" component={Logout} />
          <Route exact path="/" component={Dashboard} />
          <Route exact path="/getapp" component={GetApp} />
          <Route exact path="/d/:dropHash" component={Drop} />
          <Redirect to="/" />
        </Switch>
      </div>
    )
  }
}
