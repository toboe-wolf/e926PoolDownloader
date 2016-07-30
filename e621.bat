REM   edit e621.bat, and on the line "set POOL_ID_LIST" put the id # of each pool inside the parenthesis, seperated by a space
REM   EXAMPLE: set POOL_ID_LIST=(1188 803 1819 1274)
set POOL_ID_LIST=()












for %%i in %POOL_ID_LIST% do .\pool.py %%i --folder=.\output_pools\ --corrupt_retries=3 --name=${pos}_${id}_${rating}

PAUSE