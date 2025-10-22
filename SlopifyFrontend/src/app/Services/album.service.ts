import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CreateAlbumDTO } from '../DTO/CreateAlbumDTO';
import { env } from '../../env';
import { Observable } from 'rxjs';
import { AlbumDetails } from '../DTO/AlbumDetails';

@Injectable({
  providedIn: 'root'
})
export class AlbumService {

  constructor(private http: HttpClient) { }

  getDetails(id: string): Observable<AlbumDetails>{
    return this.http.get<AlbumDetails>(`${env.apiUrl}/albums/${id}`)
  }

  Create(data: CreateAlbumDTO){
    return this.http.post(`${env.apiUrl}/albums`, data)
  }
}
