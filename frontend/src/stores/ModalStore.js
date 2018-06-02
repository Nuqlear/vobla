import { observable, action, computed } from 'mobx';
import axios from 'axios';


export default class ModalStore {
  @observable visible = false;

  @action showModal() {
    this.visible = true;
  }

  @action hideModal() {
    this.visible = false;
  }
}
