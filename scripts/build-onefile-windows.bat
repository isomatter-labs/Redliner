pyinstaller ^
--noconfirm ^
--windowed ^
--onefile ^
--clean ^
--exclude-module pyqt5 ^
--exclude-module numba ^
--exclude-module matplotlib ^
--exclude-module scipy ^
--exclude-module PySide2 ^
--splash "./res/splash.png" ^
--paths "./" ^
--add-data "./res/*;res" ^
--add-data "./CHANGELOG.md;." ^
--icon "./res/icon.ico" ^
--distpath "./dist/onefile" ^
--workpath "./build" ^
--name "redliner" ^
.\redliner\main.py
