import { Component, OnInit } from '@angular/core';
import { CreateSongDTO } from '../../DTO/CreateSongDTO';
import { ArtistService } from '../../Services/artist.service';
import { SongService } from '../../Services/song.service';
import { MinimalArtistDTO } from '../../DTO/MinimalArtistDTO';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-song',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-song.component.html',
  styleUrls: ['./create-song.component.css']
})
export class CreateSongComponent implements OnInit {
  song: CreateSongDTO = new CreateSongDTO();

  availableArtists: MinimalArtistDTO[] = [];
  selectedArtists: MinimalArtistDTO[] = [];

  selectedArtistId: string = '';
  genresInput: string = "";

  constructor(
    private artistService: ArtistService,
    private songService: SongService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.artistService.getAll().subscribe({
      next: (value) => { this.availableArtists = value; }
    });
  }

  addArtist() {
    const artist = this.availableArtists.find(a => a.id === this.selectedArtistId);
    if (!artist) return;

    const alreadySelected = this.selectedArtists.some(a => a.id === artist.id);
    if (!alreadySelected)
      this.selectedArtists.push(artist);

    this.selectedArtistId = '';
  }

  removeArtist(id: string) {
    this.selectedArtists = this.selectedArtists.filter(a => a.id !== id);
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

  submit() {
    this.song.genres = this.genresInput.split(',')
      .map(g => g.trim())
      .filter(g => g.length > 0);

    this.song.artistIds = this.selectedArtists.map(a => a.id)

    this.songService.createSong(this.song).subscribe({
      next: (value: any) => {console.log(value);
        this.router.navigate(['/songs', value['id']])
      }
    });
  }
}
