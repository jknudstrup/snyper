# Appendix 2 Freezing bytecode

This achieves a major saving of RAM. The correct way to do this is via a
[manifest file](http://docs.micropython.org/en/latest/reference/manifest.html).
The first step is to clone MicroPython and prove that you can build and deploy
firmware to the chosen platform. Build instructions vary between ports and can
be found in the MicroPython source tree in `ports/<port>/README.md`.

The following is an example of how the entire
GUI with fonts, demos and all widgets can be frozen on RP2.

Build script:
```bash
cd /mnt/qnap2/data/Projects/MicroPython/micropython/ports/rp2
MANIFEST='/mnt/qnap2/Scripts/manifests/rp2_manifest.py'

make submodules
make clean
if make -j 8 BOARD=PICO FROZEN_MANIFEST=$MANIFEST
then
    echo Firmware is in build-PICO/firmware.uf2
else
    echo Build failure
fi
cd -
```
Manifest file contents (first line ensures that the default files are frozen):
```python
include("$(MPY_DIR)/ports/rp2/boards/manifest.py")
freeze('/mnt/qnap2/Scripts/modules/rp2_modules')
```
The directory `/mnt/qnap2/Scripts/modules/rp2_modules` contains only a symlink
to the `gui` directory of the `micropython-micro-gui` source tree. The freezing
process follows symlinks and respects directory structures.

It is usually best to keep `hardware_setup.py` unfrozen for ease of making
changes. I also keep the display driver and `boolpalette.py` in the filesystem
as I have experienced problems freezing display drivers - but feel free to
experiment.