import { observable, action, computed } from 'mobx';
import axios from 'axios';


export default class DropStore {
  @observable drops = [];
  @observable drop = undefined;
  @observable inProgress = true;
  @observable previewIsLoading = true;

  @action async loadDrops() {
    try {
      this.previewIsLoading = true;
      this.inProgress = true;
      const resp = await axios.get(
        '/api/drops'
      );
      this.drops = resp.data.drops;
      this.inProgress = false;
      return true;
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      return false;
    }
  }

  @action previewLoaded() {
    this.previewIsLoading = false;
  }

  @action async loadDrop(dropHash) {
    this.previewIsLoading = true;
    this.inProgress = true;
    this.drop = undefined;
    let drop = this.drops.find(function(el) {
      if (el.hash == dropHash) {
        return el;
      }
    })
    if (!drop) {
      try {
        const resp = await axios.get(
          `/api/drops/${dropHash}`
        );
        this.drop = resp.data;
      }
      catch(e) {
        console.log(e);
        console.log(e.resp)
        this.inProgress = false;
        return false;
      }
    }
    else {
      this.drop = drop;
    }
    this.inProgress = false;
  }

  @action async deleteDrop(dropHash) {
    this.previewIsLoading = true;
    this.inProgress = true;
    this.drop = undefined;
    try {
      const resp = await axios.delete(
        `/api/drops/${dropHash}`
      );
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      this.inProgress = false;
      return false;
    }
    this.inProgress = false;
  }

  @action async deleteAllDrops(dropHash) {
    this.previewIsLoading = true;
    this.inProgress = true;
    this.drop = undefined;
    this.drops = [];
    try {
      const resp = await axios.delete(
        '/api/drops'
      );
    }
    catch(e) {
      console.log(e);
      console.log(e.resp)
      this.inProgress = false;
      return false;
    }
    this.inProgress = false;
  }
}
