# pip install requests librespot pydub music_tag ffmpeg

import os
import sys
import requests
import argparse
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from pydub import AudioSegment
import music_tag

quality = AudioQuality.HIGH


def get_track_info(track_id, session):
    access_token = session.tokens().get('playlist-read')

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Failed to get track info: {response.status_code} - {response.text}")

    return response.json()


def fetch_audio_stream(session, track_id, quality):
    track_id = TrackId.from_uri("spotify:track:" + track_id)
    stream = session.content_feeder().load(
        track_id, VorbisOnlyAudioQuality(quality), False, None)
    if stream is not None:
        return stream.input_stream.stream()
    raise RuntimeError("No stream available.")


def download_to_file(stream, filename):
    with open(filename, 'wb') as f:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            f.write(chunk)


def ogg_to_mp3(filename):
    raw_audio = AudioSegment.from_file(filename, format="ogg",
                                       frame_rate=44100, channels=2, sample_width=2)
    raw_audio.export(filename, format="mp3")


def set_audio_tags(filename, track):
    f = music_tag.load_file(filename)
    if f is None or track is None:
        return
    if 'album' in track and 'images' in track['album'] and len(track['album']['images']) > 0:
        art = requests.get(track['album']['images'][0]['url']).content
        f['artwork'] = art
    if 'artists' in track:
        artists = [artist['name'] for artist in track['artists']]
        parsed_artists = ', '.join(artists)
        f['artist'] = parsed_artists
    if 'name' in track:
        f['tracktitle'] = track['name']
    if 'album' in track and 'name' in track['album']:
        f['album'] = track['album']['name']
    if 'album' in track and 'release_date' in track['album']:
        year = track['album']['release_date'].split("-")[0]
        f['year'] = year
    if 'disc_number' in track:
        f['discnumber'] = track['disc_number']
    if 'track_number' in track:
        f['tracknumber'] = track['track_number']
    f['comment'] = """
   /\\_/\\
 ( o.o )
  > ^ <
"""
    f.save()


def main():
    parser = argparse.ArgumentParser(description='Downloads a Spotify track.')
    parser.add_argument('--username', type=str,
                        required=True, help='Spotify username')
    parser.add_argument('--password', type=str,
                        required=True, help='Spotify password')
    parser.add_argument('--out_directory', type=str,
                        required=True, help='Download directory')
    parser.add_argument('--track', type=str, required=True,
                        help='Spotify track id')

    args = parser.parse_args()

    track_id = args.track
    username = args.username
    password = args.password
    out_directory = args.out_directory

    if not os.path.isdir(out_directory):
        os.makedirs(out_directory)

    session = Session.Builder().user_pass(username, password).create()

    track = get_track_info(track_id, session)
    artists = [artist['name'] for artist in track['artists']]
    title = ', '.join(artists) + " - " + track["name"]
    filename = os.path.join(out_directory, title + '.mp3')

    if os.path.isfile(filename):
        sys.stdout.buffer.write(filename.encode("utf-8"))
    else:
        stream = fetch_audio_stream(session, track_id, quality)
        download_to_file(stream, filename)
        ogg_to_mp3(filename)
        set_audio_tags(filename, track)
        sys.stdout.buffer.write(filename.encode("utf-8"))


if __name__ == "__main__":
    main()
