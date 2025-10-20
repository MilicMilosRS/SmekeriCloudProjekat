import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SongDetailsDTO } from '../DTO/SongDetails';
import { env } from '../../env';

@Injectable({
  providedIn: 'root'
})
export class SongService {

  constructor(private http: HttpClient) { }

  getSongDetails(id: string): Observable<SongDetailsDTO>{
    return this.http.get<SongDetailsDTO>(`${env.apiUrl}/songs/${id}`)
  }
}
