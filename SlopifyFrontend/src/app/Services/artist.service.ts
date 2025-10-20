import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ArtistDetailsDTO } from '../DTO/ArtistDetails';
import { env } from '../../env';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private http: HttpClient) { }

  getDetails(id: string): Observable<ArtistDetailsDTO>{
    return this.http.get<ArtistDetailsDTO>(`${env.apiUrl}/artists/${id}`)
  }
}
