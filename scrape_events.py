import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    today_date = datetime.now().strftime("%d %b %Y") # Format: "01 Apr 2026"
    print(f"Searching for events matching: {today_date}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            while True:
                page.wait_for_selector(".sys_mag-item", timeout=15000)
                soup = BeautifulSoup(page.content(), 'html.parser')
                events = soup.find_all('div', class_='sys_mag-item')
                
                for event in events:
                    # Use more flexible selectors to find the title and date
                    title = event.find(['h3', 'a']).get_text(strip=True)
                    date_text = event.find('p', class_='sys_mag-date').get_text(strip=True)
                    link = event.find('a')['href'] if event.find('a') else "#"
                    if not link.startswith('http'):
                        link = "https://www.visitsurrey.com" + link

                    # CHECK IF IT'S TODAY
                    # We check if 'today_date' (e.g., "01 Apr 2026") is inside the 'date_text'
                    if today_date.lower() in date_text.lower() or "today" in date_text.lower():
                        print(f"MATCH FOUND: {title}")
                        all_events_html += f"""
                        <div class='event'>
                            <a href='{link}' target='_blank'><strong>{title}</strong></a>
                            <span class='date'>📅 {date_text}</span>
                        </div>
                        """

                next_button = page.locator("a.sys_pagination-next")
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(3000) # Give it 3 seconds to flip the page
                else:
                    break
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    # Final HTML generation
    today_display = datetime.now().strftime("%A, %d %B %Y")
    final_html = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #fdfdfd; color: #222; }}
            .container {{ max-width: 600px; margin: auto; }}
            h1 {{ color: #d32f2f; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .event {{ background: white; border: 1px solid #ddd; margin-bottom: 10px; padding: 15px; border-radius: 8px; }}
            .event a {{ color: #007bff; text-decoration: none; font-size: 1.1em; }}
            .date {{ display: block; color: #666; margin-top: 5px; font-weight: bold; font-size: 0.9em; }}
            .empty {{ text-align: center; color: #999; padding: 40px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Events in Surrey Today</h1>
            <p>Showing events for: <strong>{today_display}</strong></p>
            {all_events_html if all_events_html else "<div class='empty'>No specific matches found for today's date in the list.</div>"}
            <p style="text-align: center; font-size: 0.8em; margin-top: 20px; color: #ccc;">
                Checked all pages at {datetime.now().strftime('%H:%M')}
            </p>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
