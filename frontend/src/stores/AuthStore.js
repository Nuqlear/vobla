import { makeObservable, observable, action, computed } from 'mobx'
import axios from 'axios'

axios.interceptors.request.use(
  function(config) {
    if (localStorage.token) {
      config.headers.Authorization = `Bearer ${localStorage.token}`
    } else {
      delete config.headers.Authorization
    }
    return config
  },
  function(err) {
    return Promise.reject(err)
  }
)

export default class AuthStore {
  @observable authenticated = false
  @observable inProgress = false
  @observable errors = undefined
  @observable message = undefined

  @observable user = undefined

  constructor() {
    makeObservable(this)
  }

  @observable
  values = {
    email: '',
    password: '',
    password_confirm: '',
    invite_code: ''
  }

  @action
  setEmail(email) {
    this.values.email = email
    this.message = undefined
  }

  @action
  setPassword(password) {
    this.values.password = password
    this.message = undefined
  }

  @action
  setPasswordConfirm(password_confirm) {
    this.values.password_confirm = password_confirm
    this.message = undefined
  }

  @action
  setInviteCode(invite_code) {
    this.values.invite_code = invite_code
    this.message = undefined
  }

  @action
  reset() {
    this.values.password = ''
    this.values.password_confirm = ''
    this.values.invite_code = ''
    this.message = undefined
  }

  @action
  async signup() {
    try {
      if (this.values.password != this.values.password_confirm) {
        this.message = 'Passwords dont match.'
        return false
      }
      this.inProgress = true
      this.message = undefined
      this.errors = undefined
      const resp = await axios.post('/api/users/signup', {
        invite_code: this.values.invite_code,
        email: this.values.email,
        password: this.values.password
      })
      this.signupSuccess(this.values.email, resp.data.token)
      return true
    } catch (e) {
      this.signupError(e.response)
      return false
    }
  }

  @action.bound
  signupSuccess(email, token) {
    this.inProgress = false
    this.signinSuccess(email, token)
    this.reset()
  }

  @action.bound
  signupError(response) {
    if (response) {
      if (response.status == 422) {
        let fields = response.data.error.fields
        for (let key in fields) {
          if (key == 'password') {
            this.values['password_confirm'] = ''
          }
          this.values[key] = ''
        }
        this.message = fields[Object.keys(fields)[0]]
      }
    }
    this.inProgress = false
  }

  @action
  async signin() {
    this.inProgress = true
    this.message = undefined
    this.errors = undefined
    try {
      const resp = await axios.post('/api/users/login', {
        email: this.values.email,
        password: this.values.password
      })
      this.signinSuccess(this.values.email, resp.data.token)
    } catch (e) {
      if (!e.response) {
        throw e
      }
      this.signinError(e.response)
    }
    return this.authenticated
  }

  @action
  async jwtcheck() {
    this.inProgress = true
    if (!localStorage.token) {
      this.signinError()
    }
    try {
      const resp = await axios.get('/api/users/jwtcheck')
      this.signinSuccess(localStorage.email, localStorage.token)
    } catch (e) {
      if (!e.response) {
        throw e
      }
      if (e.response.status == 401) {
        this.signinError()
      }
    }
    return this.authenticated
  }

  @action.bound
  signinSuccess(email, token) {
    this.reset()
    this.values.email = ''
    this.user = email
    localStorage.email = email
    localStorage.token = token
    this.authenticated = true
    this.inProgress = false
  }

  @action.bound
  signinError(response) {
    if (response) {
      if (response.status == 422) {
        let fields = response.data.error.fields
        for (let key in fields) {
          if (key != "email") {
            this.values[key] = ''
          }
        }
        this.message = fields[Object.keys(fields)[0]]
      }
    }
    this.user = undefined
    this.inProgress = false
  }

  @action
  async signOut() {
    this.inProgress = true
    delete localStorage.token
    delete localStorage.email
    this.user = undefined
    this.authenticated = false
    this.inProgress = false
    return this.authenticated
  }
}
