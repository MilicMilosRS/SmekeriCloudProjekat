import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { env } from '../../env';
import { SubscribeDTO } from '../DTO/SubscribeDTO';
import { Observable } from 'rxjs';
import { UserSubscription } from '../DTO/UserSubscription';
import { UnsubscribeDTO } from '../DTO/UnsubscribeDTO';
import { GradeDTO } from '../DTO/GradeDTO';

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

  getGrade(contentType: string, contentId: string): Observable<{ grade: number }> {
    return this.http.get<{grade: number}>(`${env.apiUrl}/grades`, {params: { contentType: contentType, contentId: contentId }});
  }

  setGrade(data: GradeDTO): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${env.apiUrl}/grades`, data);
  }

  test() {
    return this.http.post(`${env.apiUrl}/notifications`, {});
  }


}
