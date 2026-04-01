import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    
    # Create multiple "Today" formats to be safe
    now = datetime.now()
    today_formats = [
        now.strftime("%d %b %Y"),    # 01 Apr 2026
        now.strftime("%-d %B %Y"),   # 1 April 2026
        now.strftime("%B %-d, %Y"),  # April 1, 2026 (The one you saw!)
        "Today"                       # Sometimes sites just say "Today"
    ]
    
    print(f"Checking for these date formats: {today_formats}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            page_num = 1
            while page_num <= 12: # Scrape up to 12 pages
                page.wait_for_selector(".sys_mag-item", timeout=15000)
                soup = BeautifulSoup(page.content(), 'html.parser')
                events = soup.find_all('div', class_='sys_mag-item')
                
                print(f"Page {page_num}: Found {len(events)} items.")
                
                for event in events:
                    title_el = event.find(['h3', 'a'])
                    date_el = event.find('p', class_='sys_mag-date')
                    
                    if title_el and date_el:
                        title = title_el.get_text(strip=True)
                        date_text = date_el.get_text(strip=True)
                        
                        # Check if ANY of our date formats appear in the event's date text
                        is_today = any(fmt.lower() in date_text.lower() for fmt in today_formats)
                        
                        if is_today:
                            print(f"✅ MATCH: {title} ({date_text})")
                            link = event.find('a')['href'] if event.find('a') else "#"
                            if not link.startswith('http'):
                                link = "https://www.visitsurrey.com" + link
                            
                            all_events_html += f"""
                            <div class='event'>
                                <a href='{link}' target='_blank'><strong>{title}</strong></a>
                                <span class='date'>📅 {date_text}</span>
                            </div>
                            """

                next_button = page.locator("a.sys_pagination-next")
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(2000)
                    page_num += 1
                else:
                    break
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    # Create the final page
    today_display = now.strftime("%A, %B %-d, %Y")
    final_html = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f4f4f9; color: #333; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            h1 {{ color: #1b5e20; border-bottom: 4px solid #81c784; padding-bottom: 10px; margin-top: 0; }}
            .event {{ border-left: 5px solid #4caf50; background: #f9fff9; margin-bottom: 15px; padding: 15px; border-radius: 0 8px 8px 0; }}
            .event a {{ color: #2e7d32; text-decoration: none; font-size: 1.2em; font-weight: bold; }}
            .date {{ display: block; color: #555; margin-top: 8px; font-size: 0.95em; font-style: italic; }}
            .footer {{ text-align: center; font-size: 0.8em; color: #aaa; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Surrey Family Events</h1>
            <p>What's on for <strong>{today_display}</strong></p>
            {all_events_html if all_events_html else "<p>No events found for today's specific date.</p>"}
            <div class="footer">Last synced: {now.strftime('%H:%M')}</div>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
