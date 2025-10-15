echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v251\fluent/ntbin/win64/winkill.exe"

start "tell.exe" /B "C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v251\fluent\ntbin\win64\tell.exe" DESKTOP-N4GL6IQ 64763 CLEANUP_EXITING
timeout /t 1
"C:\PROGRA~1\ANSYSI~1\ANSYSS~1\v251\fluent\ntbin\win64\kill.exe" tell.exe
if /i "%LOCALHOST%"=="DESKTOP-N4GL6IQ" (%KILL_CMD% 11896) 
if /i "%LOCALHOST%"=="DESKTOP-N4GL6IQ" (%KILL_CMD% 11352) 
if /i "%LOCALHOST%"=="DESKTOP-N4GL6IQ" (%KILL_CMD% 11440) 
if /i "%LOCALHOST%"=="DESKTOP-N4GL6IQ" (%KILL_CMD% 21940)
del "C:\Users\Soren Poole\OneDrive - University of Virginia\Capstone\ucah\cleanup-fluent-DESKTOP-N4GL6IQ-11440.bat"
