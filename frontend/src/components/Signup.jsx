import React, { Component } from 'react'
import { inject, observer } from 'mobx-react'
import { reaction } from 'mobx'
import { Redirect, Link } from 'react-router-dom'

import Auth from './Auth'
import GuestOnly from './GuestOnly'
import Loader from './Loader'

@inject('store')
@observer
class Signup extends Component {
  constructor(props) {
    super(props)
    this.authStore = this.props.store.authStore
    this.authStore.reset()
  }

  handleEmailChange = e => this.authStore.setEmail(e.target.value)
  handlePasswordChange = e => this.authStore.setPassword(e.target.value)
  handlePasswordConfirmChange = e =>
    this.authStore.setPasswordConfirm(e.target.value)
  handleInviteCodeChange = e => this.authStore.setInviteCode(e.target.value)
  handleSubmit = async e => {
    e.preventDefault()
    await this.authStore.signup()
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
        Already have an acoount? <Link to="/login">Log In</Link>
      </div>
    )

    return (
      <Auth message={message} isProgress={inProgress} question={question}>
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
              placeholder="Invite code"
              name="invite"
              type="text"
              value={values.invite_code}
              onChange={this.handleInviteCodeChange}
              disabled={inProgress}
            />
            <input
              className="form-control"
              placeholder="Email address"
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
              className="form-control"
              placeholder="Confirm password"
              name="password_confirm"
              type="password"
              value={values.password_confirm}
              onChange={this.handlePasswordConfirmChange}
              disabled={inProgress}
            />
            <input
              type="submit"
              id="singup"
              value="Signup"
              disabled={
                inProgress ||
                message ||
                !(
                  values.invite_code &&
                  values.email &&
                  values.password &&
                  values.password_confirm
                )
              }
            />
            {inProgress ? <Loader /> : null}
          </fieldset>
        </form>
      </Auth>
    )
  }
}

export default GuestOnly(Signup)
