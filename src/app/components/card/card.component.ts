import { Component, Input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { appContants } from '../../constants';
import { AnnotationService } from '../../services/annotation.service';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './card.component.html',
  styleUrl: './card.component.css'
})
export class CardComponent {
  @Input() id: number = 0
  @Input() imageUrl: string = 'images/Pied001.jpg'
  @Input() medecinName: string = 'Ndiaga'
  @Input() grade: string = 'A'
  @Input() stade: string = 'C'
  storageUrl : string = appContants.storageUrl

  editing : boolean = false
  saving : boolean = false
  saveError : boolean = false
  editGrade : string = ''
  editStade : string = ''

  grades : string[] = ['0', '1', '2', '3']
  stades : string[] = ['A', 'B', 'C', 'D']

  constructor(private annotationService : AnnotationService) {}

  startEdit() {
    this.editGrade = String(this.grade)
    this.editStade = String(this.stade)
    this.saveError = false
    this.editing = true
  }

  cancelEdit() {
    this.editing = false
  }

  saveEdit() {
    if (this.saving) { return }
    this.saving = true
    this.saveError = false
    this.annotationService.updateAnnotation(this.id, this.editGrade, this.editStade).subscribe({
      next : (response : any) => {
        this.grade = response.grade
        this.stade = response.stade
        this.editing = false
        this.saving = false
      },
      error : () => {
        this.saveError = true
        this.saving = false
      }
    })
  }
}
