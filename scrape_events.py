import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        print(f"Opening {url}...")
        page.goto(url, wait_until="networkidle")

        page_count = 1
        while True:
            print(f"Scraping page {page_count}...")
            # Wait for events to load
            page.wait_for_selector(".sys_mag-item", timeout=10000)
            
            # Parse the current page content
            soup = BeautifulSoup(page.content(), 'html.parser')
            events = soup.find_all('div', class_='sys_mag-item')
            
            for event in events:
                title = event.find('h3').get_text(strip=True)
                date_text = event.find('p', class_='sys_mag-date').get_text(strip=True)
                all_events_html += f"<div class='event'><strong>{title}</strong><br>{date_text}</div>"

            # Check if there is a 'Next' button
            # Usually, these sites use an 'aria-label' or specific text like 'Next' or '>'
            next_button = page.query_selector("a.sys_pagination-next") # Common class for this site's 'Next'
            
            if next_button and page_count < 5: # Safety limit of 5 pages so it doesn't run forever
                print("Moving to next page...")
                next_button.click()
                page.wait_for_load_state("networkidle")
                page_count += 1
            else:
                print("No more pages or limit reached.")
                break
        
        browser.close()

    # Wrap the collected events in HTML
    today_str = datetime.now().strftime("%d %B %Y")
    final_html = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; background: #f4f7f6; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .event {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
            .event:last-child {{ border-bottom: none; }}
            h1 {{ color: #d32f2f; border-bottom: 2px solid #d32f2f; padding-bottom: 10px; }}
            .date {{ color: #666; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Family Events in Surrey</h1>
            <p><strong>Date:</strong> {today_str}</p>
            {all_events_html if all_events_html else "<p>No events found today.</p>"}
            <p style="margin-top:20px;"><small>Data updated: {datetime.now().strftime('%H:%M')}</small></p>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
