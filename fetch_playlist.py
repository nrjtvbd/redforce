import re
import datetime
import requests
import time

# --- Configuration ---
# সরাসরি কানেকশন ফেইল করলে আমরা এই প্রক্সিগুলো ব্যবহার করব
PROXIES = [
    "https://api.allorigins.win/get?url=", # CORS Proxy
    "https://api.codetabs.com/v1/proxy?quest=" # Alternative Proxy
]

BASE_URL = "http://redforce.live:8082"
PLAYER_URL = "http://redforce.live/player.php?stream="
PLAYLIST_FILENAME = "playlist.m3u"

CHANNELS = [
    {"id": "1", "name": "T.SPORTS", "group": "Sports"},
    {"id": "80", "name": "ATN.BANGLA.HD", "group": "Bangla"},
    {"id": "88", "name": "A.SPORTS.HD", "group": "Sports"},
    {"id": "95", "name": "ATN.NEWS", "group": "Bangla"},
    {"id": "7", "name": "ZEE.TV.HD", "group": "Hindi"},
    {"id": "53", "name": "ZING", "group": "Hindi"},
    {"id": "42", "name": "ZOOM", "group": "Hindi"}
]

def get_token(ch_id):
    target_url = f"{PLAYER_URL}{ch_id}"
    
    # প্রথমে প্রক্সি দিয়ে চেষ্টা করা (গিটহাব আইপি হাইড করার জন্য)
    for proxy in PROXIES:
        try:
            print(f"📡 Trying via Proxy for ID {ch_id}...")
            # Allorigins এর জন্য বিশেষ ফরম্যাট
            if "allorigins" in proxy:
                response = requests.get(f"{proxy}{target_url}", timeout=20)
                html = response.json().get('contents', '')
            else:
                response = requests.get(f"{proxy}{target_url}", timeout=20)
                html = response.text

            token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', html)
            if token_match:
                return token_match.group(1)
        except:
            continue
    return None

def main():
    print(f"🚀 Starting RedForce Bypass Fetcher...")
    playlist_entries = []
    
    for ch in CHANNELS:
        print(f"🔍 Processing: {ch['name']}...")
        token = get_token(ch['id'])
        
        if token:
            stream_url = f"{BASE_URL}/{ch['name']}/index.m3u8?token={token}&remote=no_check_ip"
            playlist_entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Token Found!")
        else:
            print(f"❌ Failed.")
        time.sleep(2)

    # ফাইল সেভ করা
    updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"#EXTM3U\n# Last Updated: {updated_at}\n"
    
    with open(PLAYLIST_FILENAME, "w") as f:
        if playlist_entries:
            f.write(header + "\n".join(playlist_entries))
            print(f"🎉 Success! {len(playlist_entries)} channels updated.")
        else:
            f.write(header + "# Fetching failed due to IP blocking.")
            print("🛑 No channels fetched.")

if __name__ == "__main__":
    main()
