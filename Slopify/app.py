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
from slopify.endpoint_stack import EndpointStack

app = cdk.App()

core = CoreStack(app, "CoreStack")
auth = AuthStack(app, "AuthStack")
genre = GenreStack(app, "GenreStack", core=core)
artist = ArtistStack(app, "ArtistStack", core=core, genre_stack=genre)
notification = NotificationStack(app,"NotificationStack")
song = SongStack(app, "SongStack", core=core, artist_stack=artist, genre_stack=genre,subscriptions_table=notification.subscriptions_table, notification=notification)
user = UserStack(app, "UserStack")
album = AlbumStack(app, "AlbumStack")
endpoint = EndpointStack(app, "EndpointStack", song_stack=song, artist_stack=artist, genre_stack=genre, user_stack=user, auth_stack=auth, notification_stack=notification)

app.synth()