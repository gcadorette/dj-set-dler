This is a script that I made to automatically download songs (mostly dj sets) when I add them to a certain playlist on Youtube. It downloads both the highest quality stream and the thumbnail and add them to both my PC music folder and my phone music folder using FTP. 

Please note that this script has been made with a very limited use in mind and has only been tested on Pop_Os using my particuliar ftp server setup. 

## Android FTP setup
To setup the FTP server on my phone, I simply use Solid Explorer's. It creates a FTP server with an IP address between 192.168.0.67 and 192.168.0.69, usually, on port 9999. 


## Linux service setup
I use this script as a service by adding `dj-set-updater.service` and copying it to the `etc/systemd/system/` folder. 

The following commands must then be executed:

First, we need to reset the service files by doing
`sudo systemctl daemon-reload`

Then, we can either choose to start the service by doing
`sudo systemctl start dj-set-updater.service`

To enable it on boot
`sudo systemctl enable dj-set-updater.service`

To check the service status
`sudo systemctl status dj-set-updater.service`

Please note that some informations must be changed in the `dj-set-updater.service` file must be changed before it can be used as a service.

- The user must be changed as the user of your machine
- WorkingDirectory must be changed to the directory where the script is located
- Validate that your python interpreter is at `/usr/bin/python3`. To make sure, you can do `whereis python` (or `whereis python3`) in a terminal. 

Note that I am using the script's default parameter (as I am the default of my own life). You can either change the defaults direcly in the script or change `dj-set-updater.service` by using the parameters of the script.

## Dependencies
This script uses the following external dependencies, that must be installed using `pip`:
- pytube
- ffmpeg
- music_tag
- emoji

Note that ffmpeg also needs to be installed (outside of `pip`) by typing `sudo apt install ffmpeg` in a terminal (on a debian based distribution, of course).

## Script parameters
- `database_location`: the relative path of the .csv file that will be used as a database. The file will be created if it doesn't exist.
- `range_ip_min`: the minimum range of the ip. Note that is made with a local ip (so 192.168.0.xxx/24) in mind, so only the last digit of the ip will be affected. 
- `range_ip_max`: the maximum range of the ip, using the same 192.168.0.xxx/24 assumption.
- `port`: the port of the ftp server
- `local_music_folder`: the absolute path of the local music folder
- `remote_music_folder`: the path of the remote music folder
- `yt_playlist_url`: the url of the Youtube playlist. Should start by `https://www.youtube.com/playlist?list=`.
- `polling_min`: How many minutes the script waits between every sync attempt.