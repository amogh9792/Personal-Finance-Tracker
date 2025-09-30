import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment.development';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  // Fetch all categories
  getCategories(): Observable<any> {
    return this.http.get(`${this.base}/categories/`);
  }

  // Fetch all transactions
  getTransactions(): Observable<any> {
    return this.http.get(`${this.base}/transactions/`);
  }
}
