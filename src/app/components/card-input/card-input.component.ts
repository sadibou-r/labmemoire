import { Component, Input } from '@angular/core';
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
  storageUrl : string = appContants.storageUrl
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
