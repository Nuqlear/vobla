import AuthStore from './AuthStore'
import DropStore from './DropStore'
import ModalStore from './ModalStore'

// export default class RootStore {
//   constructor() {
//       this.authStore = new AuthStore(this)
//       this.dropStore = new DropStore(this)
//       this.modalStore = new ModalStore(this)
//   }
// }
export default function createStore() {
  return {
      authStore: new AuthStore(this),
      dropStore: new DropStore(this),
      modalStore: new ModalStore(this),
  }
}
