import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { env } from '../../env';
import { SubscribeDTO } from '../DTO/SubscribeDTO';
import { Observable } from 'rxjs';
import { UserSubscription } from '../DTO/UserSubscription';
import { UnsubscribeDTO } from '../DTO/UnsubscribeDTO';

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

  getSubscription(): Observable<UserSubscription[]> {
    return this.http.get<UserSubscription[]>(`${env.apiUrl}/user/subscriptions`);
  }

  unsubscribe(data: UnsubscribeDTO) {
    return this.http.request('DELETE', `${env.apiUrl}/user/subscriptions`, { body: data });
  }

  isSubscribed(data: UnsubscribeDTO): Observable<{ subscribed: boolean }> {
    return this.http.post<{subscribed: boolean}>(`${env.apiUrl}/user/subscriptions/check`, data);
  }

  test() {
    return this.http.post(`${env.apiUrl}/notifications`, {});
  }


}
