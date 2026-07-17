import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { SessionService } from './session.service';
import { Observable } from 'rxjs';
import { appContants } from '../constants';

@Injectable({
  providedIn: 'root'
})
export class ImageService {

  constructor(private httpClient: HttpClient, private sessionService: SessionService) { }

  getImagesBatch() : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.get(`${appContants.baseUrl}/images/next-batch`, { headers })
  }
  getUndefinedBatch() : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.get(`${appContants.baseUrl}/images/undefined-batch`, { headers })
  }
  // Écarte une image inexploitable (doublon, pas un pied diabétique...).
  rejectImage(imageId : number) : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.post(`${appContants.baseUrl}/images/${imageId}/reject`, {}, { headers })
  }
}
