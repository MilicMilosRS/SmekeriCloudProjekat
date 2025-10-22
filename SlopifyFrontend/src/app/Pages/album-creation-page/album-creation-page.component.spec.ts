import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlbumCreationPageComponent } from './album-creation-page.component';

describe('AlbumCreationPageComponent', () => {
  let component: AlbumCreationPageComponent;
  let fixture: ComponentFixture<AlbumCreationPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlbumCreationPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlbumCreationPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
