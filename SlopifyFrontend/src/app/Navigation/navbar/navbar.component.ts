import { Component, OnInit } from '@angular/core';
import { NgIf } from '@angular/common';
import { AuthService } from '../../Auth/auth.service';
import { Router, RouterModule } from "@angular/router";

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [NgIf, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {

  constructor(private authService: AuthService, private router: Router){}

  loggedIn = false;
  loggedGroups: string[] = [];

  async ngOnInit() {
    this.authService.loggedIn$.subscribe(value => {
      this.loggedIn = value;
    });
    this.authService.userGroups$.subscribe(value => {
      this.loggedGroups = value;
    })
    await this.authService.initializeAuthState();
  }

  async logout(){
    await this.authService.logout();
    this.router.navigate(['/']);
  }
}
