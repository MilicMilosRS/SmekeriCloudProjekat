import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SongDetailsDTO } from '../DTO/SongDetails';
import { env } from '../../env';
import { CreateSongDTO } from '../DTO/CreateSongDTO';
import { GetSongsDTO } from '../DTO/GetSongsDTO';

@Injectable({
  providedIn: 'root'
})
export class SongService {

  constructor(private http: HttpClient) { }

  getAllSongs(): Observable<GetSongsDTO[]>{
    return this.http.get<GetSongsDTO[]>(`${env.apiUrl}/songs`);
  }

  createSong(data: CreateSongDTO) {
    return this.http.post(`${env.apiUrl}/songs`, data);
  }

  getSongDetails(id: string): Observable<SongDetailsDTO>{
    return this.http.get<SongDetailsDTO>(`${env.apiUrl}/songs/${id}`);
  }
}
