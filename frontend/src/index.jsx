import('./styles/main.scss')

import React from 'react'
import { render } from 'react-dom'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'mobx-react'
import { AppContainer } from 'react-hot-loader'

import { isProduction } from './utils/constants'
import Font from './assets/ectoblst-webfont.woff'
import Font2 from './assets/ectoblst-webfont.woff2'
import App from './components/App'
import createStore from './stores/stores'

import { createBrowserHistory } from "history";

const browserHistory = createBrowserHistory()

const renderApp = Component => {

  render(
    <AppContainer>
      <BrowserRouter history={browserHistory}>
        <Provider store={createStore()}>
          <App />
        </Provider>
      </BrowserRouter>
    </AppContainer>,
    document.getElementById('root')
  )
}

renderApp(App)

if (module.hot) {
  module.hot.accept(() => renderApp(App))
}
