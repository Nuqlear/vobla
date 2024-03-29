import React from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

import { FaWindows, FaLinux, FaApple} from 'react-icons/fa'

const getSharex = () => {
  axios({
    url: '/api/sharex',
    method: 'get',
    responseType: 'blob'
  }).then(response => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'vobla.sxcu')
    document.body.appendChild(link)
    link.click()
  })
}

const GetApp = () => {
  return (
    <div className="get-app">
      <div className="container">
        <div className="row">
          <div className="col-md-9">
            <div className="row">
              <div className="col-md-12 offset-md-2">
                <div className="brand text-center">
                  <Link to="/">vobla</Link>
                </div>
                <div className="body text-center">
                  <p>
                    {' '}
                    Select a preferrable installation method to get started.{' '}
                  </p>
                  <div className="list-group">
                    <a
                      className="btn btn-default list-group-item"
                      onClick={getSharex}
                    >
                      <FaWindows size={28} color="cornflowerblue" />
                      <span className="text">ShareX Vobla Uploader</span>
                    </a>
                    <a
                      className="btn btn-default list-group-item"
                      href="/release/win/Setup.exe"
                    >
                      <FaWindows size={28} color="cornflowerblue" />
                      <span className="text">
                        Vobla App Installer
                      </span>
                    </a>
                    <a
                      className="btn btn-default list-group-item disabled"
                      href=""
                    >
                      <FaApple size={28} color="cornflowerblue" />
                      <span className="text">Not Availiable ATM</span>
                    </a>
                    <a
                      className="btn btn-default list-group-item disabled"
                      href=""
                    >
                      <FaLinux size={28} color="cornflowerblue" />
                      <span className="text">Not Availiable ATM</span>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GetApp
