import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SongService } from '../../Services/song.service';
import { SongDetailsDTO } from '../../DTO/SongDetails';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../Services/user.service';
import { GradeDTO } from '../../DTO/GradeDTO';

@Component({
  selector: 'app-song-details-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './song-details-page.component.html',
  styleUrl: './song-details-page.component.css'
})
export class SongDetailsPageComponent implements OnInit{
  constructor(
    private route: ActivatedRoute,
    private songService: SongService,
    private userService: UserService
  ){}

  details: SongDetailsDTO = new SongDetailsDTO();
  songId: string | null = null;

  //grades
  grade: number = 0;
  selectedGrade: number = 1;

  ngOnInit(): void {
    this.songId = this.route.snapshot.paramMap.get('id');
    this.getDetails()

    if(this.songId)
      this.userService.getGrade('SONG', this.songId).subscribe({
        next: (data) => {this.grade = data.grade}
      });
  }

  getDetails(){
    if(this.songId == null)
      return;

    this.songService.getSongDetails(this.songId).subscribe({
      next: (value) => {this.details = value; console.log(value)}
    })
  }

  submitGrade() {
        if (this.songId == null) return;
    
        const gradeDTO: GradeDTO = {
          contentId: this.songId,
          contentType: 'SONG',
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
