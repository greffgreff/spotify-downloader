# Python Spotify Downloader

A very simple python Spotify downloader that downloads tracks from Spotify directly without needing external sources such as Youtube. 

> ⚠️  This script is made for educational purposes. Please be aware of risks that come with stream-ripping. 

## Prerequisite 

You need to have `librespot`, `pydub`, `music_tag`, and `ffmpeg` python packages already installed. If you have `pip` you can use the following command:
```py
pip install requests librespot pydub music_tag ffmpeg
```

## Usage

Run the python in the CLI like below will yield an MP3 file properly audio tagged:
```py
python spotify_downloader --username <spotify username> --password <spotify password> --track <track id> --output_dir <output directory>
```
Where the track ID is as seen in the track's Spotify URL. For instance, `6FYobREsyfp4SgtpnQbnaf` in the URL `https://open.spotify.com/track/6FYobREsyfp4SgtpnQbnaf`.

Before running the script, please familiarize yourself if its content. 
