
export class Annotation {
  id!: number;
  imageId!: number;
  userId!: number;
  grade!: string;
  stade!: string;
  constructor(
    id: number,
  imageId: number,
  userId: number,
  grade: string,
  stade: string
  ){
    this.id = id
    this.grade = grade
    this.stade = stade
    this.imageId = imageId
    this.userId = userId
  }
}
