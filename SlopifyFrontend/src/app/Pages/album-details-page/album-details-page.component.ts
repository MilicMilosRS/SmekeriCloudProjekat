import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterModule } from '@angular/router';
import { AlbumService } from '../../Services/album.service';
import { AlbumDetails } from '../../DTO/AlbumDetails';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-album-details-page',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './album-details-page.component.html',
  styleUrl: './album-details-page.component.css'
})
export class AlbumDetailsPageComponent implements OnInit{

  albumId: string | null = null;
  details: AlbumDetails = new AlbumDetails();

  constructor(
    private route: ActivatedRoute,
    private albumService: AlbumService
  ){}

  ngOnInit(): void {
    this.albumId = this.route.snapshot.paramMap.get('id');
    if(!this.albumId)
      return
    this.albumService.getDetails(this.albumId).subscribe({
      next: (value) => {this.details = value}
    })
  }
}
