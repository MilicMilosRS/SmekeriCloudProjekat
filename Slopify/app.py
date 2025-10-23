#!/usr/bin/env python3
import aws_cdk as cdk
from slopify.notification_stack import NotificationStack
from slopify.core_stack import CoreStack
from slopify.auth_stack import AuthStack
from slopify.genre_stack import GenreStack
from slopify.artist_stack import ArtistStack
from slopify.song_stack import SongStack
from slopify.album_stack import AlbumStack
from slopify.user_stack import UserStack
from slopify.feed_stack import FeedStack
from slopify.endpoint_stack import EndpointStack

app = cdk.App()

core = CoreStack(app, "CoreStack")
auth = AuthStack(app, "AuthStack")
genre = GenreStack(app, "GenreStack", core=core)
artist = ArtistStack(app, "ArtistStack", core=core, genre_stack=genre)
user = UserStack(app, "UserStack")
notification = NotificationStack(app,"NotificationStack", user_stack=user)
song = SongStack(app, "SongStack", core=core, artist_stack=artist, genre_stack=genre, notification_stack=notification)
album = AlbumStack(app, "AlbumStack", song_stack=song, genre_stack=genre)
feed = FeedStack(app, "FeedStack", core_stack=core, song_stack=song, genre_stack=genre, artist_stack=artist, user_stack=user)
endpoint = EndpointStack(app, "EndpointStack", song_stack=song, artist_stack=artist, genre_stack=genre, user_stack=user, auth_stack=auth, notification_stack=notification, album_stack=album, feed_stack=feed)

app.synth()