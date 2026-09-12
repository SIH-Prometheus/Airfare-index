import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False = you SEE the browser
        page = await browser.new_page()
        await page.goto("https://www.airindia.com/in/en/book.html", wait_until="domcontentloaded", timeout=60000)
        print("Page title:", await page.title())
        await page.wait_for_timeout(8000)  # give the JS widget time to render
        await page.screenshot(path="airindia_home.png", full_page=True)
        await asyncio.sleep(3)  # keep it open 5 sec so you can look
        await browser.close()

asyncio.run(main())