import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class AdminGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (this.authService.isAuthenticated() && this.authService.isAdmin()) {
      console.log("✅ Admin access granted");
      return true;
    } else {
      console.warn("⛔ Access denied - redirecting to login");
      this.router.navigate(['/login']);
      return false;
    }
  }
}
