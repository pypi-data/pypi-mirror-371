import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from humancursor_playwright import PlaywrightCursor


async def main():
    async with async_playwright() as playwright:
        # Launch browser
        browser = await playwright.chromium.launch(headless=False)
        
        # Create a new page
        page = await browser.new_page()
        
        try:
            # Navigate to a website
            await page.goto("https://www.google.com")
            
            # Initialize HumanCursor
            cursor = PlaywrightCursor(page)
            
            # Show the cursor (adds a red dot to visualize movements)
            await cursor.show_cursor()
            await asyncio.sleep(10)
            
            # Find the search input
            search_input = page.locator("textarea[jsname='yZiJbe']")
            
            # Move to the search input with human-like movement and click
            await cursor.click_on(search_input)
            
            # Type something
            await search_input.type("human cursor playwright")
            await asyncio.sleep(10)
            search_inpu = page.locator("a[aria-label='Войти']")
            
            # Move to the search input with human-like movement and click
            await cursor.click_on(search_inpu)
            await asyncio.sleep(10)
            # Find the search button
            search_button = page.locator("input[name='btnK']").first
            
            # Move to the search button and click
            await cursor.click_on(search_button)
            
            # Wait for results to load
            await page.wait_for_load_state('networkidle')
            
            # Find a result link
            result_link = page.locator("h3").first
            
            # Move to the result link and click
            await cursor.click_on(result_link)
            
            # Wait to see the result
            await asyncio.sleep(5)
            
        finally:
            # Close the browser
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())