@echo off
REM trigger server restart

cmd /c "cmdkey /add:entlr005 /user:jprakash /pass:123[Infosys"

C:\pstools\PsExec.exe -accepteula \\entlr005 -u "jcp\jprakash" -p "Infosys?123" cmd /c "C:\Users\jprakash\Documents\cleanup_prep.bat"

cmd /c "cmdkey /delete:entlr005"

:exit