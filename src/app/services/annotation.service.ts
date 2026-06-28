import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Annotation } from '../models/annotation';
import { Observable } from 'rxjs';
import { SessionService } from './session.service';
import { appContants } from '../constants';

@Injectable({
  providedIn: 'root'
})
export class AnnotationService {

  constructor(private httpClient : HttpClient, private sessionService: SessionService) { }
  batchCreation(annotations : any) : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    console.log(annotations)
    return this.httpClient.post(
      `${appContants.baseUrl}/batch-annotations`,
      {
        annotations : annotations
      },
      { headers });
  }
  getAnnotations() : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.get(
      `${appContants.baseUrl}/annotations/annotated-by-me`,
      { headers }
    );
  }
  getResume() : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.get(`${appContants.baseUrl}/me/resume`, { headers });
  }
  updateAnnotation(id : number, grade : string, stade : string) : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.put(
      `${appContants.baseUrl}/annotations/${id}`,
      { grade : grade, stade : stade },
      { headers }
    );
  }
}
