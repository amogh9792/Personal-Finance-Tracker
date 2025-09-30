import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment.development';

// Interfaces
export interface Transaction {
  id: number;
  date: string;
  amount: number;
  category_id?: number;
  category_name?: string;
  description?: string;
  owner_id: number;
}

export interface Summary {
  total_income: number;
  total_expense: number;
  net_savings: number;
}

@Injectable({
  providedIn: 'root'
})
export class TransactionService {
  private apiUrl = `${environment.apiBaseUrl}`;

  constructor(private http: HttpClient) {}

  // ✅ Transactions
  getTransactions(): Observable<Transaction[]> {
    return this.http.get<Transaction[]>(`${this.apiUrl}/transactions/`);
  }

  addTransaction(txn: Partial<Transaction>): Observable<Transaction> {
    return this.http.post<Transaction>(`${this.apiUrl}/transactions/`, txn);
  }

  deleteTransaction(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/transactions/${id}`);
  }

  exportTransactions(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/transactions/export`, { responseType: 'blob' });
  }

  getSummary(): Observable<Summary> {
    return this.http.get<Summary>(`${this.apiUrl}/transactions/summary`);
  }

  // ✅ Categories
  getCategories(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/categories/`);
  }

  addCategory(category: { name: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/categories/`, category);
  }

  deleteCategory(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/categories/${id}`);
  }
}
