import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ArtistService } from '../../Services/artist.service';
import { CreateArtistDTO } from '../../DTO/CreateArtistDTO';
import { Router } from '@angular/router';

@Component({
  selector: 'app-create-artist-page',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './create-artist-page.component.html',
  styleUrl: './create-artist-page.component.css'
})
export class CreateArtistPageComponent {
  artist: CreateArtistDTO = new CreateArtistDTO();
  genresInput: string = '';

  constructor(
    private artistService: ArtistService,
    private router: Router
  ) {}

  submit() {
    this.artist.genres = this.genresInput
      .split(',')
      .map(g => g.trim())
      .filter(g => g.length > 0);

    this.artistService.createArtist(this.artist).subscribe({
      next: (value: any) => {console.log(value);
       this.router.navigate(['/artists', value['id']])}
    });
  }
}
