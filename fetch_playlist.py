import re
import time
import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
BASE_URL = "http://redforce.live:8082/"
PLAYER_BASE = "http://redforce.live/player.php?stream="
PLAYLIST_FILENAME = "playlist.m3u"
MAX_WORKERS = 3

CHANNELS = [
    {"id": "1", "name": "T SPORTS", "group": "Sports"},
    {"id": "80", "name": "ATN BANGLA HD", "group": "Bangla"},
    {"id": "88", "name": "A SPORTS HD", "group": "Sports"},
    {"id": "95", "name": "ATN NEWS", "group": "Bangla"},
    {"id": "7", "name": "ZEE TV HD", "group": "Hindi"},
    {"id": "53", "name": "ZING", "group": "Hindi"},
    {"id": "42", "name": "ZOOM", "group": "Hindi"}
]

def get_stream(channel):
    driver = None
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # GitHub Actions এ ড্রাইভার সেটআপ
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        driver.get(f"{PLAYER_BASE}{channel['id']}")
        time.sleep(8) # পেজ লোড হওয়ার জন্য সময়
        
        page_source = driver.page_source
        # টোকেন খোঁজার রিজেক্স (Regex)
        match = re.search(r'token=([a-zA-Z0-9\-_.]+)', page_source)
        
        if match:
            token = match.group(1)
            # রেডফোর্স এর m3u8 ফরম্যাট
            url = f"{BASE_URL}{channel['name'].replace(' ', '.')}/index.m3u8?token={token}&remote=no_check_ip"
            print(f"✅ Extracted: {channel['name']}")
            return f'#EXTINF:-1 tvg-name="{channel["name"]}" group-title="{channel["group"]}",{channel["name"]}\n{url}'
        
        print(f"⚠️ No token for: {channel['name']}")
        return None
    except Exception as e:
        print(f"❌ Error on {channel['name']}: {e}")
        return None
    finally:
        if driver: driver.quit()

def main():
    print(f"🚀 Starting RedForce Fetcher for {len(CHANNELS)} channels...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(get_stream, CHANNELS))
    
    playlist_entries = [r for r in results if r]
    
    # এরর এড়াতে সবসময় একটি ফাইল তৈরি করা নিশ্চিত করা হচ্ছে
    updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"#EXTM3U\n# Last Updated: {updated_at}\n"
    
    if playlist_entries:
        final_content = header + "\n".join(playlist_entries)
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write(final_content)
        print(f"🎉 Success! {len(playlist_entries)} channels saved to {PLAYLIST_FILENAME}.")
    else:
        # কোনো চ্যানেল না পেলেও ফাইল তৈরি হবে যাতে Git Action ফেইল না করে
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write(header + "# No channels were fetched successfully.")
        print("🛑 No tokens found, but placeholder file created.")

if __name__ == "__main__":
    main()
