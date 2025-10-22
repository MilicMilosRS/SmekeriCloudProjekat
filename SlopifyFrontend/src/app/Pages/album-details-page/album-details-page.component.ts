import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterModule } from '@angular/router';
import { AlbumService } from '../../Services/album.service';
import { AlbumDetails } from '../../DTO/AlbumDetails';
import { CommonModule } from '@angular/common';
import { UserService } from '../../Services/user.service';
import { GradeDTO } from '../../DTO/GradeDTO';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-album-details-page',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './album-details-page.component.html',
  styleUrl: './album-details-page.component.css'
})
export class AlbumDetailsPageComponent implements OnInit{

  albumId: string | null = null;
  details: AlbumDetails = new AlbumDetails();

  //grades
  grade: number = 0;
  selectedGrade: number = 1;

  constructor(
    private route: ActivatedRoute,
    private albumService: AlbumService,
    private userService: UserService
  ){}

  ngOnInit(): void {
    this.albumId = this.route.snapshot.paramMap.get('id');
    if(!this.albumId)
      return
    this.albumService.getDetails(this.albumId).subscribe({
      next: (value) => {this.details = value}
    })
    this.userService.getGrade('ALBUM', this.albumId).subscribe({
      next: (data) => {this.grade = data.grade}
    });
  }

  submitGrade() {
    if (this.albumId == null) return;

    const gradeDTO: GradeDTO = {
      contentId: this.albumId,
      contentType: 'ALBUM',
      grade: Number(this.selectedGrade)
    };

    this.userService.setGrade(gradeDTO).subscribe({
      next: (data) => {
        this.grade = this.selectedGrade;
        console.log('Grade submitted successfully');
      },
      error: (err) => console.error('Error submitting grade:', err)
      });
  }
}
