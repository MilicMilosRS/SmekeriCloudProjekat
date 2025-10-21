import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../Auth/auth.service';
import { UserService } from '../../Services/user.service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent {
  username: string = "";
  password: string = "";

  message: string = "";

  constructor(private authService: AuthService, private userService: UserService, private router: Router) {}

  async login() {
    const success = await this.authService.loginUser(this.username, this.password);
    this.message = success ? 'Login successful!' : 'Login failed!';
    if (success)
      this.router.navigate(['/']);
  }

  getUserData(){
    this.userService.getUserData().subscribe({
      next: (value) => {console.log(value);
      }
    })
  }
}
