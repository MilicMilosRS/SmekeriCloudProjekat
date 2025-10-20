import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { env } from '../../env';
import { SubscribeDTO } from '../DTO/SubscribeDTO';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  getUserData(){
    return this.http.get(`${env.apiUrl}/user`)
  }

  subscribe(data: SubscribeDTO){
    return this.http.post(`${env.apiUrl}/user/subscriptions`, data)
  }

  test() {
    return this.http.post(`${env.apiUrl}/notifications`, {});
  }


}
