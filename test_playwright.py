import asyncio
import pandas as pd
from telegram import Bot
import os
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
TOKEN = "8621613099:AAHGN-ogOOBYgOiApjdU4bKfeWvRi4OLpg8"

CHAT_ID = "8538679635"

async def send_telegram_alert(message):

    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )
async def main():

    data = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page(
            user_agent=
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        url = "https://www.amazon.in/s?k=1.5+ton+split+ac"

        success = False

        for attempt in range(3):

            try:

                print(
                    f"\nTrying attempt {attempt + 1}"
                )

                await page.goto(
                    url,
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

            error_message = """
        ❌ AMAZON SCRAPER FAILED

        Website connection failed after 3 attempts.
        """

            print(error_message)

            await send_telegram_alert(
                error_message
            )

            await browser.close()

            return

        await page.wait_for_timeout(5000)

        html = await page.content()

        soup = BeautifulSoup(html, "html.parser")

        products = soup.select(
            "div[data-component-type='s-search-result']"
        )

        print("Products Found:", len(products))

        for product in products:

            try:

                title = product.select_one(
                    "h2"
                ).text.strip()

                price = product.select_one(
                    ".a-price-whole"
                ).text.strip()

                price = price.replace(",", "")

                price = int(price)

                rating = product.select_one(
                    ".a-icon-alt"
                )

                rating = rating.text if rating else "No Rating"

                link = product.select_one("a")

                link = "https://www.amazon.in" + link["href"]

                data.append([
                    title,
                    price,
                    rating,
                    link
                ])

            except:
                pass

        df = pd.DataFrame(
            data,
            columns=[
                "title",
                "price",
                "rating",
                "link"
            ]
        )
        df = df.drop_duplicates(
            subset="title"
        )

        premium_brands = [
        "Daikin",
        "LG",
        "Panasonic",
        "Hitachi",
        "Blue Star"
        ]

        pattern = "|".join(
            premium_brands
        )

        df = df[
            df["title"].str.contains(
                pattern,
                case=False,
                na=False
            )
        ]

        cheapest = df.iloc[0]

        print("\nCheapest Premium AC:\n")

        print(cheapest)

        print("\nTop Rated Products:\n")

        print(df[["title", "rating"]].head())

        df = df.sort_values(
            by="price"
        )

        print(df.head())

        df["scraped_at"] = datetime.now()

        if os.path.exists("latest_prices.csv"):

            old_df = pd.read_csv(
                "latest_prices.csv"
            )

            merged = df.merge(
                old_df,
                on="title",
                suffixes=("_new", "_old")
            )

            drops = merged[
                merged["price_new"]
                <
                merged["price_old"]
            ]

            if len(drops) > 0:

                print("\n🔥 PRICE DROPS DETECTED:\n")

                for _, row in drops.iterrows():

                    diff = (
                        row["price_old"]
                        -
                        row["price_new"]
                    )

                    print(
                        f"{row['title']}"
                    )

                    print(
                        f"Old Price: ₹{row['price_old']}"
                    )

                    print(
                        f"New Price: ₹{row['price_new']}"
                    )

                    print(
                        f"Drop: ₹{diff}"
                    )

                    message = f"""
                    🔥 AC PRICE DROP ALERT

                    {row['title']}

                    Old Price: ₹{row['price_old']}

                    New Price: ₹{row['price_new']}

                    Drop: ₹{diff}

                    {row['link_new']}
                    """

                    await send_telegram_alert(message)

                    print("-" * 50)
        
        
        df.to_csv(
            "latest_prices.csv",
            index=False
        )

        df.to_csv(
            "ac_price_history.csv",
            mode="a",
            header=False,
            index=False
        )

        print("\nCSV file saved successfully")

        await browser.close()


asyncio.run(main())


