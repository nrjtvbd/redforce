import re
import time
import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Configuration ---
BASE_URL = "http://redforce.live:8082/"
PLAYER_BASE = "http://redforce.live/player.php?stream="
PLAYLIST_FILENAME = "playlist.m3u"
MAX_WORKERS = 4 

# redforcetv.txt থেকে সংগৃহীত আইডি সমূহ
CHANNELS = [
    {"id": "1", "name": "T SPORTS", "group": "Sports"},
    {"id": "80", "name": "ATN BANGLA HD", "group": "Bangla"},
    {"id": "88", "name": "A SPORTS HD", "group": "Sports"},
    {"id": "95", "name": "ATN NEWS", "group": "Bangla"},
    {"id": "7", "name": "ZEE TV HD", "group": "Hindi"},
    {"id": "53", "name": "ZING", "group": "Hindi"},
    {"id": "42", "name": "ZOOM", "group": "Hindi"},
    {"id": "26", "name": "ANIMAL PLANET HD", "group": "English"}
]

def get_stream(channel):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        
        driver.get(f"{PLAYER_BASE}{channel['id']}")
        time.sleep(5)
        
        # সোর্স থেকে টোকেন খোঁজা
        match = re.search(r'token=([a-zA-Z0-9\-_.]+)', driver.page_source)
        if match:
            token = match.group(1)
            # redforce এর index.m3u8 ফরম্যাট
            url = f"{BASE_URL}{channel['name'].replace(' ', '.')}/index.m3u8?token={token}&remote=no_check_ip"
            return f'#EXTINF:-1 tvg-name="{channel["name"]}" group-title="{channel["group"]}",{channel["name"]}\n{url}'
    except:
        return None
    finally:
        if driver: driver.quit()

def main():
    print(f"🚀 Starting RedForce Fetcher...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(get_stream, CHANNELS))
    
    entries = [r for r in results if r]
    if entries:
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write("#EXTM3U\n" + "\n".join(entries))
        print(f"✅ Done! {len(entries)} channels saved.")

if __name__ == "__main__":
    main()
