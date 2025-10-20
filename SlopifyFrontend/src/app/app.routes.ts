import { Routes } from '@angular/router';
import { RegistrationPageComponent } from './Pages/registration-page/registration-page.component';
import { LoginPageComponent } from './Pages/login-page/login-page.component';
import { SongDetailsPageComponent } from './Pages/song-details-page/song-details-page.component';
import { ArtistDetailsPageComponent } from './Pages/artist-details-page/artist-details-page.component';

export const routes: Routes = [
    {path:'register', component: RegistrationPageComponent},
    {path:'login', component: LoginPageComponent},
    {path:'songs/:id', component: SongDetailsPageComponent},
    {path:'artists/:id', component: ArtistDetailsPageComponent}
];
