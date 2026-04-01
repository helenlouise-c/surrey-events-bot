import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        print(f"Opening {url}...")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            while True:
                # Wait for the event list to be ready
                page.wait_for_selector(".sys_mag-item", timeout=15000)
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                events = soup.find_all('div', class_='sys_mag-item')
                
                print(f"Found {len(events)} events on this page.")
                
                for event in events:
                    title_el = event.find('h3')
                    date_el = event.find('p', class_='sys_mag-date')
                    if title_el and date_el:
                        title = title_el.get_text(strip=True)
                        date_text = date_el.get_text(strip=True)
                        all_events_html += f"<div class='event'><strong>{title}</strong><br><span class='date'>{date_text}</span></div>"

                # Look for the right-arrow (Next) button
                next_button = page.locator("a.sys_pagination-next")
                
                # Check if it exists AND is actually clickable (not the end of the list)
                if next_button.is_visible() and next_button.is_enabled():
                    print("Clicking to next page...")
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                    # Small sleep to ensure the UI updates
                    page.wait_for_timeout(2000) 
                else:
                    print("Reached the final page.")
                    break
                    
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            browser.close()

    today_str = datetime.now().strftime("%d %B %Y")
    final_html = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f0f2f5; color: #333; }}
            .container {{ max-width: 700px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #2e7d32; border-bottom: 3px solid #2e7d32; padding-bottom: 10px; }}
            .event {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
            .date {{ color: #d32f2f; font-weight: bold; display: block; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Surrey Family Events</h1>
            <p><strong>List generated on:</strong> {today_str}</p>
            {all_events_html if all_events_html else "<p>No events currently listed.</p>"}
            <p style="text-align: center; color: #888; margin-top: 30px;"><small>Automated Scraper v1.0</small></p>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("Success! index.html updated.")

if __name__ == "__main__":
    scrape_surrey_events()
