import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { appContants } from '../../constants';
@Component({
  selector: 'app-card-input',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './card-input.component.html',
  styleUrl: './card-input.component.css'
})
export class CardInputComponent {
  @Input() imageId : number = 0
  @Input() imageUrl : string = ''
  @Input() group!: FormGroup;
  // Le parent gère le retrait : lui seul peut garder imagesBatch et le FormArray alignés.
  @Output() remove = new EventEmitter<number>()
  storageUrl : string = appContants.storageUrl

  askRemove(){
    if (confirm("Écarter cette image ? Elle ne sera plus proposée à l'annotation.")) {
      this.remove.emit(this.imageId)
    }
  }
  grades_array : any = [
    {
      gr : 0,
      sig : 'Peau intact ou cicatrice'
    },
    {
      gr : 1,
      sig : 'Ulcère superficiel'
    },
    {
      gr : 2,
      sig : 'Atteinte tendon ou capsule'
    },
    {
      gr : 3,
      sig : 'Atteinte os ou articulation'
    }
  ]
  stades_array : any = [
    {
      st : 'A',
      sig : 'Sans infection ni ischémie'
    },
    {
      st : 'B',
      sig : 'Infection'
    },
    {
      'st' : 'C',
      sig : 'Ischémie'
    },
    {
      st : 'D',
      sig : 'Infection + Ischémie'
    }
  ]

}
