import os
import sys
import json
import feedparser
from playwright.sync_api import sync_playwright
from datetime import date
from pathlib import Path

HISTORY_FILE = "tweeted_history.txt"
today = date.today()
# Format the date as YYYYMMDD
formatted_date = today.strftime("%Y%m%d")
url_querystring = "?utm_source=social&utm_medium=twitter&utm_campaign=ahfowpost+" + formatted_date

def get_latest_post(feed_url):
    print(f"Parsing feed: {feed_url}")
    feed = feedparser.parse(feed_url)
    if not feed.entries:
        return None, None
    
    latest_entry = feed.entries[0]
    tweet_text = f"New post: {latest_entry.title}\n{latest_entry.link}{url_querystring}"
    return tweet_text, latest_entry.link

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def save_to_history(url):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{url}\n")

def post_to_x(tweet_text):
    cookies_json = os.environ.get("X_COOKIES")
    if cookies_json:
        cookies = json.loads(cookies_json)
    else:
        local_cookie_path = Path.home() / ".config" / "ahfow-poster" / "x_cookies.json"
        print(f"{local_cookie_path}")
        if local_cookie_path.exists():
            with open(local_cookie_path, "r") as f:
                cookies = json.load(f)
        else:
            print("Error: X_COOKIES secret not found.")
            return False


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        page = context.new_page()
        
        page.goto("https://x.com")
        page.wait_for_timeout(5000)
        
        if "login" in page.url:
            print("Failed to authenticate using cookies.")
            browser.close()
            return False

        try:
            post_box = page.locator('div[data-testid="tweetTextarea_0"]')
            post_box.click()
            post_box.fill(tweet_text)
            page.wait_for_timeout(1000)
            
            post_button = page.locator('button[data-testid="tweetButtonInline"]')
            post_button.click()
            page.wait_for_timeout(4000)
            print("Tweet posted successfully!")
            browser.close()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            browser.close()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No RSS feed URL provided.")
        sys.exit(1)
        
    target_feed_url = sys.argv[1]
    content, post_url = get_latest_post(target_feed_url)
    
    if not content:
        print("No items found in this feed.")
        sys.exit(0)
        
    # Check history log
    history = load_history()
    if post_url in history:
        print(f"Skipping: {post_url} has already been tweeted.")
        sys.exit(0)
        
    # Attempt to post
    success = post_to_x(content)
    if success:
        save_to_history(post_url)

