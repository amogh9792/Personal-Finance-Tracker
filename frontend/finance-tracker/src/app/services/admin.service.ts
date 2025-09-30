import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

@Injectable({ providedIn: 'root' })
export class AdminService {
  private base = environment.apiBaseUrl + '/admin';

  constructor(private http: HttpClient) {}

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}/users`);
  }

  makeAdmin(userId: number): Observable<any> {
    return this.http.patch(`${this.base}/make-admin/${userId}`, {});
  }

  removeAdmin(userId: number): Observable<any> {
    return this.http.patch(`${this.base}/remove-admin/${userId}`, {});
  }
}
