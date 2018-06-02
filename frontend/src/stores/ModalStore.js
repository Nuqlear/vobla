import { observable, action, computed } from 'mobx';
import axios from 'axios';


export default class ModalStore {
  @observable visibility = {
    'DropUpload': false,
    'DropFileUpload': false
  };

  @action showModal(modalName) {
    this.visibility[modalName] = true;
  }

  @action hideModal(modalName) {
    this.visibility[modalName] = false;
  }
}
