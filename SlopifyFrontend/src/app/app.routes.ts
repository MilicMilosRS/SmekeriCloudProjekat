import { Routes } from '@angular/router';
import { RegistrationPageComponent } from './Pages/registration-page/registration-page.component';
import { LoginPageComponent } from './Pages/login-page/login-page.component';
import { SongDetailsPageComponent } from './Pages/song-details-page/song-details-page.component';
import { ArtistDetailsPageComponent } from './Pages/artist-details-page/artist-details-page.component';
import { MainPageComponentComponent } from './Pages/main-page-component/main-page-component.component';
import { UserSubscriptionsPageComponent } from './Pages/user-subscriptions-page/user-subscriptions-page.component';
import { HomePageComponent } from './Pages/home-page/home-page.component';
import { CreateSongComponent } from './Pages/create-song/create-song.component';

export const routes: Routes = [
    {path:'register', component: RegistrationPageComponent},
    {path:'login', component: LoginPageComponent},
    {path:'songs/:id', component: SongDetailsPageComponent},
    {path:'songs/new', component: CreateSongComponent},
    {path:'artists/:id', component: ArtistDetailsPageComponent},
    {path:'', component: MainPageComponentComponent},
    {path:'subscriptions', component: UserSubscriptionsPageComponent}
];
