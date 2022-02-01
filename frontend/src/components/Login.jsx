import React, { Component } from 'react'
import { inject, observer } from 'mobx-react'
import { Redirect, Link } from 'react-router-dom'

import Auth from './Auth'
import GuestOnly from './GuestOnly'
import Loader from './Loader'

@inject('store')
@observer
class Login extends Component {
  constructor(props) {
    super(props)
    this.authStore = this.props.store.authStore
    this.authStore.reset()
  }

  handleEmailChange = e => {
    console.log(this.authStore.values.email);
    this.authStore.setEmail(e.target.value)
  }
  handlePasswordChange = e => this.authStore.setPassword(e.target.value)
  handleInviteCodeChange = e => this.authStore.setInviteCode(e.target.value)
  handleSubmit = async e => {
    e.preventDefault()
    await this.authStore.signin()
  }

  render() {
    const {
      authenticated,
      inProgress,
      errors,
      values,
      message
    } = this.authStore

    const question = (
      <div>
        Don't have an account? <Link to="/signup">Sign Up</Link>
      </div>
    )

    return (
      <Auth message={this.authStore.message} question={question}>
        {this.authStore.authenticated &&
          !this.authStore.inProgress && <Redirect to="/" />}
        <form
          acceptCharset="UTF-8"
          role="form"
          className="form-auth"
          onSubmit={this.handleSubmit}
        >
          <fieldset className={inProgress ? 'op9' : ''}>
            <input
              className="form-control"
              placeholder="Email address"
              autoComplete="on"
              autocompletetype="email"
              name="email"
              type="text"
              value={values.email}
              onChange={this.handleEmailChange}
              disabled={inProgress}
            />
            <input
              className="form-control"
              placeholder="Password"
              name="password"
              type="password"
              value={values.password}
              onChange={this.handlePasswordChange}
              disabled={inProgress}
            />
            <input
              type="submit"
              id="singup"
              value="Login"
              disabled={
                inProgress || message || !(values.email && values.password)
              }
            />
          </fieldset>
          {inProgress ? <Loader /> : null}
        </form>
      </Auth>
    )
  }
}

export default GuestOnly(Login)
