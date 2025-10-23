import { ArtistSongDTO } from "./ArtistSongDTO";

export class ArtistDetailsDTO{
    id: string = "";
    name: string = "";
    bio: string = "";
    genres: string[] = [];
    songs: ArtistSongDTO[]=[];
}