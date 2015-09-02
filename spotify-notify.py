#!/usr/bin/python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


import dbus
from dbus.mainloop.glib import DBusGMainLoop

import gobject, gtk, os, tempfile, sys, time, re, urllib2
from optparse import OptionParser
from subprocess import *

# The url to use when fetching spotify track information.
SPOTIFY_OPEN_URL = "http://open.spotify.com/track/"

# The path to this application's directory.
APPLICATION_DIR = sys.path[0] + "/"

# The file path to spotify. If empty, it will try to auto detect.
SPOTIFY_PROCESS_NAME = ''

# How often to check if spotify has been closed (in milliseconds).
SPOTIFY_CLOSED_CHECK = 20000

class SpotifyNotify():

    spotifyPath = ''

    tryToReconnect = False

    tmpfile = False

    def __init__(self, debugger):
        self.debug          = debugger
        self.spotifyservice = False

        self.prev      = 0
        self.new       = False
        self.prevMeta  = {}
        self.notifyid  = 0

        self.connect()

    def __del__(self):
        if SpotifyNotify and SpotifyNotify.tmpfile:
            SpotifyNotify.tmpfile.close()

    def connect(self):
        self.debug.out("Connecting to spotify.")
        self.bus = dbus.Bus(dbus.Bus.TYPE_SESSION)

        try:
            self.spotifyservice = self.bus.get_object(
                'com.spotify.qt',
                '/org/mpris/MediaPlayer2'
            )
            SpotifyNotify.tryToReconnect = False
        except Exception, e:
            self.spotifyservice = False
            self.debug.out("Failed to connect.")
            self.debug.out(e)

    def executeCommand(self, key):
        if not key:
            return

        self.connect()
        self.debug.out("Running command: {0}".format(key))
        self.cmd = self.spotifyservice.get_dbus_method(key, 'org.mpris.MediaPlayer2.Player')
        self.cmd()

    def pollChange(self):
        try:
            self.spotifyservice = self.bus.get_object('com.spotify.qt', '/')
            self.cmd = self.spotifyservice.get_dbus_method(
                'GetMetadata',
                'org.freedesktop.MediaPlayer2'
            )
            self.new = self.cmd()
        except Exception, e:
            self.debug.out('Spotify service not connected.')
            SpotifyNotify.tryToReconnect = True

        if (self.prev != self.new):
            self.trackChange(self.new)
            self.prev = self.new

        return 1

    def trackChange(self, *trackChange):
        if not trackChange[0]:
            return

        self.prev = trackChange[0]

        trackInfo = {}
        trackMap  = {
            'artist'    : 'xesam:artist',
            'album'     : 'xesam:album',
            'title'     : 'xesam:title',
            'year'      : 'xesam:contentCreated',
            'trackhash' : 'mpris:trackid',
            'arturl'    : 'mpris:artUrl'
        }

        # Fetch the track information for the notification window.
        for key in trackMap:
            if not trackMap[key] in trackChange[0]:
                continue
            piece = trackChange[0][trackMap[key]]
            if key == 'year':
                piece = str(piece[:4])
            elif isinstance(piece, list):
                piece = ", ".join(piece)

            if not isinstance(piece, str):
                piece = str(piece)

            trackInfo[key] = piece.encode('utf-8')

        if not self.prevMeta\
          or not SpotifyNotify.tmpfile\
          or 'iconfilename' not in self.prevMeta\
          or self.prevMeta['artist'] != trackInfo['artist']\
          or self.prevMeta['album']  != trackInfo['album']:
            trackInfo['iconfilename'] = self.retrieveCoverImage(trackInfo)

        cover_image = ''

        if 'iconfilename' in trackInfo:
            cover_image = trackInfo['iconfilename']
        elif 'iconfilename' in self.prevMeta:
            cover_image = self.prevMeta['iconfilename']
            trackInfo['iconfilename'] = cover_image

        if cover_image == '':
            cover_image = APPLICATION_DIR + 'icon_spotify.png'

        self.prevMeta = trackInfo

        # Connect to notification interface on DBUS.
        self.notifyservice = self.bus.get_object(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications'
        )
        self.notifyservice = dbus.Interface(
            self.notifyservice,
            "org.freedesktop.Notifications"
        )
        notifyText = "{0}\n{1}".format(
            trackInfo['artist'],
            trackInfo['album']
        )
        if len(trackInfo['year']) > 0:
 	        notifyText += " ({0})".format(trackInfo['year'])

        # Send track change information to stdout
        print "Changing track : {0} | {1} | {2} ({3})".format(
            trackInfo['artist'],
            trackInfo['title'],
            trackInfo['album'],
            trackInfo['year']
        )

        # The second param is the replace id, so get the notify id back,
        # store it, and send it as the replacement on the next call.
        self.notifyid = self.notifyservice.Notify(
            "Spotify-notify",
            self.notifyid,
            cover_image,
            trackInfo['title'],
            notifyText,
            [],
            {},
            -1
        )

    def retrieveCoverImage(self, trackInfo):
        if 'arturl' in trackInfo:
            self.debug.out("Simply retrieving image from {0}".format(trackInfo['arturl']))
            iconfilename = self.fetchCoverImage(trackInfo['arturl'])
        else:
            #if (trackInfo['trackhash'][0:14] == 'spotify:local:'):
            #    self.debug.out("Track is a local file. No art available.")
            #    return ''

            self.debug.out("Attempting to fetch image from spotify")
            iconfilename = self.fetchCoverImageSpotify(
                trackInfo['artist'],
                trackInfo['album'],
                trackInfo['trackhash']
            )
        return iconfilename

    def fetchCoverImageSpotify(self, artist, album, trackhash):
        try:
            trackid = trackhash.split(":")[2]
            url = SPOTIFY_OPEN_URL + trackid
            tracksite = urllib2.urlopen(url).read()

            # Attempt to get the image url from the open graph image meta tag.
            imageurl  = False
            metaMatch = re.search(
                '<meta\s[^\>]*property\s*=\s*["\']og:image["\'][^\>]*/?>',
                tracksite
            )
            if metaMatch:
                contentMatch = re.search(
                    'content\s*=\s*["\']([^\"\']*)["\']',
                    metaMatch.group(0)
                )
                if contentMatch:
                    imageurl = contentMatch.group(1)

            if not imageurl:
                self.debug.out("No cover available.")
                raise()

            return self.fetchCoverImage(imageurl)
        except Exception, e:
            self.debug.out("Couldn't fetch cover image.")
            self.debug.out(e)

        return ''

    def fetchCoverImage(self, url):
        # Close the temporary image file, we are going to make a new one.
        if SpotifyNotify.tmpfile:
            SpotifyNotify.tmpfile.close()
            SpotifyNotify.tmpfile = False

        try:
            SpotifyNotify.tmpfile = tempfile.NamedTemporaryFile()
            tmpfilename = SpotifyNotify.tmpfile.name
            self.debug.out("Album art tmp filepath: {0}".format(tmpfilename))

            coverfile = urllib2.urlopen(url)
            SpotifyNotify.tmpfile.write(coverfile.read())
            SpotifyNotify.tmpfile.flush()
            return tmpfilename
        except Exception, e:
            self.debug.out("Couldn't fetch cover image.")
            self.debug.out(e)

        return ''

    @staticmethod
    def startSpotify(Debug):
        if not SpotifyNotify.spotifyPath:
            Debug.out("No spotify process identifier found.")
            return

        ident = SpotifyNotify.spotifyPath
        Debug.out("Looking for spotify as: {0}".format(ident))

        procs = SpotifyNotify.checkForProcess(
            'ps x | grep "{0}" | grep -v grep'.format(ident),
            Debug
        )
        if len(procs):
            Debug.out("Spotify process found as: {0}".format(" ".join(procs[0])))
            return

        Debug.out("Starting new Spotify now.")

        FNULL = open('/dev/null', 'w')
        spid = Popen([ident], stdout=FNULL, stderr=FNULL).pid
        if spid:
            Debug.out("Spotify started, pid: {0}.".format(spid))
        else:
            Debug.out("Spotify could not be started.")

    @staticmethod
    def checkForClosedSpotify(SN, Debug):
        if not SpotifyNotify.spotifyPath:
            Debug.out("No spotify process identifier found.")
            return False

        ident = SpotifyNotify.spotifyPath
        Debug.out("Looking for spotify as: {0}".format(ident))

        procs = SpotifyNotify.checkForProcess(
            'ps x | grep "{0}" | grep -v grep'.format(ident),
            Debug
        )
        if len(procs):
            Debug.out("Spotify process found as: {0}".format(" ".join(procs[0])))

            if (SpotifyNotify.tryToReconnect):
                SN.connect()

            return True

        if SpotifyNotify.tmpfile:
            SpotifyNotify.tmpfile.close()

        Debug.out("Spotify has been closed, therefore I die.")
        exit(0)

    @staticmethod
    def preventDuplicate(Debug):
        mypid = os.getpid()
        Debug.out("My pid: {0}".format(mypid))

        proc = SpotifyNotify.checkForProcess('ps -p {0}'.format(mypid), Debug)
        if not proc[0][3]:
            return

        process = proc[0][3]
        search  = 'ps -C {0}'.format(process)

        Debug.out("Looking for other processes named: {0}".format(process).strip())

        if process == 'python':
            if not sys.argv[0]:
                Debug.out("Process started using python, cannot determine script name.")
                return

            search = 'ps ax | grep "python {0}" | grep -v grep'.format(sys.argv[0])

        for line in SpotifyNotify.checkForProcess(search, Debug):
            if int(line[0]) != mypid:
                print("This program was already running.")
                Debug.out("I am a duplicate. I shall end myself. ({0})".format(" ".join(line)))
                exit(0)

    @staticmethod
    def checkForProcess(proc, Debug):
        output = []

        for line in Popen(proc, shell=True, stdout=PIPE).stdout:
            fields = line.split()
            if not fields[0].isdigit():
                continue

            output.append(fields)

        return output

class MediaKeyHandler():
    def __init__(self, spotifyNotify, debugger):
        self.SN    = spotifyNotify
        self.debug = debugger
        self.keys  = {
            "Play"     : "PlayPause",
            "Stop"     : "Pause",
            "Pause"    : "Pause",
            "Next"     : "Next",
            "Previous" : "Previous",
        }

        try:
            self.bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
            self.bus_object = self.bus.get_object(
                'org.gnome.SettingsDaemon',
                '/org/gnome/SettingsDaemon/MediaKeys'
            )
        except:
            print "Gnome SettingsDaemon not founnd, multimedia keys will not interact with spotify"
            return
        try:
            self.bus_object.GrabMediaPlayerKeys(
                "Spotify",
                0,
                dbus_interface='org.gnome.SettingsDaemon.MediaKeys'
            )
        except:
            pass

        self.bus_object.connect_to_signal(
            'MediaPlayerKeyPressed',
            self.handle_mediakey
        )

    def handle_mediakey(self, *mmkeys):
        for key in mmkeys:
            if not key in self.keys or not self.keys[key]:
                continue

            self.SN.executeCommand(self.keys[key])

class DebugMe():
    def __init__(self, toggle):
        if toggle:
            self.output = True
        else:
            self.output = False

    def out(self, msg):
        if not self.output:
            return

        print(">> {0}".format(msg))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        '-a',
        '--action',
        dest    = 'action',
        default = None,
        type    = 'choice',
        choices = ['playPause', 'play', 'pause', 'next', 'previous'],
        help    = 'Music player actions (playPause/play/pause/next/previous).'
    )
    parser.add_option(
        '-n',
        '--skip_notify',
        dest    = 'skipNotify',
        action  = 'store_true',
        default = False,
        help    = 'Song change notifications will be turned off.'
    )
    parser.add_option(
        '-m',
        '--skip_media_keys',
        dest    = 'skipMediaKeys',
        action  = 'store_true',
        default = False,
        help    = 'Multimedia keys will not interact with spotify.'
    )
    parser.add_option(
        '-s',
        '--skip_spotify',
        dest    = 'skipSpotify',
        action  = 'store_true',
        default = False,
        help    = 'Spotify will not be opened if it is not running and spotify notify will not close when spotify is closed.'
    )
    parser.add_option(
        '-d',
        '--debug',
        dest    = 'debug',
        action  = 'store_true',
        default = False,
        help    = 'Debug messages will be displayed.'
    )

    (options, args) = parser.parse_args()

    Debug = DebugMe(options.debug)
    print("Spotify-notify v0.6")

    if SPOTIFY_PROCESS_NAME:
        SpotifyNotify.spotifyPath = SPOTIFY_PROCESS_NAME
    else:
        for line in Popen('which spotify', shell=True, stdout=PIPE).stdout:
            SpotifyNotify.spotifyPath = str(line).strip()
            break

    if options.skipSpotify:
        Debug.out('Skipping spotify process check.')
    else:
        SpotifyNotify.startSpotify(Debug)

    DBusGMainLoop(set_as_default=True)
    SN = SpotifyNotify(Debug)

    if options.action:
        action = options.action
        action = action[0:1].upper() + action[1:]
        SN.executeCommand(action)
        exit(0)

    SpotifyNotify.preventDuplicate(Debug)

    if not options.skipMediaKeys:
        MH = MediaKeyHandler(SN, Debug)

    loop = gobject.MainLoop()

    if not options.skipSpotify:
        gobject.timeout_add(SPOTIFY_CLOSED_CHECK, SN.checkForClosedSpotify, SN, Debug)
    if not options.skipNotify:
        gobject.timeout_add(500, SN.pollChange)

    loop.run()
