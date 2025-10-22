import { MinimalContentDTO } from "./MinimalContentDTO";

export class AlbumDetails{
    id: string = "";
    name: string = "";
    genres: string[] = [];
    songs: MinimalContentDTO[] = [];
}