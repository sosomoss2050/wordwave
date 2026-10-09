@echo off
rem Make a signed WordWave.zxp for distribution (Windows). Needs ZXPSignCmd.exe (Adobe CEP-Resources, "ZXPSignCMD")
rem next to this file or on PATH. The self-signed certificate is created once (wordwave_cert.p12) and reused.
cd /d "%~dp0"
set "Z=ZXPSignCmd.exe"
if "%WORDWAVE_CERT_PASS%"=="" set "WORDWAVE_CERT_PASS=change-this-password"
if not exist wordwave_cert.p12 %Z% -selfSignedCert JP Tokyo hakoniwa WordWave %WORDWAVE_CERT_PASS% wordwave_cert.p12
if exist WordWave.zxp del WordWave.zxp
%Z% -sign com.852wa.jizura WordWave.zxp wordwave_cert.p12 %WORDWAVE_CERT_PASS% -tsa http://timestamp.digicert.com
%Z% -verify WordWave.zxp
echo WordWave.zxp ready
pause
