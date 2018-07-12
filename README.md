# Intro
*"Terrain"* is 2D landscape deformation prototype written in *Python*. This prototype allows user to deform 2D terrain by cutting holes in it. Terrain mesh is being rebuilt after each deformation by removing old and adding new triangles.

# Downloads
 * Windows EXE - https://github.com/afomins/terrain/releases/download/v0.1.0/terrain-v0.1.0.exe
 * Linux BIN - https://github.com/afomins/terrain/releases/download/v0.1.0/terrain-v0.1.0-linux
 
# How it looks
|  Cutting random holes  | Cutting Mickey Mouse shape |
| --|--|
| <img src="https://github.com/afomins/terrain/blob/master/gifs/terrain_000.gif" width="300"> | <img src="https://github.com/afomins/terrain/blob/master/gifs/terrain_001.gif" width="300"> |

# Bild instructions
 * Install `Python2`
 * Clone `git@github.com:afomins/terrain.git`
 * Install `PyQt4` for `python2`:
   * For **Windows** - run `pip install PyQt4-4.11.4-cp27-cp27m-win_amd64.whl` from [`PyQt4` directory](https://github.com/afomins/terrain/tree/master/PyQt4)
   * For **Linux** and **Cygwin** - install `PyQt4` package from package repository
 * Run `python2 terrain.py`
