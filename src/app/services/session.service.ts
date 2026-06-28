import { Injectable } from '@angular/core';
import { User } from '../models/user';

@Injectable({
  providedIn: 'root'
})
export class SessionService {
    saveUser(user: User) {
        localStorage.setItem('user', JSON.stringify(user));
    }

    getUser(): User | null {
        const userData = localStorage.getItem('user');
        return userData ? JSON.parse(userData) as User : null;
    }

    removeUser() {
        localStorage.removeItem('user');
    }
}
