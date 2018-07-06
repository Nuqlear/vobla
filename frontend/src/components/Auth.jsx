import React, { Component } from 'react'
import { inject, observer } from 'mobx-react'
import { Redirect } from 'react-router-dom'

import Loader from './Loader'

export default props => {
  return (
    <div className="auth-container">
      <div className={'auth-info ' + (props.message ? '' : 'hidden')}>
        {props.message}
      </div>
      <div className="container">
        <div className="row">
          <div className="col-md-9">
            <div className="row">
              <div className="col-md-12 offset-md-2">
                <div className="brand text-center">vobla</div>
                <div className="panel panel-default">
                  <div className="panel-body">{props.children}</div>
                </div>
                <h4
                  className={
                    'auth-question ' + (props.question ? '' : 'hidden')
                  }
                >
                  {props.question}
                </h4>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
