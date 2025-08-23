from googleapiclient.discovery import build
from tqdm import tqdm
import requests
import re
import sys
import os

pc = re.compile(r'"canonicalBaseUrl":"\/(.*?)"')

def app():
    if len(sys.argv) == 1:
        print("This program needs a YouTube API key as a parameter!")
        exit(1)
    DEVELOPER_KEY = sys.argv[1]
    youtube = build('youtube', 'v3', developerKey=DEVELOPER_KEY)
    handles = {}
    for file in tqdm(os.listdir()):
        try:
            if os.path.isdir(file):
                continue
            id = file.split("[")[-1].split("]")[0]
            e = requests.head("https://www.youtube.com/shorts/" + id)
            short = False
            if e.status_code == 200:
                short = True
            request = youtube.videos().list(part='snippet', id=id)
            details = request.execute()
            chanid = details["items"][0]["snippet"]["channelId"]
            if chanid not in handles:
                handle = re.search(pc, requests.get("https://www.youtube.com/channel/" + chanid).text).group(1)
                handles[chanid] = handle
            else:
                handle = handles[chanid]
            folder = details["items"][0]["snippet"]["channelTitle"] + " (" + handle + ")"
            if not os.path.isdir(folder):
                os.mkdir(folder)
            if short and not os.path.isdir(folder + "/Shorts"):
                os.mkdir(folder + "/Shorts")
            os.rename(file, folder + ("/Shorts" if short else "") + "/" + file)
        except Exception:
            continue
