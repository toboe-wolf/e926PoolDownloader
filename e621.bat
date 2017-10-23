@echo off
REM   edit e621.bat, and on the line "set POOL_ID_LIST" put the id # of each pool inside the parenthesis, seperated by a space
REM   EXAMPLE: set POOL_ID_LIST=(10466 803 1819 1274 1188)
set POOL_ID_LIST=(10466)









echo.
echo Please note that the e621 downloader was only written and tested with python 2.7.  If you are running the e621 downloader using python 3+, you may experience bugs or failure.
PAUSE
for %%i in %POOL_ID_LIST% do .\pool.py %%i --folder=.\output_pools\ --corrupt_retries=5 --name=${name}_${pos}
PAUSE
