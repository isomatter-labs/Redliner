pyinstaller ^
--noconfirm ^
--windowed ^
--clean ^
--exclude-module pyqt5 ^
--exclude-module numba ^
--exclude-module matplotlib ^
--exclude-module scipy ^
--exclude-module PySide2 ^
--splash "../res/splash.png" ^
--icon "../res/icon.ico" ^
--distpath "../dist/onedirectory" ^
--add-data "../res/*;res" ^
--add-data "../CHANGELOG.md;CHANGELOG.md" ^
--add-data "../res/icons/*;res/icons" ^
--workpath "../build" ^
--name "redliner" ^
..\redliner\redliner.py