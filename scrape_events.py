import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_surrey_events():
    all_events_html = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a real-looking browser header
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = context.new_page()
        
        url = "https://www.visitsurrey.com/whats-on/family-friendly-events/"
        print(f"Opening: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # We will scrape the first 3 pages just to prove it works
            for page_num in range(1, 4):
                print(f"Scraping Page {page_num}...")
                page.wait_for_selector(".sys_mag-item", timeout=10000)
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                items = soup.find_all('div', class_='sys_mag-item')
                
                print(f"Found {len(items)} events on this page.")
                
                for item in items:
                    title_el = item.find(['h3', 'a'])
                    date_el = item.find('p', class_='sys_mag-date')
                    
                    title = title_el.get_text(strip=True) if title_el else "Unnamed Event"
                    date_text = date_el.get_text(strip=True) if date_el else "No date shown"
                    
                    # Fix links
                    link_el = item.find('a')
                    link = link_el['href'] if link_el else "#"
                    if link.startswith('/'):
                        link = "https://www.visitsurrey.com" + link

                    # FOR NOW: We add EVERYTHING. No filters. 
                    # This is to prove the scraper can actually see the data.
                    all_events_html += f"""
                    <div style="border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 8px;">
                        <a href="{link}" style="font-weight: bold; color: blue;">{title}</a>
                        <p style="margin: 5px 0; color: #555;">{date_text}</p>
                    </div>
                    """

                # Try to click next
                next_btn = page.locator("a.sys_pagination-next")
                if next_btn.is_visible():
                    next_btn.click()
                    page.wait_for_timeout(3000)
                else:
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    # Simple HTML Output
    final_html = f"<html><body><h1>Debug: All Surrey Events</h1>{all_events_html}</body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)

if __name__ == "__main__":
    scrape_surrey_events()
