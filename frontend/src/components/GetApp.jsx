import React from 'react';
import { Link, withRouter } from 'react-router-dom';

import FaWindows from 'react-icons/lib/fa/windows';
import FaLinux from 'react-icons/lib/fa/linux';
import FaApple from 'react-icons/lib/fa/apple';


const GetApp = () => {
  return (
    <div className='get-app'>
      <div className='container'>
        <div className='row'>
          <div className='col-md-9'>
            <div className='row'>
              <div className='col-md-12 offset-md-2'>
                <div className='brand text-center'>
                  <Link to='/'>
                    vobla
                  </Link>
                </div>
                <div className='body text-center'>
                  <h5> Select an Operating System install package to get started. </h5>
                  <div className='list-group'>
                    <a className='btn btn-default list-group-item' href='/release/win/Setup.exe'>
                      <FaWindows size={ 28 } color='cornflowerblue'/>
                      <span className='text'>Windows installer</span>
                    </a>
                    <a className='btn btn-default list-group-item disabled' href=''>
                      <FaApple size={ 28 } color='cornflowerblue'/>
                      <span className='text'>macOS installer</span>
                    </a>
                    <a className='btn btn-default list-group-item disabled' href=''>
                      <FaLinux size={ 28 } color='cornflowerblue'/>
                      <span className='text'>Linux / Ubuntu installer</span>
                    </a>
                  </div>
                  <h5> Currently <u>Vobla</u> is availiable only for Windows. </h5>
                  <h5> Support for another systems is coming later. </h5>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GetApp;
