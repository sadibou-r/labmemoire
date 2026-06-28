import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { SessionService } from '../../services/session.service';
import { NgClass } from '@angular/common';
import { CardInputComponent } from "../../components/card-input/card-input.component";
import { Image } from '../../models/image';
import { ImageService } from '../../services/image.service';
import { FormBuilder, FormGroup, FormArray, ReactiveFormsModule } from '@angular/forms';
import { Annotation } from '../../models/annotation';
import { AnnotationService } from '../../services/annotation.service';
import { AnnotationDTO } from '../../models/annotation-dto';
import { CardComponent } from "../../components/card/card.component";
import { User } from '../../models/user';
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [NgClass, CardInputComponent, ReactiveFormsModule, CardComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  has_error : boolean = false
  annoter : boolean = true
  imagesBatch : Image[] = []
  annotationsList : AnnotationDTO[] = []
  form!: FormGroup;
  current_batch : any = 1
  total_batches : any = 1
  isSubmitting = false;
  // Pagination de l'onglet "Annotations" (correction).
  correctionPageSize = 12;
  correctionPage = 1;
  constructor(
    private router : Router,
    private authService : AuthService,
    private sessionService: SessionService,
    private imageService : ImageService,
    private fb: FormBuilder,
    private annotationService : AnnotationService
  ){}
  logout(){
    this.authService.logout().subscribe(
      {
        next : response => {
        },
        error : err => {
        }
      }
    )
    this.router.navigate(['login'])
  }
    printUser(){
  }
  goAnnotation(){
    this.annoter = false
  }
  goAnnoter(){
    this.annoter = true
  }
  ngOnInit(){
    this.form = this.fb.group({
      items: this.fb.array([])
    });
    if(this.sessionService.getUser()?.id == 4){
      this.imageService.getUndefinedBatch().subscribe({
        next : response => {
          console.log(response)
          this.current_batch = 1
          this.total_batches = 1
          response.images.forEach((image: any)  => {
            this.imagesBatch.push(new Image(image.id,image.path,image.isAnnotated))
            this.itemsArray.push(this.createItem());
          });
        },
        error : err => {
        }
      })
    }
    else{
      this.imageService.getImagesBatch().subscribe({
        next : response => {
          this.current_batch = response.current_batch
          this.total_batches = response.total_batches
          response.images.forEach((image: any)  => {
            this.imagesBatch.push(new Image(image.id,image.path,image.isAnnotated))
            this.itemsArray.push(this.createItem());
          });
        },
        error : err => {
        }
      })
    }

    this.annotationService.getAnnotations().subscribe(
      {
        next:  response  => {
          response.forEach((annotation:any) =>{
            this.annotationsList.push(
              new AnnotationDTO(
                annotation.id,
                new User(
                  annotation.user.id,
                  annotation.user.name,
                  annotation.user.email,
                ''),
              new Image(
                annotation.image.id,
                annotation.image.path,
                true
              ),
              annotation.grade,
              annotation.stade
              )
            )
          }
        )
        this.applyResume();
      }
      }
    )
  }

  get correctionStorageKey(): string {
    return `correctionPage_${this.sessionService.getUser()?.id ?? 'anon'}`;
  }
  // Au chargement : ouvrir l'onglet Annotations sur la page de la dernière image
  // corrigée (mémorisée côté serveur). À défaut, reprendre la dernière page vue (local).
  private applyResume() {
    const fallbackToLocal = () => {
      const saved = Number(localStorage.getItem(this.correctionStorageKey));
      if (saved) {
        this.correctionPage = Math.min(Math.max(1, saved), this.totalCorrectionPages);
      }
    };
    this.annotationService.getResume().subscribe({
      next: (res: any) => {
        const id = res?.annotation_id;
        const idx = id ? this.annotationsList.findIndex(a => a.id === id) : -1;
        if (idx >= 0) {
          this.annoter = false; // basculer sur l'onglet "Annotations"
          this.correctionPage = Math.floor(idx / this.correctionPageSize) + 1;
        } else {
          fallbackToLocal();
        }
      },
      error: () => fallbackToLocal()
    });
  }
  get totalCorrectionPages(): number {
    return Math.max(1, Math.ceil(this.annotationsList.length / this.correctionPageSize));
  }
  get pagedAnnotations(): AnnotationDTO[] {
    const start = (this.correctionPage - 1) * this.correctionPageSize;
    return this.annotationsList.slice(start, start + this.correctionPageSize);
  }
  get correctionRangeStart(): number {
    return this.annotationsList.length === 0 ? 0 : (this.correctionPage - 1) * this.correctionPageSize + 1;
  }
  get correctionRangeEnd(): number {
    return Math.min(this.correctionPage * this.correctionPageSize, this.annotationsList.length);
  }
  setCorrectionPage(p: number) {
    this.correctionPage = Math.min(Math.max(1, p), this.totalCorrectionPages);
    localStorage.setItem(this.correctionStorageKey, String(this.correctionPage));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  nextCorrectionPage() { this.setCorrectionPage(this.correctionPage + 1); }
  prevCorrectionPage() { this.setCorrectionPage(this.correctionPage - 1); }

get itemsArray(): FormArray {
  return this.form.get('items') as FormArray;
}

get itemsControls(): FormGroup[] {
  return this.itemsArray.controls as FormGroup[];
}

  createItem(): FormGroup {
    return this.fb.group({
      grade: [''],
      stade: ['']
    });
  }

  onSubmit() {
    if (this.isSubmitting) {
      return;
    }
    const user = this.sessionService.getUser();
    if (!user) {
      throw new Error("Aucun utilisateur en session !");
    }
    const annotations : Annotation[] = []
    this.imagesBatch.forEach((image,index) => annotations.push(new Annotation(0, image.id, user.id, String(this.form.value.items[index].grade), String(this.form.value.items[index].stade.st))))
    const payload = annotations.map(a => ({
      image_id: a.imageId,
      grade: a.grade,
      stade: a.stade,
    }))
    this.annotationService.batchCreation(payload).subscribe({
      next : response => {
        response.annotations.forEach((annotation:any) =>{
            this.annotationsList.push(
              new AnnotationDTO(
                annotation.id,
                new User(
                  annotation.user.id,
                  annotation.user.name,
                  annotation.user.email,
                ''),
              new Image(
                annotation.image.id,
                annotation.image.path,
                true
              ),
              annotation.grade,
              annotation.stade
              )
            )
          })
          this.annoter = false
          this.imageService.getImagesBatch().subscribe({
            next : response => {
              // Réinitialiser avant de remplir
              this.imagesBatch = [];
              this.itemsArray.clear();
              this.current_batch = response.current_batch
              this.total_batches = response.total_batches
              console.log('rep : ',response)
              response.images.forEach((image: any)  => {
                this.imagesBatch.push(new Image(image.id,image.path,image.isAnnotated))
                this.itemsArray.push(this.createItem());
              });
            },
            error : err => {
            }
          })
        this.has_error = false
      },
      error: err => {
        this.has_error = true
      }
    })
    setTimeout(() => {
      this.isSubmitting = false;
    }, 15000);
  }
}
