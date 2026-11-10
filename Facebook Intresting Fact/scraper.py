import os
import json
import random
import requests
import time
import traceback
from playwright.sync_api import sync_playwright

def send_telegram_error(error_msg):
    """Telegram par error message bhejne ka function Thread ID 8 me"""
    token = os.environ.get("TELEGRAM_FAILD_TOKEN")
    chat_id = os.environ.get("TELEGRAM_FAILD_ID")
    repo_name = os.environ.get("GITHUB_REPOSITORY", "Unknown Repo")
    folder_name = "Facebook Intresting Fact"
    thread_id = "8"

    # Message limit to avoid Telegram API error on huge tracebacks
    safe_error = str(error_msg)[:800] 
    
    text = f"🚨 **Automation Failed!**\n\n**Repo:** `{repo_name}`\n**Folder:** `{folder_name}`\n**Error:**\n`{safe_error}`"
    
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "message_thread_id": thread_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print("Failed to send Telegram alert:", e)
    else:
        print("Telegram tokens not found in environment!")

def get_random_untracked_link():
    """link.txt se ek naya random link nikalna jo track.json me na ho"""
    if not os.path.exists("link.txt"):
        raise FileNotFoundError("link.txt file nahi mili!")
        
    with open("link.txt", "r") as f:
        all_links = [line.strip() for line in f if line.strip()]
        
    tracked = []
    if os.path.exists("track.json"):
        try:
            with open("track.json", "r") as f:
                tracked = json.load(f)
        except:
            tracked = []

    available_links = [link for link in all_links if link not in tracked]
    
    if not available_links:
        raise ValueError("link.txt me koi naya link bacha hi nahi hai! Sab download ho chuke hain.")
        
    return random.choice(available_links), tracked

def download_instagram_video(ig_url, output_filename="video_to_upload.mp4"):
    # Aapki di hui nayi list + Puraani fallback list combine ki gayi hai
    websites_list = [
        "https://downsnap.in/v", "https://snapscooper.app/", "https://instagramfetch.com/",
        "https://snapinsta.to/", "https://igram.io/", "https://downloadgram.org/",
        "https://indown.io/", "https://saveig.app/", "https://instasaved.net/",
        "https://instadownloader.co/", "https://instavideosave.net/", "https://reelsvideo.io/",
        "https://reelsaver.net/", "https://igram.world/", "https://igram.site/",
        "https://igram.pk/", "https://fastdl.app/", "https://snapinsta.app/",
        "https://snapinsta.ai/", "https://saveinsta.dev/", "https://downig.com/",
        "https://inflact.com/", "https://savefrom.net/", "https://9xbuddy.com/",
        "https://cobalt.tools/", "https://amoyshare.com/", "https://pastedownload.com/",
        "https://smallseotools.com/", "https://duplichecker.com/", "https://acethinker.com/",
        "https://igdl.net/", "https://savereel.online/", "https://www.ilovereels.site/",
        "https://reelsdownloader.tools/", "https://getreelsdownloader.com/", "https://xadownloader.com/",
        "https://www.instatubehd.online/", "https://snapdownloader.net/instagram"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for site_url in websites_list:
            print(f"\n[+] Trying website: {site_url}")
            page = context.new_page()
            
            try:
                page.goto(site_url, timeout=20000)
                page.wait_for_load_state("domcontentloaded")

                # Smart Locator for Input
                input_locator = page.locator("input[type='url'], input[name*='url'], input[name*='q'], input[id*='url'], input[id*='link'], input[placeholder*='Instagram']").first
                input_locator.wait_for(state="visible", timeout=8000)
                input_locator.fill(ig_url)
                time.sleep(1) 

                # Smart Locator for Submit Button
                submit_locator = page.locator("button[type='submit'], button[id*='submit'], button[class*='btn'], button:has-text('Download'), button:has-text('Get')").first
                submit_locator.click()

                print("    Waiting for extraction...")
                # Smart Locator for MP4 Download Link
                download_locator = page.locator("a[href*='.mp4'], a[href*='cdninstagram.com'], a[download], a:has-text('Download Video'), a:has-text('Download MP4')").first
                download_locator.wait_for(state="attached", timeout=15000)
                
                mp4_url = download_locator.get_attribute('href')

                if mp4_url and ('http' in mp4_url):
                    print(f"    [SUCCESS] Found MP4 Link!")
                    response = requests.get(mp4_url, stream=True)
                    if response.status_code == 200:
                        with open(output_filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=1024):
                                f.write(chunk)
                        page.close()
                        browser.close()
                        return True
            except Exception as e:
                print(f"    [FAILED] Skipping {site_url}...")
            finally:
                page.close()

        browser.close()
        raise Exception("Saari 40+ websites fail ho gayin ya link private hai!")

if __name__ == "__main__":
    try:
        # 1. Random untracked link nikalo
        target_link, tracked_list = get_random_untracked_link()
        print(f"Processing Link: {target_link}")

        # 2. Video download karo
        success = download_instagram_video(target_link, "video_to_upload.mp4")

        # 3. Agar download successful hai, toh link ko track.json me save kar do
        if success:
            tracked_list.append(target_link)
            with open("track.json", "w") as f:
                json.dump(tracked_list, f, indent=4)
            print("Track.json updated successfully!")

    except Exception as e:
        error_trace = traceback.format_exc()
        print("Script failed:", error_trace)
        send_telegram_error(error_trace)
        exit(1) # Action ko fail mark karne ke liye
