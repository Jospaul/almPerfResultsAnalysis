@echo off
REM Author: Jospaul Mahajan Prakash
REM Company: Infosys Limited

set ALMUSERNAME=jprakash
set ALMPASSWORD=Infosys?123

REM Takes "file" for file only output, "teams" for teams only output and "tf" for both
set OUTPUTTYPE=tf

REM Takes a run id if results of a specific run id has to be computed
set RUNID=1941

python .\almPerfResultsAnalysis\__main__.py -u %ALMUSERNAME% -p %ALMPASSWORD% -o %OUTPUTTYPE%