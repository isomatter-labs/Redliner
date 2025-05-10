pyinstaller ^
--noconfirm ^
--onefile ^
--clean ^
--splash "../res/splash.png" ^
--icon "../res/icon.ico" ^
--distpath "../dist/debug" ^
--add-data "../res/*;res" ^
--add-data "../CHANGELOG.md;CHANGELOG.md" ^
--add-data "../res/icons/*;res/icons" ^
--workpath "../build" ^
--name "redliner" ^
..\redliner\redliner.py