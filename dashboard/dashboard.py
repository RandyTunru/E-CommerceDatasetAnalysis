import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

def sellers_revenue(df):
    condition = df.order_status == "delivered"

    sellers_revenue_df = df[condition].groupby("seller_id").agg({
        "order_id": "nunique",
        "price": "sum"
    }).sort_values(by="price", ascending=False).reset_index().head(5)
    sellers_revenue_df = sellers_revenue_df.rename(columns={'price': 'revenue'})
    return sellers_revenue_df

def category_performace(df):
    canceled_condition = ["canceled", "unavailable"]

    indices_to_drop = df[df['order_status'].isin(canceled_condition)].index

    uncanceled_orders_df = df.drop(indices_to_drop)

    category_performance_df = uncanceled_orders_df.groupby("product_category_name_english").order_id.nunique().reset_index()
    category_performance_df = category_performance_df.rename(columns={'order_id': 'order_amount'})
    return category_performance_df

def rfm(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].max()
    
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

all_df = pd.read_csv('dashboard\main_df.csv')

all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"]).dt.date

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.header("E-Commerce Dashboard")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

start_date = pd.to_datetime(start_date).date()
end_date = pd.to_datetime(end_date).date()


main_df = all_df[((all_df["order_purchase_timestamp"] <= end_date) | (all_df["order_purchase_timestamp"] == end_date)) & (all_df["order_purchase_timestamp"] >= start_date)]


sellers_revenue_df = sellers_revenue(main_df)
category_performance_df = category_performace(main_df)
rfm_df = rfm(main_df)

st.header('E-Commerce Dashboard :sparkles:')

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

st.subheader('Top 5 Sellers by Revenue')
col1, col2 = st.columns(2)

with col1:
    total_orders = sellers_revenue_df.order_id.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(sellers_revenue_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

plt.figure(figsize=(10, 5))
sns.barplot(data=sellers_revenue_df, x="seller_id", y="revenue", palette=colors)

plt.xticks(rotation=45, ha='right')

plt.title("Top 5 Sellers by Revenue")

st.pyplot(plt)

st.subheader('Category Performance')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35,15))

sns.barplot(x="order_amount", y="product_category_name_english", data=category_performance_df.sort_values("order_amount", ascending=False).head(5), palette=colors, hue="product_category_name_english", ax=ax[0], linewidth=2)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Category", loc="center", fontsize=15)
ax[0].legend().remove()

sns.barplot(x="order_amount", y="product_category_name_english", data=category_performance_df.sort_values("order_amount").head(5), palette=colors, hue="product_category_name_english", ax=ax[1], linewidth=2)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("Worst Performing Category", loc="center", fontsize=15)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].legend().remove()

plt.suptitle("Best and Worst Performing Category by Number of Sales", fontsize=20)

st.pyplot(fig)

st.subheader('RFM Analysis')

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35,15))

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15, rotation=45)


sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15, rotation=45)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=45)

for axes in ax:
  for label in axes.get_xticklabels():
      label.set_horizontalalignment('right')

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)

st.pyplot(fig)