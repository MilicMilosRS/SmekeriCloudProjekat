import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      region: 'eu-central-1',
      userPoolId: 'eu-central-1_Z7Bb8pEba',
      userPoolClientId: '29j731php562710sfr6m978oiq',
      loginWith:{
        username: true,
        email: true
      }
    } as any
  }
}, {ssr: false});

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
