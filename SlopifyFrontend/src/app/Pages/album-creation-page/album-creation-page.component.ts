import { Component } from '@angular/core';
import { CreateAlbumDTO } from '../../DTO/CreateAlbumDTO';
import { GetSongsDTO } from '../../DTO/GetSongsDTO';
import { HttpClient } from '@angular/common/http';
import { SongService } from '../../Services/song.service';
import { AlbumService } from '../../Services/album.service';
import { Router, RouterLink, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-album-creation-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './album-creation-page.component.html',
  styleUrl: './album-creation-page.component.css'
})
export class AlbumCreationPageComponent {
  album: CreateAlbumDTO = new CreateAlbumDTO();
  songs: GetSongsDTO[] = [];
  selectedSongId: string = '';

  constructor(
    private http: HttpClient,
    private router: Router,
    private songService: SongService,
    private albumService: AlbumService
  ) {}

  ngOnInit(): void {
    this.songService.getAllSongs().subscribe({
      next: (data) => (this.songs = data),
      error: (err) => console.error('Failed to load songs', err)
    });
  }

  addSong(): void {
    if (!this.selectedSongId) {
      alert('Please select a song.');
      return;
    }

    if (this.album.songIds.includes(this.selectedSongId)) {
      alert('Song already added.');
      return;
    }

    this.album.songIds.push(this.selectedSongId);
    this.selectedSongId = '';
  }

  removeSong(songId: string): void {
    this.album.songIds = this.album.songIds.filter((id) => id !== songId);
  }

  createAlbum(): void {
    if (!this.album.name || this.album.songIds.length === 0) {
      alert('Please enter an album name and add at least one song.');
      return;
    }

    this.albumService.Create(this.album).subscribe({
      next: (value: any) => {
        this.router.navigate(['albums', value['id']])
      },
      error: (err) => {
        console.error('Failed to create album', err);
        alert('Failed to create album.');
      }
    });
  }

  getSongTitle(id: string): string {
    const song = this.songs.find((s) => s.id === id);
    return song ? song.title : id;
  }

}
