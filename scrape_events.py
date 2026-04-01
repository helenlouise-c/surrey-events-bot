import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Setting a standard window size so the buttons are where we expect them
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        print(f"Opening {url}...")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            page_count = 1
            while page_count <= 5: 
                print(f"Scraping page {page_count}...")
                
                # Wait for events to appear
                page.wait_for_selector(".sys_mag-item", timeout=15000)
                
                # Scrape the current page
                soup = BeautifulSoup(page.content(), 'html.parser')
                events = soup.find_all('div', class_='sys_mag-item')
                
                for event in events:
                    title_el = event.find('h3')
                    date_el = event.find('p', class_='sys_mag-date')
                    if title_el and date_el:
                        title = title_el.get_text(strip=True)
                        date_text = date_el.get_text(strip=True)
                        all_events_html += f"<div class='event'><strong>{title}</strong><br><span class='date'>{date_text}</span></div>"

                # FIND THE NEXT BUTTON: 
                # We look for the link that has the 'next' class
                next_button = page.locator("a.sys_pagination-next")
                
                if next_button.is_visible():
                    print("Found the arrow! Clicking...")
                    next_button.click()
                    # Wait for the new content to load
                    page.wait_for_load_state("networkidle")
                    page_count += 1
                else:
                    print("Reached the last page.")
                    break
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    # Create the HTML file
    today_str = datetime.now().strftime("%d %B %Y")
    final_html = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; padding: 20px; background: #f0f2f5; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #1a73e8; margin-top: 0; }}
            .event {{ border-bottom: 1px solid #eee; padding: 15px 0; }}
            .date {{ color: #d93025; font-size: 0.9em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Surrey Family Events</h1>
            <p>Generated on: {today_str}</p>
            {all_events_html if all_events_html else "<p>No events found today.</p>"}
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
