echo off
for %%f in (*.mp3) do (
	rem echo a[%%~nf]
	rem echo b[%%~f]
	echo [%%~ff]
	aacgain /r /k /d 3 "%%~ff"
)