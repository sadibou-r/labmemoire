export const appContants = {
  // URLs relatives : même origine que le backend.
  //  - en prod : FastAPI sert le frontend ET l'API sur le même domaine.
  //  - en dev (ng serve) : proxy.conf.json redirige /api et /storage vers localhost:8000.
  main_url: '',
  get baseUrl() {
    return `${this.main_url}/api`;
  },
  get storageUrl() {
    return `${this.main_url}/storage/`;
  }
}

