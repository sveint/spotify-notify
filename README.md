spotify-notify
==============

Spotify-notify is a __notifier for currently playing song__ in Spotify on a linux system, using the notify-osd notifier (found in e.g. Ubuntu). It also includess __support for media keys__. It is intended for use on Ubuntu systems - current dependency is notify-osd.

![Example image](https://dl.dropbox.com/u/100344/spotifynotify2.png)


Getting started
---------------
### Installation

If you want to install spotify-notify permanently, it's recommended to follow these instructions. They apply to Ubuntu only but may work on other Debian-based distros as well.

Just execute the following terminal commands to install spotify-notify:
```bash
sudo mkdir /opt/spotify-notify/     # Create new directory to install spotify-notify
cd /opt/spotify-notify/             # Change current directory to this folder
# Download current version of spotify-notify
sudo wget https://raw.githubusercontent.com/sveint/spotify-notify/master/spotify-notify.py
sudo chmod a+x spotify-notify.py    # Mark spotify-notify.py as an executable
python spotify-notify.py -s &       # Start spotify-notify in background
```

### Adding spotify-notify to autostart
In Ubuntu you can easily add spotify-notify to the autostart. You only need to open the startup-programmes dialog. More details can be found in the [Ubuntu Wiki](https://help.ubuntu.com/community/AddingProgramToSessionStartup#Startup_Programs). As the name you can choose something like "Spotify Notify" and as the command to be executed, choose

`python spotify-notify.py -s`

The comment field can be left empty.

Advanced
--------
### Running spotify-notify (general information)
To get it running, you first need to clone this repository or download the file `spotify-notify.py`. Afterwards you can run spotify-notify by

`python spotify-notify.py`

It will launch Spotify for you if not already running. Please see options below to change default behavior.

If you want to launch the file directly you can first add execution rights to it:

`chmod a+x spotify-notify.py`

then launch by

`./spotify-notify.py`

### Command line options

Available options are:

| Option                        | Description                                                |
| ------------------------------|:----------------------------------------------------------:|
| `-h, --help`                  | Show help message and exit                                 |
| `-a ACTION, --action=ACTION`  | Music player actions (playPause/play/pause/next/previous). |
| `-n, --skip_notify`           | Song change notifications will be turned off.              |
| `-m, --skip_media_keys`       | Multimedia keys will not interact with spotify.            |
| `-s, --skip_spotify`          | Spotify will not be opened if it is not running and spotify notify will not close when spotify is closed. |
| `-d, --debug`                 | Debug messages will be displayed.                          |



### FAQ


#### Q: How can I launch the script at startup?

Just add a new entry to the startup applications, using the following as the "Command"-string;

`/<path>/<to>/spotify-notify/spotify-notify.py -s`

- Make sure that "spotify-notify.py" is executable
- Make note of the "-s" parameter at the end, as this makes sure that spotify-notify doesn't start Spotify, and that it doesn't quit when you quit Spotify.


#### Q: I want to use the script just for the media key support. How can I do this?

Launch with -n as parameter.


#### Q: Do I need Ubuntu to use this script? Will others distros work?

A: Other distros supporting the same messaging system might work, please report any success stories!


Spotify-notify is in no way affiliated with Spotify. Spotify is the registered trade mark of the Spotify Group.
