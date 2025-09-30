import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { TransactionService, Transaction, Summary } from '../../services/transaction.service';
import { AuthService } from '../../services/auth.service';
import { environment } from '../../../environments/environment.development';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  transactions: Transaction[] = [];
  summary: Summary | null = null;
  categories: any[] = [];

  newTxn = { amount: 0, category_id: 0, description: '' };
  newCategory = '';
  isAdmin = false;

  constructor(
    private txnService: TransactionService,
    private http: HttpClient,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadTransactions();
    this.loadSummary();
    this.loadCategories();
    this.isAdmin = this.authService.isAdmin();
  }

  loadTransactions() {
    this.txnService.getTransactions().subscribe({
      next: (data) => this.transactions = data,
      error: (err) => console.error(err)
    });
  }

  loadSummary() {
    this.txnService.getSummary().subscribe({
      next: (data) => this.summary = data,
      error: (err) => console.error(err)
    });
  }

  // 📌 Direct call to backend without service
  loadCategories() {
    this.http.get<any[]>(`${environment.apiBaseUrl}/categories`).subscribe({
      next: (data) => this.categories = data,
      error: (err) => console.error('❌ Failed to load categories', err)
    });
  }

  addCategory() {
    if (!this.newCategory.trim()) return;
    this.http.post<any>(`${environment.apiBaseUrl}/categories`, { name: this.newCategory }).subscribe({
      next: (cat) => {
        this.categories.push(cat);
        this.newCategory = '';
      },
      error: (err) => console.error('❌ Failed to add category', err)
    });
  }

  deleteCategory(id: number) {
    this.http.delete(`${environment.apiBaseUrl}/categories/${id}`).subscribe({
      next: () => this.categories = this.categories.filter(c => c.id !== id),
      error: (err) => console.error('❌ Failed to delete category', err)
    });
  }

  addTransaction() {
    this.txnService.addTransaction(this.newTxn).subscribe({
      next: (txn) => {
        this.transactions.unshift(txn);
        this.loadSummary();
        this.newTxn = { amount: 0, category_id: 0, description: '' };
      },
      error: (err) => console.error(err)
    });
  }

  deleteTransaction(id: number) {
    this.txnService.deleteTransaction(id).subscribe({
      next: () => {
        this.transactions = this.transactions.filter(t => t.id !== id);
        this.loadSummary();
      },
      error: (err) => console.error(err)
    });
  }

  logout() {
    this.authService.logout();
    window.location.href = '/login';
  }
}
