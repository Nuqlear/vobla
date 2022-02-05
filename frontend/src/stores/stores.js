import AuthStore from './AuthStore'
import DropStore from './DropStore'
import ModalStore from './ModalStore'
import { registerErrorMiddleware } from '../utils/ApiClient';

// export default class RootStore {
//   constructor() {
//       this.authStore = new AuthStore(this)
//       this.dropStore = new DropStore(this)
//       this.modalStore = new ModalStore(this)
//   }
// }
export default function createStore() {
  var store = {
      authStore: new AuthStore(this),
      dropStore: new DropStore(this),
      modalStore: new ModalStore(this),
  }
  registerErrorMiddleware(store);
  return store;
}
