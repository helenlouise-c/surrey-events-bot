import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    now = datetime.now()
    
    # Visit Surrey uses "Apr 01" or "Apr 1" in their date badges
    month_short = now.strftime("%b") # e.g., "Apr"
    day_padded = now.strftime("%d")  # e.g., "01"
    day_unpadded = now.strftime("%-d") # e.g., "1"
    
    match_1 = f"{month_short} {day_padded}"   # "Apr 01"
    match_2 = f"{month_short} {day_unpadded}" # "Apr 1"
    
    print(f"Targeting: {match_1} or {match_2}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            for page_num in range(1, 11): # Check up to 10 pages
                print(f"Scanning Page {page_num}...")
                page.wait_for_selector(".sys_mag-item", timeout=10000)
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                items = soup.find_all('div', class_='sys_mag-item')
                
                for item in items:
                    # Get the text from the entire item to find our date match
                    item_text = item.get_text(" ", strip=True)
                    
                    if match_1 in item_text or match_2 in item_text or "Today" in item_text:
                        title_el = item.find(['h3', 'a'])
                        title = title_el.get_text(strip=True) if title_el else "Unknown Event"
                        
                        # Find the link
                        link_el = item.find('a')
                        link = link_el['href'] if link_el else "#"
                        if link.startswith('/'):
                            link = "https://www.visitsurrey.com" + link
                        
                        print(f"✨ MATCH FOUND: {title}")
                        
                        all_events_html += f"""
                        <div class='event-card'>
                            <div class='event-info'>
                                <a href='{link}' target='_blank' class='title'>{title}</a>
                                <p class='status'>📅 Happening Today</p>
                            </div>
                        </div>
                        """

                # Pagination: Click the right arrow
                next_btn = page.locator("a.sys_pagination-next")
                if next_btn.is_visible() and next_btn.is_enabled():
                    next_btn.click()
                    page.wait_for_timeout(2000)
                else:
                    break
        except Exception as e:
            print(f"Scraper Error: {e}")
        finally:
            browser.close()

    # Create a nice looking interface
    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Surrey Events Bot</title>
        <style>
            body {{ font-family: -apple-system, system-ui, sans-serif; background: #f0f2f5; padding: 20px; }}
            .container {{ max-width: 500px; margin: auto; }}
            h1 {{ color: #1c1e21; font-size: 24px; margin-bottom: 5px; }}
            .subtitle {{ color: #606770; margin-bottom: 20px; }}
            .event-card {{ background: white; border-radius: 12px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #42b72a; }}
            .title {{ font-weight: bold; color: #1877f2; text-decoration: none; font-size: 18px; }}
            .status {{ color: #42b72a; font-weight: 600; margin-top: 5px; font-size: 14px; }}
            .empty-state {{ text-align: center; background: white; padding: 40px; border-radius: 12px; color: #606770; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Surrey Family Events</h1>
            <p class="subtitle">Showing events for {now.strftime('%A, %B %d')}</p>
            {all_events_html if all_events_html else "<div class='empty-state'>No events listed for today yet. Try again later!</div>"}
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
