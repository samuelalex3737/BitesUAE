# BitesUAE – Food Delivery CX & Operations Dashboard

## 📌 Project Overview
This project analyzes customer experience and operational performance for **BitesUAE**, a UAE-based food delivery platform operating across Dubai, Abu Dhabi, Sharjah, and Ajman.

The dashboard supports two audiences:
- **Executive View** – GMV, customer behavior, discount effectiveness
- **Manager View** – delivery performance, delays, cancellations, and operational bottlenecks

---

## 🧩 Business Objectives
- Track GMV trends and top-performing zones & cuisines
- Measure repeat customer behavior
- Evaluate promo discount burn rates
- Identify delivery delays and cancellation drivers
- Support operational decision-making using what-if analysis

---

## 🗂️ Dataset Description
The project uses **6 relational datasets**:

| File | Description |
|----|----|
| customers.csv | Customer profiles and segmentation |
| restaurants.csv | Restaurant metadata, cuisine, prep time |
| riders.csv | Delivery rider details |
| orders.csv | Order transactions |
| order_items.csv | Item-level order details |
| delivery_events.csv | Delivery timeline and performance |

Primary and foreign keys are maintained across all tables.

---

## 🔑 Key KPIs
### Executive KPIs
- GMV (Gross Merchandise Value)
- Average Order Value (AOV)
- Repeat Customer Rate
- Discount Burn Rate

### Operational KPIs
- On-Time Delivery Rate
- Average Delivery Time
- Cancellation Rate
- Delay Breakdown by Zone

---

## 🧠 Data Assumptions & Cleaning
- Cancelled orders have no delivered time
- Missing discount values are treated as zero
- Orders are considered on-time if:
