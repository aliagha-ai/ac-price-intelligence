import sqlite3
import pandas as pd
import re

def extract_brand(title):

    brands = [
        "Daikin",
        "LG",
        "Panasonic",
        "Hitachi",
        "Blue Star",
        "Voltas",
        "Samsung",
        "Godrej",
        "Carrier",
        "Lloyd",
        "Whirlpool",
        "Hisense"
    ]

    for brand in brands:

        if brand.lower() in title.lower():

            return brand

    return "Unknown"


def extract_tonnage(title):

    match = re.search(
        r'(\d+(\.\d+)?)\s*ton',
        title.lower()
    )

    if match:

        return float(match.group(1))

    return None


def extract_star_rating(title):

    match = re.search(
        r'(\d)\s*star',
        title.lower()
    )

    if match:

        return int(match.group(1))

    return None


def extract_wifi(title):

    return "wifi" in title.lower()


def extract_inverter(title):

    return "inverter" in title.lower()

def normalize_title(title):

    title = title.lower()

    remove_words = [
        "2025",
        "2026",
        "model",
        "split",
        "inverter",
        "ac",
        "wifi",
        "smart"
    ]

    for word in remove_words:

        title = re.sub(
            rf"\b{word}\b",
            "",
            title
        )

    title = re.sub(
        r'[^a-z0-9 ]',
        '',
        title
    )

    title = " ".join(
        title.split()
    )

    return title

def extract_model_number(title):

    pattern = r'\b[A-Z0-9\-]{5,}\b'

    matches = re.findall(
        pattern,
        str(title).upper()
    )

    ignore_words = [
        "SPLIT",
        "INVERTER",
        "COPPER",
        "STAR",
        "WIFI"
    ]

    filtered = []

    for match in matches:

        if match not in ignore_words:

            filtered.append(match)

    if filtered:

        return filtered[0]

    return "UNKNOWN"


def process_prices(df):

    # df["model_no"] = df["title"].apply(
    #     extract_model_number
    # )

    df = df.drop_duplicates(
        subset="title"
    )

    # =====================================
    # PREMIUM FILTER DISABLED FOR NOW
    # =====================================

    # premium_brands = [
    #     "Daikin",
    #     "LG",
    #     "Panasonic",
    #     "Hitachi",
    #     "Blue Star"
    # ]

    # pattern = "|".join(
    #     premium_brands
    # )

    exclude_keywords = [
        "remote",
        "stand",
        "cover",
        "pipe",
        "stabilizer",
        "cleaner",
        "filter",
        "installation kit",
        "wire"
    ]

    exclude_pattern = "|".join(
        exclude_keywords
    )

    df = df[
        (
            df["title"].str.contains(
                "split",
                case=False,
                na=False
            )
        )
        &
        (
            ~df["title"].str.contains(
                exclude_pattern,
                case=False,
                na=False
            )
        )
    ]

    df["normalized_title"] = (
        df["title"]
        .apply(normalize_title)
    )

    df = df.sort_values(
        by="price"
    )

    df["brand"] = df["title"].apply(
        extract_brand
    )

    df["tonnage"] = df["title"].apply(
        extract_tonnage
    )

    df["star_rating"] = df["title"].apply(
        extract_star_rating
    )

    df["wifi"] = df["title"].apply(
        extract_wifi
    )

    df["inverter"] = df["title"].apply(
        extract_inverter
    )

    return df


def save_data(df):

    df.to_csv(
        "data/latest_prices.csv",
        index=False
    )

    df.to_csv(
        "data/ac_price_history.csv",
        mode="a",
        header=False,
        index=False
    )


def save_to_database(df):

    conn = sqlite3.connect(
        "data/ac_prices.db"
    )

    df.to_sql(
        "ac_prices",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()


def generate_insights(df):

    cheapest = df.iloc[0]

    average_price = int(
        df["price"].mean()
    )

    total_products = len(df)

    insights = f"""
📊 AC MARKET INSIGHTS

Total Premium ACs: {total_products}

🔥 Cheapest AC:
{cheapest['title']}

💰 Price: ₹{cheapest['price']}

📈 Average Price: ₹{average_price}
"""
    
    return insights

def detect_price_drops(
    current_df,
    historical_df
):

    alerts = []

    for _, current_row in current_df.iterrows():

        current_title = current_row["title"]

        current_price = current_row["price"]

        old_rows = historical_df[
            historical_df["title"] == current_title
        ]

        if len(old_rows) > 0:

            old_price = old_rows.iloc[-1]["price"]

            if current_price < old_price:

                drop = old_price - current_price

                alert = f"""
🔥 PRICE DROP DETECTED

📦 Product:
{current_title}

💰 Old Price: ₹{old_price}

🆕 New Price: ₹{current_price}

📉 Drop: ₹{drop}
"""

                alerts.append(alert)

    return alerts

def find_cheapest_products(df):

    cheapest_products = []

    grouped = df.groupby(
        "normalized_title"
    )

    for product_name, group in grouped:

        cheapest_row = group.loc[
            group["price"].idxmin()
        ]

        cheapest_products.append({
            "product": product_name,
            "website": cheapest_row["website"],
            "price": cheapest_row["price"]
        })

    return pd.DataFrame(
        cheapest_products
    )

def generate_events(df):

    events = []

    cheapest_5_star = df[
        df["star_rating"] == 5
    ]

    if not cheapest_5_star.empty:

        row = cheapest_5_star.sort_values(
            "price"
        ).iloc[0]

        events.append(
            f"""
🏆 CHEAPEST 5 STAR AC

📦 {row['title']}

💰 ₹{row['price']}
"""
        )

    daikin = df[
        df["brand"] == "Daikin"
    ]

    if not daikin.empty:

        row = daikin.sort_values(
            "price"
        ).iloc[0]

        events.append(
            f"""
🏆 CHEAPEST DAIKIN

📦 {row['title']}

💰 ₹{row['price']}
"""
        )

    under_40k = df[
        df["price"] <= 40000
    ]

    if not under_40k.empty:

        row = under_40k.sort_values(
            "price"
        ).iloc[0]

        events.append(
            f"""
🏆 BEST AC UNDER 40K

📦 {row['title']}

💰 ₹{row['price']}
"""
        )

    return events

def detect_anomalies(
    current_df,
    historical_df
):

    alerts = []

    for _, current_row in current_df.iterrows():

        current_title = current_row["title"]

        current_price = current_row["price"]

        old_rows = historical_df[
            historical_df["title"] == current_title
        ]

        if len(old_rows) >= 3:

            avg_price = old_rows["price"].mean()

            if current_price < avg_price * 0.90:

                discount_pct = round(
                    (
                        (avg_price - current_price)
                        / avg_price
                    ) * 100,
                    2
                )

                alert = f"""
🚨 ANOMALY DETECTED

📦 Product:
{current_title}

💰 Current Price: ₹{current_price}

📊 Historical Avg: ₹{int(avg_price)}

📉 Discount: {discount_pct}%
"""

                alerts.append(alert)

    return alerts

from datetime import datetime

def write_log(message):

    with open(
        "logs/run_log.txt",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"[{datetime.now()}] {message}\n"
        )