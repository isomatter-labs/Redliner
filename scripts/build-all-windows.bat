rmdir /s /q ..\dist
rmdir /s /q ..\build
del redliner.spec
call scripts/build-onefile-windows.bat
call scripts/build-debug-windows.bat
call scripts/build-onedirectory-windows.bat
