spotify-notify
==============

Spotify-notify is a notifier for currently playing song in Spotify on a linux system, using the notify-osd notifier (found in e.g. Ubuntu). It also includes support for media keys It is intended for use on Ubuntu systems - current dependency is notify-osd.

![Example image](https://dl.dropbox.com/u/100344/spotifynotify2.png)


Getting started
---------------

These instructions apply to Ubuntu only (but may work on other Debian-based distros)

To get it running, you first need to clone this repository or download the file from above.

`python spotify-notify.py`

It will launch Spotify for you if not already running. Please see options below to change default behavior.

If you want to launch the file directly you can first do:

`chmod a+x spotify-notify.py`
then launch by `./spotify-notify.py`

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