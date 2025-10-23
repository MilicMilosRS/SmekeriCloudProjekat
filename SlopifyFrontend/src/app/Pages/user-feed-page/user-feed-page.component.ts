import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FeedService } from '../../Services/feed.service';
import { FeedSongDTO } from '../../DTO/FeedSongDTO';

@Component({
  selector: 'app-user-feed-page',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './user-feed-page.component.html',
  styleUrl: './user-feed-page.component.css'
})
export class UserFeedPageComponent implements OnInit{
  constructor(private feedService: FeedService){};

  songs: FeedSongDTO[] = []

  ngOnInit(): void {
    this.feedService.getFeed().subscribe({
      next: (value) => {this.songs = value}
    })
  }
}
