import { store } from 'rfx-core';

import AuthStore from './AuthStore';
import DropStore from './DropStore';

export default store.setup({
	authStore: AuthStore,
  dropStore: DropStore
});
