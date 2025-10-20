import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SongDetailsPageComponent } from './song-details-page.component';

describe('SongDetailsPageComponent', () => {
  let component: SongDetailsPageComponent;
  let fixture: ComponentFixture<SongDetailsPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SongDetailsPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SongDetailsPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
