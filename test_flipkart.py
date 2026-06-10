import asyncio

from scrapers.flipkart_scraper import (
    scrape_flipkart
)


async def main():

    df = await scrape_flipkart()

    print(df.head())


asyncio.run(main())