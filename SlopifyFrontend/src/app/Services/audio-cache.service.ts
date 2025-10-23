import { Injectable } from '@angular/core';
import {openDB} from 'idb'

@Injectable({
  providedIn: 'root'
})
export class AudioCacheService {
  private dbPromise = openDB('audio-cache-db', 1, {
    upgrade(db) {
      db.createObjectStore('audioFiles');
    }
  });

  async saveAudio(key: string, blob: Blob) {
    const db = await this.dbPromise;
    await db.put('audioFiles', blob, key);
  }

  async getAudio(key: string): Promise<Blob | undefined> {
    const db = await this.dbPromise;
    return await db.get('audioFiles', key);
  }

  async hasAudio(key: string): Promise<boolean> {
    const db = await this.dbPromise;
    const audio = await db.get('audioFiles', key);
    return !!audio;
  }

  

}
