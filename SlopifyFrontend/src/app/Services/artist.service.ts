import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ArtistDetailsDTO } from '../DTO/ArtistDetails';
import { env } from '../../env';
import { MinimalArtistDTO } from '../DTO/MinimalArtistDTO';
import { CreateArtistDTO } from '../DTO/CreateArtistDTO';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private http: HttpClient) { }

  getDetails(id: string): Observable<ArtistDetailsDTO>{
    return this.http.get<ArtistDetailsDTO>(`${env.apiUrl}/artists/${id}`)
  }

  getAll(): Observable<MinimalArtistDTO[]>{
    return this.http.get<MinimalArtistDTO[]>(`${env.apiUrl}/artists`);
  }

  createArtist(data: CreateArtistDTO){
    return this.http.post(`${env.apiUrl}/artists`, data);
  }
}
