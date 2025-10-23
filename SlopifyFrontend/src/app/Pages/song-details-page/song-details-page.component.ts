import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SongService } from '../../Services/song.service';
import { SongDetailsDTO } from '../../DTO/SongDetails';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../Services/user.service';
import { GradeDTO } from '../../DTO/GradeDTO';
import { AudioCacheService } from '../../Services/audio-cache.service';

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
    private userService: UserService,
    private audioCache: AudioCacheService
  ){}

  details: SongDetailsDTO = new SongDetailsDTO();
  songId: string | null = null;

  //grades
  grade: number = 0;
  selectedGrade: number = 1;

  audioUrl: string = '';
  loadedFromCache: boolean = false;

  ngOnInit(): void {
    this.songId = this.route.snapshot.paramMap.get('id');
    this.getDetails()

    if(this.songId){
      this.userService.getGrade('SONG', this.songId).subscribe({
        next: (data) => {this.grade = data.grade}
      });
    }
  }

  async loadAudio() {
  if (!this.songId || !this.details.s3SongUrl) return;

  try {
    const cacheExists = await this.audioCache.hasAudio(this.songId);
    if (cacheExists) {
      const blob = await this.audioCache.getAudio(this.songId);
      if (blob) {
        this.audioUrl = URL.createObjectURL(blob);
        this.loadedFromCache = true;
        return;
      }
    }

    //Fetch from web and cache
    const response = await fetch(this.details.s3SongUrl);
    if (!response.ok) throw new Error('Network response was not ok');

    const blob = await response.blob();
    this.audioUrl = URL.createObjectURL(blob);
    await this.audioCache.saveAudio(this.songId, blob);
    this.loadedFromCache = false;

  } catch (err) {
    console.error('Error loading audio:', err);
  }
}


  getDetails(){
    if(this.songId == null)
      return;

    this.songService.getSongDetails(this.songId).subscribe({
      next: async (value) => {
        this.details = value; console.log(value)
        if (this.details.s3SongUrl) {
          await this.loadAudio();
        }
      }
    })
  }

  async clearCache() {
    if (!this.songId) return;

    try {
      const db = await this.audioCache['dbPromise'];
      await db.delete('audioFiles', this.songId);

      console.log('Cache cleared for this song');
    } catch (err) {
      console.error('Error clearing cache:', err);
    }
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
