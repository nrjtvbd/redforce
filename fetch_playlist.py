import re
import time
import datetime
import requests

# --- Configuration ---
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
    headers = {
        "Referer": "http://redforce.live/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    try:
        # সরাসরি প্লেয়ার পেজ থেকে ডাটা আনা
        response = requests.get(f"{PLAYER_URL}{ch_id}", headers=headers, timeout=15)
        if response.status_code == 200:
            # সোর্স কোড থেকে টোকেন খুঁজে বের করা
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Connection Error for ID {ch_id}: {e}")
    return None

def main():
    print(f"🚀 Starting RedForce Fetcher (Requests Mode)...")
    playlist_entries = []
    
    for ch in CHANNELS:
        print(f"📡 Fetching: {ch['name']}...")
        token = get_token(ch['id'])
        
        if token:
            # আপনার ইনস্পেক্ট করা URL ফরম্যাট অনুযায়ী
            stream_url = f"{BASE_URL}/{ch['name']}/index.m3u8?token={token}&remote=no_check_ip"
            playlist_entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Token Failed.")
        time.sleep(1) # সার্ভারে চাপ কমাতে সামান্য বিরতি

    updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"#EXTM3U\n# Last Updated: {updated_at}\n"

    with open(PLAYLIST_FILENAME, "w") as f:
        if playlist_entries:
            f.write(header + "\n".join(playlist_entries))
            print(f"🎉 Playlist updated with {len(playlist_entries)} channels.")
        else:
            f.write(header + "# No tokens found.")
            print("🛑 No channels were fetched.")

if __name__ == "__main__":
    main()
