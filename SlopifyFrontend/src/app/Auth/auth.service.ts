import { Injectable } from '@angular/core';
import { RegisterData } from '../DTO/RegisterData';
import { signUp, signIn, fetchAuthSession } from 'aws-amplify/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() { }

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
      const { isSignedIn, nextStep } = await signIn({ username, password });
      console.log('Login success:', isSignedIn, nextStep);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
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

  async logout() {
    const { signOut } = await import('aws-amplify/auth');
    await signOut();
  }
}
