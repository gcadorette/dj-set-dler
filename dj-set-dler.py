import argparse, sys

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

config = {
    "database_location": Config(DEFAULT_DB_LOCATION, 'Change the database location.'),
    "range_ip_min": Config(DEFAULT_RANGE_IP_MIN, f'Change the minimum value of the range checked for the ftp server. Search if from, by default, 192.168.0.{DEFAULT_RANGE_IP_MIN} to 192.168.0.{DEFAULT_RANGE_IP_MAX}'),
    "range_ip_max": Config(DEFAULT_RANGE_IP_MAX, f'Change the minimum value of the range checked for the ftp server. Search if from, by default, 192.168.0.{DEFAULT_RANGE_IP_MIN} to 192.168.0.{DEFAULT_RANGE_IP_MAX}'),
    "port": Config(DEFAULT_PORT, 'Change the maximum value of the range checked for the ftp server. '),
    "local_music_folder": Config(DEFAULT_LOCAL, 'The local folder to add the set to.'),
    "remote_music_folder": Config(DEFAULT_REMOTE, 'The remote to add the set to.'),
    "yt_playlist_url": Config(DEFAULT_YT_PLAYLIST_URL, 'The Youtube playlist URL. Has to be public.')
}


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    for config_name, config_obj in config.items():
        parser.add_argument(f'--{config_name}', help=config_obj.help, default=config_obj.default_val)

    args = parser.parse_args()
    args_dict = vars(args)

    for config_name, config_obj in config.items():
        val = args_dict[config_name]
        config_obj.val = val
        
    