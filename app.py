import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="BitesUAE Dashboard", layout="wide")

# ------------------------------
# Load Data (FIXED PATHS)
# ------------------------------
@st.cache_data
def load_data():
    customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
    restaurants = pd.read_csv("restaurants.csv")
    orders = pd.read_csv("orders.csv", parse_dates=["order_datetime"])
    order_items = pd.read_csv("order_items.csv")
    delivery_events = pd.read_csv(
        "delivery_events.csv",
        parse_dates=[
            "order_placed_time",
            "restaurant_confirmed_time",
            "food_ready_time",
            "rider_picked_up_time",
            "delivered_time",
            "estimated_delivery_time"
        ]
    )
    riders = pd.read_csv("riders.csv")

    return customers, restaurants, orders, order_items, delivery_events, riders


customers, restaurants, orders, order_items, delivery_events, riders = load_data()

# ------------------------------
# JOIN TABLES (CRITICAL)
# ------------------------------
orders = orders.merge(customers, on="customer_id", how="left")
orders = orders.merge(restaurants, on="restaurant_id", how="left")
orders = orders.merge(delivery_events, on="order_id", how="left")

# ------------------------------
# SIDEBAR FILTERS
# ------------------------------
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Order Date Range",
    [orders["order_datetime"].min().date(), orders["order_datetime"].max().date()]
)

city_filter = st.sidebar.multiselect("City", orders["city"].dropna().unique())
zone_filter = st.sidebar.multiselect("Zone", orders["zone"].dropna().unique())
cuisine_filter = st.sidebar.multiselect("Cuisine", orders["cuisine_type"].dropna().unique())
tier_filter = st.sidebar.multiselect("Restaurant Tier", orders["restaurant_tier"].dropna().unique())

view_toggle = st.sidebar.radio("View", ["Executive View", "Manager View"])

# ------------------------------
# APPLY FILTERS
# ------------------------------
df = orders.copy()

df = df[
    (df["order_datetime"].dt.date >= date_range[0]) &
    (df["order_datetime"].dt.date <= date_range[1])
]

if city_filter:
    df = df[df["city"].isin(city_filter)]
if zone_filter:
    df = df[df["zone"].isin(zone_filter)]
if cuisine_filter:
    df = df[df["cuisine_type"].isin(cuisine_filter)]
if tier_filter:
    df = df[df["restaurant_tier"].isin(tier_filter)]

delivered = df[df["order_status"] == "Delivered"]

# ==============================
# EXECUTIVE VIEW
# ==============================
if view_toggle == "Executive View":
    st.title("📊 Executive Dashboard")

    gmv = delivered["gross_amount"].sum()
    aov = delivered["gross_amount"].mean()
    discount_burn = (
        delivered["discount_amount"].sum() /
        delivered["gross_amount"].sum()
    ) * 100

    repeat_rate = (
        delivered.groupby("customer_id")
        .size()
        .gt(1)
        .mean() * 100
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("GMV (AED)", f"{gmv:,.0f}")
    c2.metric("AOV (AED)", f"{aov:,.0f}")
    c3.metric("Repeat Rate (%)", f"{repeat_rate:.1f}")
    c4.metric("Discount Burn (%)", f"{discount_burn:.1f}")

    gmv_zone = delivered.groupby("zone")["gross_amount"].sum().sort_values()
    st.plotly_chart(
        px.bar(gmv_zone, orientation="h", title="GMV by Zone"),
        use_container_width=True
    )

    cuisine_mix = delivered.groupby("cuisine_type")["gross_amount"].sum()
    st.plotly_chart(
        px.pie(values=cuisine_mix.values, names=cuisine_mix.index, hole=0.4,
               title="GMV by Cuisine"),
        use_container_width=True
    )

# ==============================
# MANAGER VIEW
# ==============================
else:
    st.title("🚴 Manager Dashboard")

    delivered_events = df.dropna(subset=["delivered_time"])

    on_time_rate = (
        (delivered_events["delivered_time"]
         <= delivered_events["estimated_delivery_time"])
        .mean() * 100
    )

    avg_delivery = delivered_events["actual_delivery_time_mins"].mean()
    cancellation_rate = (df["order_status"] == "Cancelled").mean() * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("On-Time Rate (%)", f"{on_time_rate:.1f}")
    c2.metric("Avg Delivery Time (mins)", f"{avg_delivery:.1f}")
    c3.metric("Cancellation Rate (%)", f"{cancellation_rate:.1f}")

    delay_df = delivered_events.copy()
    delay_df["status"] = np.where(
        delay_df["delivered_time"] > delay_df["estimated_delivery_time"],
        "Late", "On Time"
    )

    delay_zone = delay_df.groupby(["zone", "status"]).size().reset_index(name="count")

    st.plotly_chart(
        px.bar(delay_zone, x="zone", y="count", color="status",
               title="Delivery Performance by Zone"),
        use_container_width=True
    )

    # ------------------------------
    # WHAT-IF ANALYSIS
    # ------------------------------
    st.subheader("🔮 What-If Analysis")

    prep_reduction = st.slider("Reduce Avg Prep Time (mins)", 1, 15, 5)
    cancel_reduction = st.slider("Reduce Cancellation Rate (%)", 5, 30, 10)

    projected_on_time = min(on_time_rate + prep_reduction * 0.5, 100)
    recovered_gmv = gmv * cancel_reduction / 100

    st.write(f"**Projected On-Time Rate:** {projected_on_time:.1f}%")
    st.write(f"**Projected GMV Recovery:** AED {recovered_gmv:,.0f}")
