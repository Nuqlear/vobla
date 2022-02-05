import axios from 'axios';


function registerErrorMiddleware(store) {
  axios.interceptors.response.use(function (response) {
    return response;
  }, function (error) {
    if (error.response && error.response.status) {
      if (error.response.status == 400) {
        var message = error.response.data["error"]["message"];
      } else if (error.response.status == 500) {
        var message = "Something blown up";
      }
      store.modalStore.setError('Error', message);
    }
    return Promise.reject(error);
  });
}

export {axios, registerErrorMiddleware};
