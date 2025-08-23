. .\env.ps1 #set environment variables.. 
Remove-Item -Path ".\dist" -Recurse
uv version --bump patch
uv build
uv publish 