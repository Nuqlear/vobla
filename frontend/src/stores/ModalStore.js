import { makeObservable, observable, action, computed } from 'mobx'
import { axios } from '../utils/ApiClient'

export default class ModalStore {
  @observable
  visibility = {
    DropUpload: false,
    DropFileUpload: false,
    Error: false,
  }

  @observable
  errorData = {
    name: '',
    text: '',
  }

  constructor() {
    makeObservable(this)
  }

  @action
  setError(name, text) {
    this.errorData.name = name;
    this.errorData.text = text;
    this.visibility["Error"] = true;
  }

  @action
  showModal(modalName) {
    this.visibility[modalName] = true
  }

  @action
  hideModal(modalName) {
    this.visibility[modalName] = false
  }
}
