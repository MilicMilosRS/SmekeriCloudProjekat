import { Component } from '@angular/core';
import { RegisterData } from '../../DTO/RegisterData';
import { AuthService } from '../../Auth/auth.service';
import { FormsModule } from '@angular/forms'

@Component({
  selector: 'app-registration-page',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './registration-page.component.html',
  styleUrl: './registration-page.component.css'
})
export class RegistrationPageComponent {
  registrationData: RegisterData = new RegisterData();
  message: string = '';

  constructor(private authService: AuthService) {}

  async register() {
    const today = new Date();
    const birthDate = new Date(this.registrationData.birthDate);

    if (birthDate >= today) {
      this.message = 'Birthday must be in the past!';
      return;
    }

    try {
      const success = await this.authService.registerUser(this.registrationData);
      this.message = success ? 'Registration successful!' : 'Registration failed!';
    } catch (err) {
      this.message = 'Registration failed!';
      console.error(err);
  }
}
}
