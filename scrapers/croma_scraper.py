import pandas as pd
import re

from datetime import datetime
from playwright.async_api import async_playwright


async def scrape_croma():

    url = "https://www.croma.com/home-appliances/air-conditioners/split-acs/c/393?q=%3Arelevance%3ASG-AirConditionerCategory-AirConditionerCapacity_range%3A1.5+to+1.7+ton"

    data = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()

        await page.goto(
            url,
            timeout=60000
        )

        await page.wait_for_timeout(
            5000
        )

        try:

            await page.fill(
                "input.pinElem",
                "400049"
            )

            await page.click(
                "#apply-pincode-btn"
            )

            print(
                "Pincode Applied"
            )

        except Exception as e:

            print(
                f"Pincode Error: {e}"
            )

        await page.wait_for_timeout(
            10000
        )

        html = await page.content()

        with open(
            "croma_page.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(html)

        print(
            "\nHTML Saved"
        )

        
        # Temporary extraction test
        products = re.findall(
            r'"name":"([^"]+)".*?"value":(\d+)',
            html,
            re.DOTALL
        )

        print(
            f"\nProducts With Prices: {len(products)}"
        )

        for name, price in products[:10]:

            print(name)
            print(price)
            print("-" * 50)

        for name, price in products:

            data.append([
                name,
                int(price),
                "No Rating",
                "No Link",
                "Croma",
                "UNKNOWN",
                datetime.now()
            ])

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
            f"\nCroma Rows: {len(df)}"
        )

        print(
            df.head()
        )

        return df