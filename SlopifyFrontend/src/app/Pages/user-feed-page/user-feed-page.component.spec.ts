import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserFeedPageComponent } from './user-feed-page.component';

describe('UserFeedPageComponent', () => {
  let component: UserFeedPageComponent;
  let fixture: ComponentFixture<UserFeedPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserFeedPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserFeedPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
