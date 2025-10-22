import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CreateAlbumDTO } from '../DTO/CreateAlbumDTO';
import { env } from '../../env';

@Injectable({
  providedIn: 'root'
})
export class AlbumService {

  constructor(private http: HttpClient) { }

  Create(data: CreateAlbumDTO){
    return this.http.post(`${env.apiUrl}/albums`, data)
  }
}
