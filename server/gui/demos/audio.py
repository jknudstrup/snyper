# audio.py

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021-2024 Peter Hinch

# Uses nonblocking reads rather than StreamWriter because there is no non-hacky way
# to do non-allocating writes: see https://github.com/micropython/micropython/pull/7868
# Hack was
# swriter.out_buf = wav_samples_mv[:num_read]
# await swriter.drain()
# WAV files
# The proper way is to parse the WAV file as per
# https://github.com/miketeachman/micropython-i2s-examples/blob/master/examples/wavplayer.py
# Here for simplicity we assume stereo files ripped from CD's.

import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from machine import I2S
from machine import Pin
import pyb

root = "/sd/music"  # Location of directories containing albums

# Do allocations early
BUFSIZE = 1024 * 20  # 5.8ms/KiB 8KiB occasional dropouts
WAVSIZE = 1024 * 2
_RFSH_GATE = const(10)  # While playing, reduce refresh rate
# allocate sample array once
wav_samples = bytearray(WAVSIZE)

# ======= I2S CONFIGURATION =======

# Pyboard D
pyb.Pin("EN_3V3").on()  # Pyboard D: provide 3.3V on 3V3 output pin
I2S_ID = 1
config = {
    "sck": Pin("W29"),
    "ws": Pin("W16"),
    "sd": Pin("Y4"),
    "mode": I2S.TX,
    "bits": 16,  # Sample size in bits/channel
    "format": I2S.STEREO,
    "rate": 44100,  # Sample rate in Hz
    "ibuf": BUFSIZE,  # Internal buffer size
}

# RP2 from https://docs.micropython.org/en/latest/rp2/quickref.html#i2s-bus
# I2S_ID = 0
# config = {
#     "sck": Pin(16),
#     "ws": Pin(17),
#     "sd": Pin(18),
#     "mode": I2S.TX,
#     "bits": 16,  # Sample size in bits/channel
#     "format": I2S.STEREO,
#     "rate": 44100,  # Sample rate in Hz
#     "ibuf": BUFSIZE,  # Buffer size
# }

audio_out = I2S(I2S_ID, **config)

# ======= GUI =======

from gui.widgets import Button, CloseButton, HorizSlider, Listbox, Label
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
import gui.fonts.icons as icons
from gui.core.colors import *

import os
import gc
import asyncio
import sys

# Initial check on filesystem
try:
    subdirs = [x[0] for x in os.ilistdir(root) if x[1] == 0x4000]
    if len(subdirs):
        subdirs.sort()
    else:
        print("No albums found in ", root)
        sys.exit(1)
except OSError:
    print(f"Expected {root} directory not found.")
    sys.exit(1)


class SelectScreen(Screen):
    songs = []
    album = ""

    def __init__(self, wri):
        super().__init__()
        Listbox(wri, 2, 2, elements=subdirs, dlines=8, width=100, callback=self.lbcb)

    def lbcb(self, lb):  # sort
        directory = "".join((root, "/", lb.textvalue()))
        songs = [x[0] for x in os.ilistdir(directory) if x[1] != 0x4000]
        songs.sort()
        SelectScreen.songs = ["".join((directory, "/", x)) for x in songs]
        SelectScreen.album = lb.textvalue()
        Screen.back()


class BaseScreen(Screen):
    def __init__(self):

        args = {
            "bdcolor": RED,
            "slotcolor": BLUE,
            "legends": ("-48dB", "-24dB", "0dB"),
            "value": 0.5,
            "height": 15,
        }
        buttons = {
            "shape": CIRCLE,
            "fgcolor": GREEN,
        }
        super().__init__()
        self.mt = asyncio.ThreadSafeFlag()
        audio_out.irq(self.audiocb)
        # Audio status
        self.playing = False  # Track is playing
        self.stop_play = False  # Command
        self.paused = False
        self.songs = []  # Paths to songs in album
        self.song_idx = 0  # Current index into .songs
        self.offset = 0  # Offset into file
        self.volume = -3

        wri = CWriter(ssd, arial10, GREEN, BLACK, False)
        wri_icons = CWriter(ssd, icons, WHITE, BLACK, False)
        Button(wri_icons, 2, 2, text="E", callback=self.new, args=(wri,), **buttons)  # New
        Button(wri_icons, row := 30, col := 2, text="D", callback=self.replay, **buttons)  # Replay
        Button(wri_icons, row, col := col + 25, text="F", callback=self.play_cb, **buttons)  # Play
        Button(wri_icons, row, col := col + 25, text="B", callback=self.pause, **buttons)  # Pause
        Button(wri_icons, row, col := col + 25, text="A", callback=self.stop, **buttons)  # Stop
        Button(wri_icons, row, col + 25, text="C", callback=self.skip, **buttons)  # Skip
        row = 60
        col = 2
        self.lbl = Label(wri, row, col, 120)
        self.lblsong = Label(wri, self.lbl.mrow + 2, col, 120)
        row = 110
        col = 14
        HorizSlider(wri, row, col, callback=self.slider_cb, **args)
        CloseButton(wri)  # Quit the application

    def audiocb(self, i2s):  # Audio buffer empty
        self.mt.set()

    def slider_cb(self, s):
        self.volume = round(8 * (s.value() - 1))

    def play_cb(self, _):
        self.play_album()

    def pause(self, _):
        self.stop_play = True
        self.paused = True
        self.show_song()

    def stop(self, _):  # Abandon album
        self.stop_play = True
        self.paused = False
        self.song_idx = 0
        self.show_song()

    def replay(self, _):
        if self.stop_play:
            self.song_idx = max(0, self.song_idx - 1)
        else:
            self.stop_play = True  # Replay from start
        self.paused = False
        self.show_song()
        # self.play_album()

    def skip(self, _):
        self.stop_play = True
        self.paused = False
        self.song_idx = min(self.song_idx + 1, len(self.songs) - 1)
        self.show_song()
        # self.play_album()

    def new(self, _, wri):
        self.stop_play = True
        self.paused = False
        Screen.change(
            SelectScreen,
            args=[
                wri,
            ],
        )

    def play_album(self):
        if not self.playing:
            self.reg_task(asyncio.create_task(self.album_task()))

    def after_open(self):
        self.songs = SelectScreen.songs
        self.lbl.value(SelectScreen.album)
        if self.songs:
            self.song_idx = 0  # Start on track 0
            self.show_song()
            # self.play_album()

    def show_song(self):  # 13ms
        song = self.songs[self.song_idx]
        ns = song.find(SelectScreen.album)
        ne = song[ns:].find("/") + 1
        end = song[ns + ne :].find(".wav")
        self.lblsong.value(song[ns + ne : ns + ne + end])

    async def album_task(self):
        self.playing = True  # Prevent other instances
        self.stop_play = False
        # Leave paused status unchanged
        songs = self.songs[self.song_idx :]  # Start from current index
        for song in songs:
            self.show_song()
            await self.play_song(song)
            if self.stop_play:
                break  # A callback has stopped playback
            self.song_idx += 1
        else:
            self.song_idx = 0  # Played to completion.
            self.show_song()
        self.playing = False

    # Open and play a binary wav file
    async def play_song(self, song):
        wav_samples_mv = memoryview(wav_samples)
        size = len(wav_samples)
        if not self.paused:
            # advance to first byte of Data section in WAV file. This is not
            # correct for all WAV files. See link above.
            self.offset = 44
        with open(song, "rb") as wav:
            _ = wav.seek(self.offset)
            while not self.stop_play:
                async with Screen.rfsh_lock:  # Lock out refresh
                    for n in range(_RFSH_GATE):  # for _RFSH_GATE buffers full
                        if not (num_read := wav.readinto(wav_samples_mv)):  # Song end
                            return
                        I2S.shift(buf=wav_samples_mv[:num_read], bits=16, shift=self.volume)
                        audio_out.write(wav_samples_mv[:num_read])
                        await self.mt.wait()
                        # wav_samples is now empty. Save offset in case we pause play.
                        self.offset += size
                await asyncio.sleep_ms(0)  # Allow refresh to grab lock


def test():
    print("Audio demo.")
    try:
        Screen.change(BaseScreen)  # A class is passed here, not an instance.
    finally:
        audio_out.deinit()
        print("==========  CLOSE AUDIO ==========")


test()
