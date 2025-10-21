import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { UserService } from '../../Services/user.service';
import { UserSubscription } from '../../DTO/UserSubscription';
import { Router } from '@angular/router';
import { UnsubscribeDTO } from '../../DTO/UnsubscribeDTO';

@Component({
  selector: 'app-user-subscriptions-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-subscriptions-page.component.html',
  styleUrl: './user-subscriptions-page.component.css'
})
export class UserSubscriptionsPageComponent implements OnInit {

  constructor(private userService: UserService, private router: Router) {}

  subscriptions: UserSubscription[] = [];

  ngOnInit() {
    this.userService.getSubscription().subscribe({
      next: (data) => {
        this.subscriptions = data;
      },
      error: (err) => {
        console.error('Error fetching subscriptions:', err);
      }
    });
  }

  viewArtist(contentId: string) {
    const id = contentId.split('#')[1];
    if (id) {
        this.router.navigate(['/artists', id]);
    }
  }

  unsubscribe(contentId: string) {

    var data = new UnsubscribeDTO();
    data.contentType = contentId.split('#')[0];
    data.contentId = contentId.split('#')[1];
    this.userService.unsubscribe(data).subscribe({
      next: () => {
        this.subscriptions = this.subscriptions.filter(s => s.contentId !== contentId);
      }
    })
  }
}
