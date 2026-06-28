export class User {
  id!: number;
  name!: string;
  email!: string;
  token!: string;
  constructor(id: number,name:string,email: string,token : string){
    this.id = id
    this.name = name
    this.email = email
    this.token = token
  }
}
