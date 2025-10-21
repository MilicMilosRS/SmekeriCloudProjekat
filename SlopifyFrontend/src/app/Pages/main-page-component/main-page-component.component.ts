import { Component } from '@angular/core';
import { MinimalContentDTO } from '../../DTO/MinimalContentDTO';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GenreService } from '../../Services/genre.service';
import { RouterModule } from '@angular/router';
import { UnsubscribeDTO } from '../../DTO/UnsubscribeDTO';
import { UserService } from '../../Services/user.service';
import { SubscribeDTO } from '../../DTO/SubscribeDTO';

@Component({
  selector: 'app-main-page-component',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './main-page-component.component.html',
  styleUrl: './main-page-component.component.css'
})
export class MainPageComponentComponent {
  genres: string[] = [];
  selectedGenre: string = "";

  artists: MinimalContentDTO[] = [];
  songs: MinimalContentDTO[] = [];
  albums: MinimalContentDTO[] = [];

  //is subbed to genre
  isSubbed = false;

  constructor(
    private http: HttpClient,
    private genreService: GenreService,
    private userService: UserService
  ) {}

  ngOnInit(): void {
    this.loadGenres();
  }

  loadGenres() {
    this.genreService.getAllGenres().subscribe({
      next: (value) => {this.genres = value}
    })
  }

  onGenreChange() {
    if (!this.selectedGenre) return;

    this.genreService.getContentByGenre(this.selectedGenre).subscribe(
      contents => {
        console.log(contents);
        this.artists = contents.filter(c => c.contentId.startsWith('ARTIST#'));
        this.songs = contents.filter(c => c.contentId.startsWith('SONG#'));
        this.albums = contents.filter(c => c.contentId.startsWith('ALBUM#'));
      });

    this.userService.isSubscribed({contentType: "GENRE", contentId: this.selectedGenre,}).subscribe({
        next: (data) => {
          this.isSubbed = data.subscribed;
        }
      });
  }

  subGenre() {
    var data = new SubscribeDTO();
    data.contentId = this.selectedGenre;
    data.contentType = "GENRE";
    data.contentName = this.selectedGenre;
    this.userService.subscribe(data).subscribe({
      next: (value) => {this.isSubbed = true},
    })
  }

  unsubGenre() {
    var data = new UnsubscribeDTO();
    data.contentId = this.selectedGenre;
    data.contentType = "GENRE";
    this.userService.unsubscribe(data).subscribe({
      next: (value) => {this.isSubbed = false},
    })
  }
}
