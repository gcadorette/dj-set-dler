import argparse, sys
from pytube import Playlist

DEFAULT_DB_LOCATION = './db.csv'
DEFAULT_RANGE_IP_MIN = '67'
DEFAULT_RANGE_IP_MAX = '70'
DEFAULT_PORT = '9999'
DEFAULT_LOCAL = "~/Music"
DEFAULT_REMOTE = "Music"
DEFAULT_YT_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLMr2Sm7Ci5lX5kMzWQ_f7zmAhIXmN3iua"

class Config:
    def __init__(self, default_val, help):
        self.default_val = default_val
        self.help = f'{help} Default: {default_val}'
        self.val = ''

class DjSet:
    def __init__(self, url, artist, title):
        self.url = url
        self.artist = artist
        self.title = title

config = {
    "database_location": Config(DEFAULT_DB_LOCATION, 'Change the database location.'),
    "range_ip_min": Config(DEFAULT_RANGE_IP_MIN, f'Change the minimum value of the range checked for the ftp server. Search if from, by default, 192.168.0.{DEFAULT_RANGE_IP_MIN} to 192.168.0.{DEFAULT_RANGE_IP_MAX}'),
    "range_ip_max": Config(DEFAULT_RANGE_IP_MAX, f'Change the minimum value of the range checked for the ftp server. Search if from, by default, 192.168.0.{DEFAULT_RANGE_IP_MIN} to 192.168.0.{DEFAULT_RANGE_IP_MAX}'),
    "port": Config(DEFAULT_PORT, 'Change the maximum value of the range checked for the ftp server. '),
    "local_music_folder": Config(DEFAULT_LOCAL, 'The local folder to add the set to.'),
    "remote_music_folder": Config(DEFAULT_REMOTE, 'The remote to add the set to.'),
    "yt_playlist_url": Config(DEFAULT_YT_PLAYLIST_URL, 'The Youtube playlist URL. Has to be public.')
}


def check_playlist_for_new_vids(playlist_url, database_location):
    dj_sets = []
    with open(database_location, "r", encoding="utf-8") as f:
        for line in f.readlines()[1:]:
            entry = line.replace("\n", "").split(",")
            if len(entry) == 0:
                break #if empty line
            dj_sets.append(DjSet(*entry))
    playlist = Playlist(playlist_url)
    videos_to_add = []
    known_urls = [x.url for x in dj_sets]
    for video in playlist.videos:
        djset = DjSet(video.embed_url, video.author, video.title.replace(",", "```"))
        if djset.url not in known_urls:
            videos_to_add.append(djset)
    with open(database_location, "a", encoding="utf-8") as f:
        for vid in videos_to_add:
            f.write(f'{vid.url},{vid.artist},{vid.title}\n')
    return videos_to_add
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    for config_name, config_obj in config.items():
        parser.add_argument(f'--{config_name}', help=config_obj.help, default=config_obj.default_val)

    args = parser.parse_args()
    args_dict = vars(args)

    for config_name, config_obj in config.items():
        val = args_dict[config_name]
        config_obj.val = val
        
    check_playlist_for_new_vids(config["yt_playlist_url"].val, config["database_location"].val)
    