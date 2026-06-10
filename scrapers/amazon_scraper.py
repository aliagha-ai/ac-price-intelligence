import asyncio
import pandas as pd
from datetime import datetime
import re

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright
)

from config.settings import (
    AMAZON_URL
)

async def extract_product_details(
    browser,
    product_url,
    title
):

    try:

        page = await browser.new_page()

        await page.goto(
            product_url,
            timeout=60000
        )

        await page.wait_for_timeout(1500)

        html = await page.content()

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        tables = soup.select(
            "table"
        )

        model_no = "UNKNOWN"

        rows = soup.select("tr")

        for row in rows:

            header = row.select_one("th")

            value_cell = row.select_one("td")

            if header and value_cell:

                key = header.get_text(
                    strip=True
                ).lower()

                value = value_cell.get_text(
                    strip=True
                )

                if "model" in key:

                    print(
                        f"\nKEY: {key}"
                    )

                    print(
                        f"VALUE: {value}"
                    )

                    if len(value) > 4 and value.upper() != "AC":

                        model_no = value

                        break

        if model_no == "UNKNOWN":

            matches = re.findall(
                r'\b[A-Z]+[0-9]+[A-Z0-9\-]*\b',
                title.upper()
            )

            ignore_words = [
                "SPLIT",
                "INVERTER",
                "COPPER",
                "MODEL",
                "STAR",
                "TON",
                "SMART",
                "CONVERTIBLE",
                "COOLING"
            ]

            for match in matches:

                if (
                    match not in ignore_words
                    and
                    len(match) >= 6
                    and
                    any(char.isdigit() for char in match)
                ):

                    model_no = match

                    break

        await page.close()

        return model_no

    except Exception as e:

        print(
            f"Detail scrape failed: {e}"
        )

        return "UNKNOWN"
    
async def scrape_amazon():

    data = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page(
            user_agent=
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        success = False

        for attempt in range(3):

            try:

                print(
                    f"\nTrying attempt {attempt + 1}"
                )

                await page.goto(
                    AMAZON_URL,
                    timeout=60000
                )

                success = True

                break

            except Exception as e:

                print(
                    f"\nAttempt failed: {e}"
                )

                await asyncio.sleep(5)

        if not success:

            await browser.close()

            return None

        await page.wait_for_timeout(5000)

        html = await page.content()

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        products = soup.select(
            "div[data-component-type='s-search-result']"
        )

        print(
            "Products Found:",
            len(products)
        )

        for product in products[:5]:

            try:

                title = product.select_one(
                    "h2"
                ).text.strip()

                price = product.select_one(
                    ".a-price-whole"
                ).text.strip()

                price = int(
                    price.replace(",", "")
                )

                rating = product.select_one(
                    ".a-icon-alt"
                )

                rating = (
                    rating.text
                    if rating
                    else "No Rating"
                )

                link = product.select_one("a")

                link = (
                    "https://www.amazon.in"
                    +
                    link["href"]
                )

                model_no = await extract_product_details(
                    browser,
                    link,
                    title
                )

                data.append([
                    title,
                    price,
                    rating,
                    link,
                    "Amazon",
                    model_no,
                    datetime.now()
                ])

            except:
                pass

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

        await browser.close()

        return df