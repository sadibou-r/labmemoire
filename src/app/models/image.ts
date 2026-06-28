export class Image {
  id!: number;
  path!: string;
  isAnnotated!: boolean;
  constructor(id: number,path: string,isAnnotated: boolean){
    this.id = id
    this.path = path
    this.isAnnotated = isAnnotated
  }
}
