import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { MinimalContentDTO } from '../DTO/MinimalContentDTO';
import { env } from '../../env';

@Injectable({
  providedIn: 'root'
})
export class GenreService {
  constructor(private http: HttpClient){}

  getContentByGenre(genre: string): Observable<MinimalContentDTO[]>{
    return this.http.get<MinimalContentDTO[]>(`${env.apiUrl}/contents?genre=${genre}`);
  }

  getAllGenres(): Observable<string[]>{
    return this.http.get<string[]>(`${env.apiUrl}/genres`)
  }
}
