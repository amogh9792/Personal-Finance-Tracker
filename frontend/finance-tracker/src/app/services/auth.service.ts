import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment.development';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private base = environment.apiBaseUrl;
  private tokenKey = 'access_token';

  constructor(private http: HttpClient) {}

  // 🔹 Login
  login(username: string, password: string): Observable<any> {
    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    return this.http.post(`${this.base}/auth/login`, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  }

  // 🔹 Register
  register(username: string, password: string): Observable<any> {
    return this.http.post(`${this.base}/auth/register`, { username, password });
  }

  // 🔹 Save JWT token
  saveToken(token: string) {
    sessionStorage.setItem(this.tokenKey, token);
  }

  // 🔹 Get JWT token
  getToken(): string | null {
    return sessionStorage.getItem(this.tokenKey);
  }

  // 🔹 Logout
  logout() {
    sessionStorage.removeItem(this.tokenKey);
  }

  // 🔹 Is logged in?
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  // 🔹 Decode JWT and check admin role
  isAdmin(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      console.log('🔍 Decoded JWT:', payload);
      return payload.is_admin === true;
    } catch (e) {
      console.error('Failed to decode token', e);
      return false;
    }
  }
}
