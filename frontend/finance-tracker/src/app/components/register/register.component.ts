import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  username: string = '';
  password: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    if (!this.username || !this.password) return;

    this.authService.register(this.username, this.password).subscribe({
      next: () => {
        alert('✅ Registration successful! Please login.');
        this.router.navigate(['/login']); // redirect to login after success
      },
      error: (err) => {
        console.error('❌ Registration failed', err);
        alert('Registration failed. Try a different username.');
      }
    });
  }
}
