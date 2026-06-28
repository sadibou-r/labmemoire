import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { User } from '../models/user';
import { appContants } from '../constants';
import { SessionService } from './session.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private httpClient: HttpClient,private sessionService: SessionService) {}
  loginUser(authInformations : any) : Observable<any>{
      const headers = new HttpHeaders({
      'ngrok-skip-browser-warning': 'true'
    });
    return this.httpClient.post(`${appContants.baseUrl}/login`,authInformations,{ headers });
  }
  logout() : Observable<any>{
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.sessionService.getUser()?.token}`,
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': 'true'
    });
    localStorage.removeItem('user')
    return this.httpClient.post(`${appContants.baseUrl}/logout`, {}, { headers });
  }
}
