import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment.development';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss']
})
export class AdminComponent implements OnInit {
  users: any[] = [];

  constructor(private http: HttpClient, private authService: AuthService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers() {
    this.http.get<any[]>(`${environment.apiBaseUrl}/admin/users`).subscribe({
      next: (data) => this.users = data,
      error: (err) => console.error('❌ Failed to load users', err)
    });
  }

  makeAdmin(userId: number) {
    this.http.patch(`${environment.apiBaseUrl}/admin/make-admin/${userId}`, {}).subscribe({
      next: () => this.loadUsers(),
      error: (err) => console.error('❌ Failed to promote user', err)
    });
  }

  removeAdmin(userId: number) {
    this.http.patch(`${environment.apiBaseUrl}/admin/remove-admin/${userId}`, {}).subscribe({
      next: () => this.loadUsers(),
      error: (err) => console.error('❌ Failed to demote user', err)
    });
  }
}
