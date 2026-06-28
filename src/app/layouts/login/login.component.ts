import { NgIf } from '@angular/common';
import { Component } from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms'
import { SessionService } from '../../services/session.service';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { User } from '../../models/user';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  formulaire! : FormGroup
  badLogin : boolean = false
  constructor(private fb : FormBuilder,private sessionService : SessionService,private router : Router,private authService : AuthService) {
      this.formulaire = fb.group({
          username : [
              '',
              [
                  Validators.required,
              ]
          ],
          password : [
              '',
              [
                  Validators.required,
                  Validators.minLength(8)
              ]
          ]
      })
  }
  loginUser(){
      const informations = {
          email : this.formulaire.get('username')?.value,
          password: this.formulaire.get('password')?.value
      }
      this.authService.loginUser(informations).subscribe(
        {
          next: response =>{
                let user = new User(response.user.id,response.user.name,response.user.email,response.token);
                this.sessionService.saveUser(user);
                this.router.navigate(['home'])
                this.badLogin = false

          },
          error : err => {
            this.badLogin = true
          }

        }
      )
  }

}
