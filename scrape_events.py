import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Opening website...")
        page.goto("https://www.visitsurrey.com/whats-on/family-friendly-events/", wait_until="networkidle")
        
        # Wait specifically for the event items to appear in the HTML
        page.wait_for_selector(".sys_mag-item", timeout=10000)
        
        # Get the fully rendered HTML
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()

    events = soup.find_all('div', class_='sys_mag-item')
    today_str = datetime.now().strftime("%d %B %Y")
    
    html_output = f"""
    <html>
    <head>
        <title>Surrey Events Today</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; line-height: 1.6; }}
            .event {{ border-bottom: 1px solid #eee; padding: 10px 0; }}
            h1 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <h1>Family Events in Surrey: {today_str}</h1>
    """

    if not events:
        html_output += "<p>No events found. The page structure might have changed.</p>"
    else:
        for event in events:
            title = event.find('h3').get_text(strip=True)
            date_text = event.find('p', class_='sys_mag-date').get_text(strip=True)
            html_output += f"<div class='event'><strong>{title}</strong><br>{date_text}</div>"

    html_output += f"<p><small>Last updated: {datetime.now().strftime('%H:%M')}</small></p></body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_output)
    print("Successfully updated index.html")

if __name__ == "__main__":
    scrape_surrey_events()
