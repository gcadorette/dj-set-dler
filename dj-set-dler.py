import argparse, sys, os, re, ftplib
from pytube import Playlist, YouTube
import ffmpeg

DEFAULT_DB_LOCATION = './db.csv'
DEFAULT_RANGE_IP_MIN = '67'
DEFAULT_RANGE_IP_MAX = '70'
DEFAULT_PORT = '9999'
DEFAULT_LOCAL = "~/Music"
DEFAULT_REMOTE = "Music"
DEFAULT_YT_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLMr2Sm7Ci5lX5kMzWQ_f7zmAhIXmN3iua"
CACHE = "./.cache"

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
        djset = DjSet(video.embed_url, video.author, video.title.replace(",", ""))
        if djset.url not in known_urls:
            videos_to_add.append(djset)
    return videos_to_add
    
def download_videos_from_playlist(videos_url, destination):
    downloaded = []
    for video in videos_url:
        YouTube(video.url).streams.get_audio_only().download(output_path=destination)
        path = f'{destination}/{video.title}'
        path = re.sub(r'((?:[^.]*\.+[^.]+)*)(\.*)', r'\1', path) #basically remove the lasting dots
        path = os.path.abspath(path)
        #mp4 to mp3
        ffmpeg.input(f'{path}.mp4').output(f'{path}.mp3').run()

        downloaded.append({"url": f'{path}.mp3', "title": video.title})
        os.remove(f'{path}.mp4')
    return downloaded

def move_to_local(videos_downloaded, local_music_folder):
    moved_videos = []
    for video in videos_downloaded:
        new_location = os.path.abspath(f'{local_music_folder}/{video["title"]}')
        os.replace(video["url"], new_location)
        moved_videos.append({"url": new_location, "title": video.title})
    return moved_videos

def move_to_ftp(ftp_connection, folder, files_to_send):
    ftp_connection.cwd(folder)
    for file in files_to_send:
        with open(file["url"], "rb") as f:
            ftp_connection.storbinary(f'STOR {file["title"]}.mp3', file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    for config_name, config_obj in config.items():
        parser.add_argument(f'--{config_name}', help=config_obj.help, default=config_obj.default_val)

    args = parser.parse_args()
    args_dict = vars(args)

    for config_name, config_obj in config.items():
        val = args_dict[config_name]
        config_obj.val = val
    min_ip = int(config_obj["range_ip_min"].val)
    max_ip = int(config_obj["range_ip_max"].val)
    ftp = None
    for i in range(min_ip, max_ip + 1):
        ftp = ftplib.FTP(f'192.168.0.{str(i)}:{config_obj["port"].val}')
        try:
            ftp.login()
            break
        except:
            ftp = None
    if ftp is None:
        print("The ftp connection failed. Either the ftp server is not accessible or the configuration is incorrect. Fix the issue and run the script later.")
        return

    videos_to_add = check_playlist_for_new_vids(config["yt_playlist_url"].val, config["database_location"].val)

    if not os.path.exists(CACHE):
        os.mkdir(CACHE)

    videos_downloaded = download_videos_from_playlist(videos_to_add, CACHE)
    