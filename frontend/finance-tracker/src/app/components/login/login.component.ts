import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username: string = '';
  password: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    if (!this.username || !this.password) return;

    this.authService.login(this.username, this.password).subscribe({
      next: (res) => {
        this.authService.saveToken(res.access_token);
        this.router.navigate(['/dashboard']); // redirect to dashboard after login
      },
      error: (err) => {
        console.error('❌ Login failed', err);
        alert('Invalid username or password');
      }
    });
  }
}
