import os
import json
import time
import feedparser
from playwright.sync_api import sync_playwright

# Setup RSS feed URL
RSS_FEED_URL = "https://www.fullofwishes.co.uk/feed/"

def get_latest_post():
    feed = feedparser.parse(RSS_FEED_URL)
    if not feed.entries:
        return None
    latest_entry = feed.entries[0]
    return f"New post: {latest_entry.title}\n{latest_entry.link}"

def post_to_x(tweet_text):
    # Fetch cookies from GitHub environment variables
    cookies_json = os.environ.get("X_COOKIES")
    if not cookies_json:
        print("Error: X_COOKIES secret not found.")
        return

    cookies = json.loads(cookies_json)

    with sync_playwright() as p:
        # Launch Chromium with a realistic desktop user agent
        browser = p.chromium.launch(headless=True)
        
        # Open a browser context and inject our saved login cookies
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        # Navigate directly to the X compose page
        print("Navigating to X...")
        page.goto("https://x.com")
        page.wait_for_timeout(5000) # Give the page time to process cookies and load
        
        # Fallback check to ensure we aren't stuck on a login wall
        if "login" in page.url:
            print("Failed to authenticate using cookies. Session might be expired.")
            browser.close()
            return

        try:
            # Click the post box (using X's draft editor selector)
            print("Locating text box...")
            post_box = page.locator('div[data-testid="tweetTextarea_0"]')
            post_box.click()
            
            # Type the content dynamically like a real user
            print("Typing post content...")
            post_box.fill(tweet_text)
            page.wait_for_timeout(1000)
            
            # Locate and click the blue "Post" button
            print("Clicking the post button...")
            post_button = page.locator('button[data-testid="tweetButtonInline"]')
            post_button.click()
            
            # Give the network time to send the post before closing the browser
            page.wait_for_timeout(4000)
            print("Automation finished successfully!")
            
        except Exception as e:
            print(f"An error occurred during browser execution: {e}")
            # Optional: page.screenshot(path="error.png") to help debug failures
            
        browser.close()

if __name__ == "__main__":
    content = get_latest_post()
    if content:
        post_to_x(content)
    else:
        print("No new updates found in the RSS feed.")

