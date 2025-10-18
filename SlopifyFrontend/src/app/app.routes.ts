import { Routes } from '@angular/router';
import { RegistrationPageComponent } from './Pages/registration-page/registration-page.component';
import { LoginPageComponent } from './Pages/login-page/login-page.component';

export const routes: Routes = [
    {path:'register', component: RegistrationPageComponent},
    {path:'login', component: LoginPageComponent},
];
