import { Injectable } from '@angular/core';
import { RegisterData } from '../DTO/RegisterData';
import { signUp, signIn, fetchAuthSession } from 'aws-amplify/auth';
import { jwtDecode } from 'jwt-decode';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() {}

  private loggedInSubject = new BehaviorSubject<boolean>(false);
  public loggedIn$ = this.loggedInSubject.asObservable();

  private userGroupsSubject = new BehaviorSubject<string[]>([]);
  public userGroups$ = this.userGroupsSubject.asObservable();

  async initializeAuthState() {
    try {
      const session = await fetchAuthSession();
      const token = session.tokens?.idToken?.toString();

      if (token) {
        this.loggedInSubject.next(true);

        const decoded: any = jwtDecode(token);
        const groups: string[] = decoded['cognito:groups'] || [];
        this.userGroupsSubject.next(groups);
      } else {
        this.loggedInSubject.next(false);
        this.userGroupsSubject.next([]);
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      this.loggedInSubject.next(false);
      this.userGroupsSubject.next([]);
    }
  }

  async registerUser(data: RegisterData) {
    try {
      const { nextStep } = await signUp({
        username: data.username,
        password: data.password,
        options: {
          userAttributes: {
            given_name: data.firstName,
            family_name: data.lastName,
            birthdate: data.birthDate,
            email: data.email
          }
        }
      });
      console.log('Signup successful:', nextStep);
      return true;
    } catch (error) {
      console.error('Error signing up:', error);
      return false;
    }
  }

  async loginUser(username: string, password: string) {
    try {
      const { isSignedIn } = await signIn({ username, password });
      console.log('Login success:', isSignedIn);

      if (isSignedIn) {
        this.loggedInSubject.next(true);
        await this.initializeAuthState();
      }

      return true;
    } catch (error) {
      console.error('Login failed:', error);
      this.loggedInSubject.next(false);
      return false;
    }
  }

  async getJwtToken(): Promise<string | null> {
    try {
      const session = await fetchAuthSession();
      return session.tokens?.idToken?.toString() ?? null;
    } catch (error) {
      console.error('Failed to fetch JWT:', error);
      return null;
    }
  }

  async isLoggedIn(): Promise<boolean> {
    try {
      const session = await fetchAuthSession();
      const idToken = session.tokens?.idToken?.toString();
      const loggedIn = !!idToken;
      this.loggedInSubject.next(loggedIn);
      return loggedIn;
    } catch (error) {
      console.error('Failed to check login status:', error);
      this.loggedInSubject.next(false);
      return false;
    }
  }

  async logout() {
    const { signOut } = await import('aws-amplify/auth');
    await signOut();
    this.loggedInSubject.next(false);
  }
}
