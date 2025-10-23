import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { FeedSongDTO } from '../DTO/FeedSongDTO';
import { env } from '../../env';

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  constructor(private http: HttpClient) { }

  getFeed(): Observable<FeedSongDTO[]>{
    return this.http.get<FeedSongDTO[]>(`${env.apiUrl}/user/feed`)
  }
}
