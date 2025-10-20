import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SongService } from '../../Services/song.service';
import { SongDetailsDTO } from '../../DTO/SongDetails';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-song-details-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './song-details-page.component.html',
  styleUrl: './song-details-page.component.css'
})
export class SongDetailsPageComponent implements OnInit{
  constructor(
    private route: ActivatedRoute,
    private songService: SongService
  ){}

  details: SongDetailsDTO = new SongDetailsDTO();
  songId: string | null = null;

  ngOnInit(): void {
    this.songId = this.route.snapshot.paramMap.get('id');
    this.getDetails()
  }

  getDetails(){
    if(this.songId == null)
      return;

    this.songService.getSongDetails(this.songId).subscribe({
      next: (value) => {this.details = value; console.log(value)}
    })
  }
}
