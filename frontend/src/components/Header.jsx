import React, { Component } from 'react';
import { inject, observer } from 'mobx-react';
import { Link, withRouter } from 'react-router-dom';


@inject('store')
@observer
export default class Header extends Component {
  constructor(props) {
    super(props);
    this.store = this.props.store.authStore;
    this.protected = this.props.protected || [];
  }

  componentDidMount() {
    document.addEventListener('click', this._handlePageClick);
    this.hideDropdown();
  }

  componentWillUnmount() {
    document.removeEventListener('click', this._handlePageClick);
  }

  _handlePageClick = (e) => {
    var wasDown = this.mouseDownOnDropdown;
    var wasUp = this.mouseUpOnDropdown;
    this.mouseDownOnDropdown = false;
    this.mouseUpOnDropdown = false;
    if (!wasDown && !wasUp)
      this.hideDropdown();
  }

  handleMouseDownOnDropdown = () => {
    this.mouseDownOnDropdown = true;
  }

  handleMouseUpOnDropDown = () => {
    this.mouseUpOnDropdown = true;
  }

  toggleDropdown = () => {
    this.setState({
      dropdownShown: !this.state.dropdownShown
    });
  }

  hideDropdown = () => {
    this.setState({
      dropdownShown: false
    });
  }

  render() {
    const { authenticated, logOut, user } = this.store;
    const self = this;
    let navbarRight;
    if (authenticated) {
      navbarRight = (
        <ul className='navbar-nav justify-content-end'>
          { this.protected.map(function(el, index) {
            return (
              <li className='nav-item' onClick={ el.onClick } key={ index }>
                { el.jsx }
              </li>
            );
          }) }
          <li className='nav-item' onClick={ this.toggleDropdown }
          onMouseDown={ this.handleMouseDownOnDropDown } onMouseUp={ this.handleMouseUpOnDropDown }>
            { user } &#x25BE;
          </li>
        </ul>
      );
    }
    else {
      navbarRight = (
        <ul className='navbar-nav justify-content-end'>
          <li className='nav-item'>
            <Link to='/login' data-toggle='collapse' data-target='#skeleton-navigation-navbar-collapse.in'
              className='nav-auth-btn'>
              Login
            </Link>
          </li>
        </ul>
      );
    }
    return (
      <div className='root secondary-color-background'>
        <div className='navigation'>
          <nav className='navbar navbar-toggleable-md navbar-light bg-faded'>
            <Link to='/' className='brand navbar-brand' activeclassname='active'>
              vobla
            </Link>
            { navbarRight }
          </nav>
          <ul className={ this.state && this.state.dropdownShown ? 'dropdown-menu active' : 'dropdown-menu'}
          onMouseDown={ this.handleMouseDownOnDropDown } onMouseUp={ this.handleMouseUpOnDropDown }>
            <Link to='/getapp' className='dropdown-item'>Get app</Link>
            <Link to='/logout' className='dropdown-item'>Logout</Link>
          </ul>
        </div>
      </div>
    );
  }
}
