import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserSubscriptionsPageComponent } from './user-subscriptions-page.component';

describe('UserSubscriptionsPageComponent', () => {
  let component: UserSubscriptionsPageComponent;
  let fixture: ComponentFixture<UserSubscriptionsPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserSubscriptionsPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserSubscriptionsPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
