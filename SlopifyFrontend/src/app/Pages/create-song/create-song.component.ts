import { Component, OnInit } from '@angular/core';
import { CreateSongDTO } from '../../DTO/CreateSongDTO';
import { ArtistService } from '../../Services/artist.service';
import { SongService } from '../../Services/song.service';
import { MinimalArtistDTO } from '../../DTO/MinimalArtistDTO';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-create-song',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-song.component.html',
  styleUrls: ['./create-song.component.css']
})
export class CreateSongComponent implements OnInit {
  song: CreateSongDTO = new CreateSongDTO();

  availableArtists:MinimalArtistDTO[] = [];

  selectedArtistId: string = '';

  constructor(
    private artistService: ArtistService,
    private songService: SongService
  ){}

  ngOnInit(): void {
    this.artistService.getAll().subscribe({
      next: (value) => {this.availableArtists = value}
    })
  }

  addArtist() {
    if (this.selectedArtistId && !this.song.artistIds.includes(this.selectedArtistId)) {
      this.song.artistIds.push(this.selectedArtistId);
    }
    this.selectedArtistId = '';
  }

  removeArtist(id: string) {
    this.song.artistIds = this.song.artistIds.filter(a => a !== id);
  }

  onMp3Change(event: any) {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      this.song.songMp3Data = (reader.result as string).split(',')[1];
    };
    reader.readAsDataURL(file);
  }

  onImageChange(event: any) {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      this.song.imageData = (reader.result as string).split(',')[1];
    };
    reader.readAsDataURL(file);
  }

  genresInput: string = "";
  submit() {
    this.song.genres = this.genresInput.split(',')
      .map(g => g.trim())
      .filter(g => g.length > 0);

    this.songService.createSong(this.song).subscribe();
  }

}
