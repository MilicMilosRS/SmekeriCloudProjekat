import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { UserService } from '../../Services/user.service';
import { UserSubscription } from '../../DTO/UserSubscription';
import { Router } from '@angular/router';

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
}
