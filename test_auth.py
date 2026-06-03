import os
import json
import time
from playwright.sync_api import sync_playwright

def test_login():
    # Fetch cookies from environment variable
    cookies_json = os.environ.get("X_COOKIES")
    if not cookies_json:
        print("❌ Error: X_COOKIES environment variable is empty!")
        return

    try:
        cookies = json.loads(cookies_json)
    except Exception as e:
        print(f"❌ Error parsing JSON formatting: {e}")
        return

    with sync_playwright() as p:
        # Launch browser (set headless=False if running locally to watch it work)
        browser = p.chromium.launch(headless=True)
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        print("🔄 Navigating to X Home...")
        page.goto("https://x.com")
        page.wait_for_timeout(7000)  # Wait for feed elements to populate
        
        current_url = page.url
        print(f"📍 Current URL: {current_url}")
        
        # Save a visual capture to inspect the state
        page.screenshot(path="x_test_capture.png")
        print("📸 Screenshot saved as 'x_test_capture.png'")
        
        if "login" in current_url or "i/flow/login" in current_url:
            print("❌ Authentication failed. X redirected you to the login screen.")
        else:
            print("✅ Success! Your cookies successfully bypassed the login wall.")
            
        browser.close()

if __name__ == "__main__":
    test_login()

