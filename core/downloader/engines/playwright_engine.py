from playwright.async_api import async_playwright


class PlaywrightDownloader:

    @staticmethod
    async def download(job):

        async with async_playwright() as p:

            browser = await p.chromium.launch()

            page = await browser.new_page()

            await page.goto(
                job.url
            )

            # placeholder logic

            await browser.close()

            return False