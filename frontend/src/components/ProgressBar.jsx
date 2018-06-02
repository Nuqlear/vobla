import React, { Component } from 'react';


export default props => {
  return (
    <div className="progress">
      <div className="progress-bar" style={ {width: props.value + "%"} }></div>
      <span className="progress-value">{ Math.round(props.value) }%</span>
    </div>
  );
};
