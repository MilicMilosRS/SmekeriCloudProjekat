import { Component } from '@angular/core';
import { MinimalContentDTO } from '../../DTO/MinimalContentDTO';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GenreService } from '../../Services/genre.service';

@Component({
  selector: 'app-main-page-component',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './main-page-component.component.html',
  styleUrl: './main-page-component.component.css'
})
export class MainPageComponentComponent {
  genres: string[] = [];
  selectedGenre: string = "";

  artists: MinimalContentDTO[] = [];
  songs: MinimalContentDTO[] = [];
  albums: MinimalContentDTO[] = [];

  constructor(
    private http: HttpClient,
    private genreService: GenreService,
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
  }
}
