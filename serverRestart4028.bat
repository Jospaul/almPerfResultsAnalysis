@echo off
REM trigger server restart

cmd /c "cmdkey /add:entlr005 /user:jprakash /pass:Infosys_123"

C:\pstools\PsExec.exe \\entlr005 cmd /c "C:\Users\jprakash\Documents\cleanup_prep.bat"

cmd /c "cmdkey /delete:entlr005"

:exit