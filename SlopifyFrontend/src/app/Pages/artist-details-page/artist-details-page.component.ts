import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ArtistService } from '../../Services/artist.service';
import { ArtistDetailsDTO } from '../../DTO/ArtistDetails';
import { CommonModule } from '@angular/common';
import { UserService } from '../../Services/user.service';
import { SubscribeDTO } from '../../DTO/SubscribeDTO';
import { UnsubscribeDTO } from '../../DTO/UnsubscribeDTO';

@Component({
  selector: 'app-artist-details-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './artist-details-page.component.html',
  styleUrl: './artist-details-page.component.css'
})
export class ArtistDetailsPageComponent implements OnInit{
  constructor(
    private route: ActivatedRoute,
    private artistService: ArtistService,
    private userService: UserService
  ){}

  details: ArtistDetailsDTO = new ArtistDetailsDTO();
  artistId: string | null = null;

  //subscription
  isSubbed = false;

  ngOnInit(): void {
    this.artistId = this.route.snapshot.paramMap.get('id');
    this.getDetails()
    if(this.artistId)
      this.userService.isSubscribed({contentType: "ARTIST", contentId: this.artistId,}).subscribe({
        next: (data) => {
          this.isSubbed = data.subscribed;
        }
      });
  }

  getDetails(){
    if(this.artistId == null)
      return

    this.artistService.getDetails(this.artistId).subscribe({
      next: (value) => {this.details = value; console.log(value);
      }
    })
  }

  subscribeToArtist(){
    if(this.artistId == null)
      return;

    var data = new SubscribeDTO();
    data.contentId = this.artistId;
    data.contentType = "ARTIST";
    data.contentName = this.details.name;
    this.userService.subscribe(data).subscribe({
      next: (value) => {this.isSubbed = true},
    })
  }

  unsubscribeFromArtist(){
    if(this.artistId == null)
      return;

    var data = new UnsubscribeDTO();
    data.contentId = this.artistId;
    data.contentType = "ARTIST";
    this.userService.unsubscribe(data).subscribe({
      next: (value) => this.isSubbed = false
    })
  }

  /*testSubscription() {
  this.userService.test().subscribe({
    next: (res) => console.log('Test trigger successful', res),
    error: (err) => console.error('Test trigger failed', err)
  });
}*/

}
