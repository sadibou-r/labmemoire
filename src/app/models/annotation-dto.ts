import { Image } from "./image";
import { User } from "./user";

export class AnnotationDTO {
  id! : number;
  user! : User;
  image!: Image;
  grade!: string;
  stade!: string;
  constructor(id: number,user: User,image : Image,grade : string,stade : string){
    this.id = id
    this.user = user
    this.image = image
    this.grade = grade
    this.stade = stade
  }
}
