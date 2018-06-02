import { store } from 'rfx-core';

import AuthStore from './AuthStore';
import DropStore from './DropStore';
import ModalStore from './ModalStore';


export default store.setup({
	authStore: AuthStore,
  dropStore: DropStore,
  modalStore: ModalStore
});
