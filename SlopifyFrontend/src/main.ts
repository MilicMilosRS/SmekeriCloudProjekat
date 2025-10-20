import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      region: 'eu-central-1',
      userPoolId: 'eu-central-1_RcYdFX66F',
      userPoolClientId: '19dp9ulrc79mq59redhq4c0gmd',
      loginWith:{
        username: true,
        email: true
      }
    } as any
  }
}, {ssr: false});

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
