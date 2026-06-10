import shutil
from datetime import datetime

import pandas as pd

from utils.price_utils import (
    process_prices,
    save_data,
    save_to_database,
    generate_insights,
    detect_price_drops,
    find_cheapest_products,
    generate_events,
    detect_anomalies,
    write_log
)


from scrapers.flipkart_scraper import (
    scrape_flipkart
)

import asyncio

from scrapers.amazon_scraper import (
    scrape_amazon
)

from scrapers.croma_scraper import (
    scrape_croma
)

from alerts.telegram_alert import (
    send_telegram_alert
)

def backup_database():

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        f"backups/ac_prices_{timestamp}.db"
    )

    shutil.copy(
        "data/ac_prices.db",
        backup_file
    )

    print(
        f"\nBackup Created: {backup_file}"
    )

    write_log(
        f"BACKUP CREATED: {backup_file}"
    )

async def main():

    write_log(
        "RUN STARTED"
    )
    


    print(
        "\nStarting Amazon scraper..."
    )

    try:

        amazon_df = await scrape_amazon()

    except Exception as e:

        print(
            f"\nAmazon Error: {e}"
        )

        await send_telegram_alert(
            f"❌ Amazon Scraper Failed\n\n{e}"
        )

        amazon_df = pd.DataFrame()


    try:

        flipkart_df = await scrape_flipkart()

    except Exception as e:

        print(
            f"\nFlipkart Error: {e}"
        )

        await send_telegram_alert(
            f"❌ Flipkart Scraper Failed\n\n{e}"
        )

        flipkart_df = pd.DataFrame()


    try:

        croma_df = await scrape_croma()

    except Exception as e:

        print(
            f"\nCroma Error: {e}"
        )

        await send_telegram_alert(
            f"❌ Croma Scraper Failed\n\n{e}"
        )

        croma_df = pd.DataFrame()

    df = pd.concat(
        [
            amazon_df,
            flipkart_df,
            croma_df
        ],
        ignore_index=True
    )

    print(
        f"\nRAW PRODUCTS: {len(df)}"
    )

    if len(df) == 0:

        write_log(
            "NO PRODUCTS SCRAPED"
        )

        await send_telegram_alert(
            "❌ No products scraped from any website."
        )

        return
    


    print("\nScraping Success!\n")

    df = process_prices(df)

    print(
        f"\nAFTER PROCESSING: {len(df)}"
    )

    write_log(
        f"TOTAL PRODUCTS: {len(df)}"
    )

    print(
        df[
            [
                "brand",
                "tonnage",
                "star_rating",
                "wifi",
                "inverter"
            ]
        ].head()
    )

    print(
        df[
            ["title", "model_no"]
        ].head()
    )

    cheapest_df = find_cheapest_products(
        df
    )

    print(
        "\nCHEAPEST PRODUCTS\n"
    )

    print(
        cheapest_df.head(10)
    )

    import sqlite3

    conn = sqlite3.connect(
        "data/ac_prices.db"
    )

    historical_df = pd.read_sql_query(
        "SELECT * FROM ac_prices",
        conn
    )
    price_drop_alerts = detect_price_drops(
        df,
        historical_df
    )

    anomaly_alerts = detect_anomalies(
        df,
        historical_df
    )

    conn.close()
    save_data(df)
    save_to_database(df)
    backup_database()
    
    events = generate_events(df)

    for event in events:

        print(event)

        await send_telegram_alert(
            event
        )

    insights = generate_insights(df)

    print(
        "\nReached Telegram Alert Section"
    )

    print(insights)

    for alert in price_drop_alerts:

        print(alert)

        await send_telegram_alert(
            alert
        )
    await send_telegram_alert(
    insights
    )

    for alert in anomaly_alerts:

        print(alert)

        await send_telegram_alert(
            alert
        )

    write_log(
        "RUN COMPLETED"
    )


asyncio.run(main())