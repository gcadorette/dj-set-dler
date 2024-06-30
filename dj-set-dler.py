import argparse, sys, os, re, ftplib, requests, time
from pytube import Playlist, YouTube
import ffmpeg
import music_tag
import emoji

DEFAULT_DB_LOCATION = './db.csv'
DEFAULT_RANGE_IP_MIN = '67'
DEFAULT_RANGE_IP_MAX = '70'
DEFAULT_PORT = '9999'
DEFAULT_LOCAL = "~/Music"
DEFAULT_REMOTE = "Music"
DEFAULT_YT_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLMr2Sm7Ci5lX5kMzWQ_f7zmAhIXmN3iua"
DEFAULT_POLLING = 30
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
    "yt_playlist_url": Config(DEFAULT_YT_PLAYLIST_URL, 'The Youtube playlist URL. Has to be public.'),
    "polling_min": Config(DEFAULT_POLLING, 'Polling rate, in minutes. The script will be looking for changes to the youtube playlist every polling rate minutes.')
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
        title = video.title.replace(",", "").replace("/", "").replace(".", "").replace("#", "")
        title = emoji.replace_emoji(title, '')
        djset = DjSet(video.embed_url, video.author, title)

        if djset.url not in known_urls:
            videos_to_add.append(djset)
    return videos_to_add
    
def download_videos_from_playlist(videos_url, destination):
    downloaded = []
    elems_in_cache_folder = [x.split(".")[0] for x in os.listdir(destination)]
    for video in videos_url:
        dir_name = video.title if video.title[0] != '/' else video.title[1:]
        dir_name = f'{destination}/{dir_name}/'
        downloaded.append({"url": dir_name, "title": video.title})

        if video.title in elems_in_cache_folder:
            continue
        youtube_vid = YouTube(video.url)
        thumbnail_url = youtube_vid.thumbnail_url
        dled_file = youtube_vid.streams.get_audio_only().download(output_path=destination)

        path = f'{destination}/{video.title}'
        path = os.path.abspath(path)

        os.rename(dled_file, f'{path}.mp4')

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        #mp4 to mp3
        stream = ffmpeg.input(f'{path}.mp4').output(f'{dir_name}/{video.title}.mp3')
        ffmpeg.run(stream, overwrite_output=True)
        os.remove(f'{path}.mp4')

        img_data = requests.get(thumbnail_url).content
        
        song = music_tag.load_file(f'{dir_name}/{video.title}.mp3')
        song["artist"] = video.artist
        song["tracktitle"] = video.title

        with open(f'{dir_name}/{video.title}.jpg', "wb") as f:
            f.write(img_data)
        with open(f'{dir_name}/{video.title}.jpg', "rb") as f:
            song["artwork"] = f.read()

        song.save()

        print(f'downloaded {video.title}')
    return downloaded

def move_to_local(videos_downloaded, local_music_folder):
    moved_videos = []
    destination = os.path.expanduser(local_music_folder) if local_music_folder[0] == '~' else os.path.abspath(local_music_folder)
    for video in videos_downloaded:
        new_location = os.path.abspath(f'{destination}/{video["title"]}')
        if not os.path.exists(new_location):
            os.replace(video["url"], new_location)
            moved_videos.append({"url": new_location, "title": video["title"]})
            print(f'moved {video["title"]} to local folder')
    return moved_videos

def move_to_ftp(ftp_connection, folder, files_to_send):
    ftp_connection.cwd(folder)
    filetypes = ['mp3', 'jpg']
    for file in files_to_send:
        if file["title"] not in ftp_connection.nlst():
            ftp_connection.mkd(file["title"])
        else:
            continue
        ftp_connection.cwd(file["title"])
        for filetype in filetypes:
            filename =  f'{file["title"]}.{filetype}'
            if filename not in ftp_connection.nlst():
                with open(f'{file["url"]}/{file["title"]}.{filetype}', "rb") as f:
                    ftp_connection.storbinary(f'STOR {filename}', f)
        print(f'moved {file["title"]} to ftp server')
        ftp_connection.cwd("..")

def save_to_db(database_location, songs_added):
    for song in songs_added:
        with open(database_location, "a", encoding="utf-8") as f:
            f.write(f'{song.url},{song.artist},{song.title}\n')
        print(f'saved {song.title} to database')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    for config_name, config_obj in config.items():
        parser.add_argument(f'--{config_name}', help=config_obj.help, default=config_obj.default_val)

    args = parser.parse_args()
    args_dict = vars(args)

    for config_name, config_obj in config.items():
        val = args_dict[config_name]
        config_obj.val = val

    min_ip = int(config["range_ip_min"].val)
    max_ip = int(config["range_ip_max"].val)

    if min_ip < 0 or min_ip > 255:
        sys.exit("The minimum ip should be between 0 and 255. Please enter a valid value")
    if max_ip < 0 or min_ip > 255:
        sys.exit("The maximum ip should be between 0 and 255. Please enter a valid value")

    polling_rate = int(config["polling_min"].val)

    while True:
        ftp = None
        for i in range(min_ip, max_ip + 1):
            try:
                ftp = ftplib.FTP()
                ftp.connect(f'192.168.0.{str(i)}', int(config["port"].val))
                ftp.login()
                break
            except Exception as e:
                ftp = None
        if ftp is not None:
            videos_to_add = check_playlist_for_new_vids(config["yt_playlist_url"].val, config["database_location"].val)

            if not os.path.exists(CACHE):
                os.mkdir(CACHE)

            videos_downloaded = download_videos_from_playlist(videos_to_add, CACHE)
            videos_moved = move_to_local(videos_downloaded, config["local_music_folder"].val)
            move_to_ftp(ftp, config["remote_music_folder"].val, videos_moved)

            save_to_db(config["database_location"].val, videos_to_add)
            ftp.close()
        else:
            print("The ftp connection failed. Either the ftp server is not accessible or the configuration is incorrect. Fix the issue and run the script later.")

        time.sleep(polling_rate * 60) #wait until the next polling