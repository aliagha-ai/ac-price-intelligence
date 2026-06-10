import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px


st.set_page_config(
    page_title="AC Dashboard",
    layout="wide"
)


st.title(
    "📊 AC Market Intelligence Dashboard"
)


conn = sqlite3.connect(
    "data/ac_prices.db"
)


query = """
SELECT *
FROM ac_prices
"""


df = pd.read_sql_query(
    query,
    conn
)


conn.close()


# ---------------- SIDEBAR ----------------

st.sidebar.header(
    "🔍 Filters"
)


brands = st.sidebar.multiselect(
    "Select Brand",
    options=[
        "LG",
        "Daikin",
        "Panasonic",
        "Hitachi",
        "Blue Star"
    ],
    default=[
        "LG",
        "Daikin",
        "Panasonic",
        "Hitachi",
        "Blue Star"
    ]
)


search_text = st.sidebar.text_input(
    "Search Product"
)


price_range = st.sidebar.slider(
    "Select Price Range",
    int(df["price"].min()),
    int(df["price"].max()),
    (
        int(df["price"].min()),
        int(df["price"].max())
    )
)


sort_option = st.sidebar.selectbox(
    "Sort By",
    [
        "Lowest Price",
        "Highest Price"
    ]
)

selected_product = st.sidebar.selectbox(
    "Select Product Trend",
    df["title"].unique()
)


# ---------------- FILTER LOGIC ----------------

pattern = "|".join(brands)

df["brand"] = (
    df["title"]
    .str.split()
    .str[0]
)

filtered_df = df[
    (
        df["title"].str.contains(
            pattern,
            case=False,
            na=False
        )
    )
    &
    (
        df["title"].str.contains(
            search_text,
            case=False,
            na=False
        )
    )
    &
    (
        df["price"] >= price_range[0]
    )
    &
    (
        df["price"] <= price_range[1]
    )
]


if sort_option == "Lowest Price":

    filtered_df = filtered_df.sort_values(
        by="price"
    )

else:

    filtered_df = filtered_df.sort_values(
        by="price",
        ascending=False
    )


# ---------------- MAIN DASHBOARD ----------------

st.subheader(
    "📦 Filtered AC Data"
)

st.dataframe(
    filtered_df,
    width="stretch"
)


# ---------------- METRICS ----------------

st.subheader(
    "📈 Market Statistics"
)


col1, col2, col3 = st.columns(3)


col1.metric(
    "Total Products",
    len(filtered_df)
)

col2.metric(
    "Average Price",
    f"₹{int(filtered_df['price'].mean())}"
)

col3.metric(
    "Lowest Price",
    f"₹{filtered_df['price'].min()}"
)
# ---------------- BEST DEALS ----------------

st.subheader(
    "🔥 Best Deals"
)


cheapest_product = (
    filtered_df
    .sort_values(by="price")
    .iloc[0]
)


most_expensive = (
    filtered_df
    .sort_values(
        by="price",
        ascending=False
    )
    .iloc[0]
)


col4, col5 = st.columns(2)


with col4:

    st.success(
        f"""
        Cheapest Deal

        {cheapest_product['title']}

        ₹{cheapest_product['price']}

        Website: {cheapest_product['website']}
        """
    )


with col5:

    st.error(
        f"""
        Most Expensive

        {most_expensive['title']}

        ₹{most_expensive['price']}

        Website: {most_expensive['website']}
        """
    )
# ---------------- CHARTS ----------------

st.subheader(
    "📊 Brand Price Comparison"
)


brand_avg = (
    filtered_df
    .groupby("brand")["price"]
    .mean()
    .reset_index()
)


fig = px.bar(
    brand_avg,
    x="brand",
    y="price",
    color="brand",
    title="Average AC Price by Brand"
)


st.plotly_chart(
    fig,
    use_container_width=True
)

# ---------------- PRICE TREND ----------------

st.subheader(
    "📈 Price Trend Analysis"
)


trend_df = df[
    df["title"] == selected_product
]


trend_df = trend_df.sort_values(
    by="scraped_at"
)


fig2 = px.line(
    trend_df,
    x="scraped_at",
    y="price",
    title="Price Trend Over Time",
    markers=True
)


st.plotly_chart(
    fig2,
    use_container_width=True
)
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
            pattern,
            case=False,
            na=False
        )
    )
    &
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