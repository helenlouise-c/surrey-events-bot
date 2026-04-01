import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def is_event_today(date_text):
    """
    Checks if 'today' falls within the provided date text.
    Handles 'April 1, 2026' and ranges like 'Mar 30, 2026 - Apr 2, 2026'
    """
    now = datetime.now()
    # Looking for 'April 1' or '1 April' or 'Apr 1'
    today_check_1 = now.strftime("%B %-d") # April 1
    today_check_2 = now.strftime("%-d %B") # 1 April
    today_check_3 = now.strftime("%b %-d") # Apr 1
    
    dt_str = date_text.lower()
    
    # If today's month and day appear in the text, it's a match!
    if (today_check_1.lower() in dt_str or 
        today_check_2.lower() in dt_str or 
        today_check_3.lower() in dt_str or
        "today" in dt_str):
        return True
    return False

def scrape_surrey_events():
    all_events_html = ""
    print(f"Scraping for: {datetime.now().strftime('%B %-d, %Y')}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            page_num = 1
            while page_num <= 15: # Check plenty of pages
                page.wait_for_selector(".sys_mag-item", timeout=15000)
                soup = BeautifulSoup(page.content(), 'html.parser')
                events = soup.find_all('div', class_='sys_mag-item')
                
                print(f"Page {page_num}: Scanning {len(events)} events...")
                
                for event in events:
                    title_el = event.find(['h3', 'a'])
                    date_el = event.find('p', class_='sys_mag-date')
                    
                    if title_el and date_el:
                        title = title_el.get_text(strip=True)
                        date_text = date_el.get_text(strip=True)
                        
                        if is_event_today(date_text):
                            print(f"🎯 FOUND: {title}")
                            link = event.find('a')['href'] if event.find('a') else "#"
                            if not link.startswith('http'):
                                link = "https://www.visitsurrey.com" + link
                            
                            all_events_html += f"""
                            <div class='event'>
                                <a href='{link}' target='_blank'>{title}</a>
                                <span class='date'>📅 {date_text}</span>
                            </div>
                            """

                next_button = page.locator("a.sys_pagination-next")
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(3000)
                    page_num += 1
                else:
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    # The rest of the HTML generation remains similar...
    final_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Surrey Events Today</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #f4f4f9; color: #333; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            h1 {{ color: #2e7d32; border-bottom: 3px solid #81c784; padding-bottom: 10px; }}
            .event {{ border-left: 5px solid #4caf50; background: #f9fff9; margin-bottom: 15px; padding: 15px; }}
            .event a {{ color: #1b5e20; text-decoration: none; font-size: 1.2em; font-weight: bold; }}
            .date {{ display: block; color: #666; margin-top: 5px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>What's on in Surrey Today</h1>
            <p>Date: {datetime.now().strftime('%A, %B %-d, %Y')}</p>
            {all_events_html if all_events_html else "<p>No events matching today's date found yet. Check back later!</p>"}
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
