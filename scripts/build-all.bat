rmdir /s /q ..\dist
rmdir /s /q ..\build
del redliner.spec
call build-onefile.bat
call build-onedirectory.bat
call build-debug.bat
