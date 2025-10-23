import { Routes } from '@angular/router';
import { RegistrationPageComponent } from './Pages/registration-page/registration-page.component';
import { LoginPageComponent } from './Pages/login-page/login-page.component';
import { SongDetailsPageComponent } from './Pages/song-details-page/song-details-page.component';
import { ArtistDetailsPageComponent } from './Pages/artist-details-page/artist-details-page.component';
import { MainPageComponentComponent } from './Pages/main-page-component/main-page-component.component';
import { UserSubscriptionsPageComponent } from './Pages/user-subscriptions-page/user-subscriptions-page.component';
import { HomePageComponent } from './Pages/home-page/home-page.component';
import { CreateSongComponent } from './Pages/create-song/create-song.component';
import { CreateArtistPageComponent } from './Pages/create-artist-page/create-artist-page.component';
import { AlbumCreationPageComponent } from './Pages/album-creation-page/album-creation-page.component';
import { AlbumDetailsPageComponent } from './Pages/album-details-page/album-details-page.component';
import { UserFeedPageComponent } from './Pages/user-feed-page/user-feed-page.component';

export const routes: Routes = [
    {path:'register', component: RegistrationPageComponent},
    {path:'login', component: LoginPageComponent},
    {path:'songs/new', component: CreateSongComponent},
    {path:'songs/:id', component: SongDetailsPageComponent},
    {path:'artists/new', component: CreateArtistPageComponent},
    {path:'artists/:id', component: ArtistDetailsPageComponent},
    {path:'albums/new', component: AlbumCreationPageComponent},
    {path:'albums/:id', component: AlbumDetailsPageComponent},
    {path:'discover', component: MainPageComponentComponent},
    {path:'', component: UserFeedPageComponent},
    {path:'subscriptions', component: UserSubscriptionsPageComponent}
];
