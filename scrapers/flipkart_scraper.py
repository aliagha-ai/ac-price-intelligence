import asyncio
import pandas as pd

from datetime import datetime

from playwright.async_api import (
    async_playwright
)


async def scrape_flipkart():

    url = (
        "https://www.flipkart.com/search?q=1.5+ton+split+ac"
    )

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        await page.goto(url)

        await page.wait_for_timeout(5000)

        products = await page.query_selector_all(
            "div[data-id]"
        )

        data = []

        print(
            f"\nTotal product containers: {len(products)}"
        )

        for product in products[:20]:

            try:

                title_element = await product.query_selector(
                    "div.RG5Slk"
                )

                price_element = await product.query_selector(
                    "div.hZ3P6w.DeU9vF"
                )

                if title_element and price_element:

                    title = await title_element.inner_text()

                    price = await price_element.inner_text()

                    price = (
                        price
                        .replace("₹", "")
                        .replace(",", "")
                    )

                    price = int(price)

                    model_no = "UNKNOWN"

                    data.append([
                        title,
                        price,
                        "No Rating",
                        "No Link",
                        "Flipkart",
                        model_no,
                        datetime.now()
                    ])

                    print(title)
                    print(price)
                    print("-" * 50)

            except Exception as e:

                print(e)

        await browser.close()

        df = pd.DataFrame(
            data,
            columns=[
                "title",
                "price",
                "rating",
                "link",
                "website",
                "model_no",
                "scraped_at"
            ]
        )

        print(
            f"\nFlipkart Products Found: {len(df)}"
        )

        print(df.head())

        return df