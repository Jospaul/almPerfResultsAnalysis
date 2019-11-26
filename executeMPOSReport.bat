@echo off
REM Author: Jospaul Mahajan Prakash
REM Company: Infosys Limited

set ALMUSERNAME=jprakash
set ALMPASSWORD=123[Infosys

REM Takes "file" for file only output, "teams" for teams only output and "tf" for both
set OUTPUTTYPE=tf

REM Takes a run id if results of a specific run id has to be computed
set RUNID=1941

cmd /c "cmdkey /add:enttools201 /user:%ALMUSERNAME% /pass:%ALMPASSWORD%"

cmd /c "cmdkey /add:len-file /user:%ALMUSERNAME% /pass:%ALMPASSWORD%"

python .\almPerfResultsAnalysis\__main__.py -u %ALMUSERNAME% -p %ALMPASSWORD% -o %OUTPUTTYPE%

cmd /c "cmdkey /delete:len-file

cmd /c "cmdkey /delete:enttools201"