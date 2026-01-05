import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="BitesUAE Dashboard", layout="wide")

# ------------------------------
# 1. Load Data
# ------------------------------
@st.cache_data
def load_data():
    customers = pd.read_csv("customers.csv")
    restaurants = pd.read_csv("restaurants.csv")
    orders = pd.read_csv("orders.csv")
    order_items = pd.read_csv("order_items.csv")
    delivery_events = pd.read_csv("delivery_events.csv")
    riders = pd.read_csv("riders.csv")
    return customers, restaurants, orders, order_items, delivery_events, riders

customers, restaurants, orders, order_items, delivery_events, riders = load_data()

# ------------------------------
# 2. Sidebar Filters
# ------------------------------
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range", [])
city_filter = st.sidebar.multiselect("Select City", options=customers['city'].unique())
zone_filter = st.sidebar.multiselect("Select Zone", options=restaurants['zone'].unique())
cuisine_filter = st.sidebar.multiselect("Select Cuisine", options=restaurants['cuisine_type'].unique())
restaurant_tier_filter = st.sidebar.multiselect("Select Restaurant Tier", options=restaurants['restaurant_tier'].unique())
time_filter = st.sidebar.selectbox("Time of Day", options=["All", "Lunch (12–2 PM)", "Peak (7–10 PM)", "Off-Peak"])

view_toggle = st.sidebar.radio("Select View", options=["Executive View", "Manager View"])

# ------------------------------
# 3. Filter Data
# ------------------------------
# Example: Filter by city
if city_filter:
    orders = orders[orders['city'].isin(city_filter)]

# ------------------------------
# 4. Executive View
# ------------------------------
if view_toggle == "Executive View":
    st.title("Executive Dashboard")
    
    # Example KPI: GMV
    gmv = orders[orders['order_status']=="Delivered"]["gross_amount"].sum()
    st.metric(label="GMV (AED)", value=f"{gmv:,.2f}")
    
    # Example Chart: GMV by Zone
    gmv_by_zone = orders.groupby('zone')['gross_amount'].sum().sort_values(ascending=False)
    fig_zone = px.bar(gmv_by_zone, x=gmv_by_zone.index, y=gmv_by_zone.values, labels={'x':'Zone', 'y':'GMV'})
    st.plotly_chart(fig_zone, use_container_width=True)
    
    # Example Donut Chart: GMV by Cuisine
    gmv_by_cuisine = orders.groupby('cuisine_type')['gross_amount'].sum()
    fig_cuisine = px.pie(values=gmv_by_cuisine.values, names=gmv_by_cuisine.index, hole=0.4)
    st.plotly_chart(fig_cuisine, use_container_width=True)
    
# ------------------------------
# 5. Manager View
# ------------------------------
else:
    st.title("Manager Dashboard")
    
    # Example KPI: On-Time Delivery Rate
    on_time = delivery_events[delivery_events['actual_delivery_time_mins'] <= delivery_events['estimated_delivery_time']]
    on_time_rate = len(on_time) / len(delivery_events) * 100
    st.metric(label="On-Time Delivery Rate (%)", value=f"{on_time_rate:.2f}%")
    
    # Example: Average Delivery Time
    avg_delivery = delivery_events['actual_delivery_time_mins'].mean()
    st.metric(label="Average Delivery Time (mins)", value=f"{avg_delivery:.1f}")
    
    # Example chart: Delay Breakdown by Zone
    delay_data = delivery_events.copy()
    delay_data['delay_type'] = np.where(delay_data['actual_delivery_time_mins'] > delay_data['estimated_delivery_time'], "Late", "On Time")
    delay_zone = delay_data.groupby(['zone', 'delay_type']).size().reset_index(name='count')
    fig_delay = px.bar(delay_zone, x='zone', y='count', color='delay_type', title="Delay Breakdown by Zone")
    st.plotly_chart(fig_delay, use_container_width=True)

# ------------------------------
# 6. Add What-If Analysis (Manager)
# ------------------------------
if view_toggle == "Manager View":
    st.subheader("What-If Analysis")
    prep_reduction = st.slider("Reduce Avg Prep Time by (mins)", 1, 15, 5)
    cancellation_reduction = st.slider("Reduce Cancellation Rate by (%)", 5, 30, 10)
    
    st.write(f"Projected improvement in on-time rate: +{prep_reduction * 0.5:.1f}%")  # dummy calc
    st.write(f"Projected GMV recovery from reduced cancellations: AED {gmv * cancellation_reduction/100:,.0f}")

