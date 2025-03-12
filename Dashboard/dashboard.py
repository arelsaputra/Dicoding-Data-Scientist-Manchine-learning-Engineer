import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import numpy as np

st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")
st.title("Dashboard E-Commerce")
st.markdown("---")

URL_GITHUB = "https://raw.githubusercontent.com/arelsaputra/Dicoding-Data-Scientist-Manchine-learning-Engineer/refs/heads/main/Dashboard/main_data.csv"

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(URL_GITHUB)

        if 'order_purchase_timestamp' in data.columns:
            data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'], errors='coerce')

        return data
    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")
        return None

dataset = load_data()

if dataset is not None:
    st.subheader("Contoh Data dari main_data.csv")
    st.write(dataset.head())

    st.sidebar.header("Filter Data")
    selected_category = st.sidebar.selectbox("Pilih Kategori Produk:", options=dataset['product_category_name'].dropna().unique())
    date_range = st.sidebar.date_input("Pilih Rentang Tanggal:", [])
    price_range = st.sidebar.slider("Pilih Rentang Harga:", float(dataset['price'].min()), float(dataset['price'].max()), (float(dataset['price'].min()), float(dataset['price'].max())))
    selected_rating = st.sidebar.slider("Pilih Rentang Rating:", 1, 5, (1, 5))
    selected_payment = st.sidebar.multiselect("Pilih Metode Pembayaran:", options=dataset['payment_type'].dropna().unique())
    selected_city = st.sidebar.multiselect("Pilih Kota Pembeli:", options=dataset['customer_city'].dropna().unique())

    filtered_data = dataset[dataset['product_category_name'] == selected_category]

    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_data = filtered_data[(filtered_data['order_purchase_timestamp'] >= start_date) & 
                                      (filtered_data['order_purchase_timestamp'] <= end_date)]

    filtered_data = filtered_data[(filtered_data['price'] >= price_range[0]) & (filtered_data['price'] <= price_range[1])]
    filtered_data = filtered_data[(filtered_data['review_score'] >= selected_rating[0]) & (filtered_data['review_score'] <= selected_rating[1])]
    
    if selected_payment:
        filtered_data = filtered_data[filtered_data['payment_type'].isin(selected_payment)]
    if selected_city:
        filtered_data = filtered_data[filtered_data['customer_city'].isin(selected_city)]

    st.sidebar.write(f"Jumlah Data yang Sesuai: {len(filtered_data)}")

    st.subheader("Tren Penjualan Bulanan")
    if 'order_purchase_timestamp' in dataset.columns:
        dataset['month'] = dataset['order_purchase_timestamp'].dt.to_period('M').astype(str)
        sales_trend = dataset.groupby('month').size().reset_index(name='count')

        fig = px.line(sales_trend, x='month', y='count', title="Tren Penjualan Bulanan",
                      labels={'month': 'Bulan', 'count': 'Jumlah Transaksi'}, markers=True)
        st.plotly_chart(fig)

    st.subheader("10 Produk Kategori yang Paling Banyak Terjual")
    product_sales = dataset.groupby('product_category_name').size().reset_index(name='count')
    product_sales = product_sales.sort_values(by='count', ascending=False).head(10)

    fig2 = px.bar(product_sales, y='product_category_name', x='count', orientation='h',
                  labels={'count': 'Jumlah Produk Terjual', 'product_category_name': 'Kategori Produk'},
                  title="10 Produk Kategori yang Paling Banyak Terjual", color='count')
    st.plotly_chart(fig2)

    st.subheader("Word Cloud: Distribusi Kategori Produk")
    dataset['product_category_name'] = dataset['product_category_name'].astype(str)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(dataset['product_category_name']))
    
    plt.figure(figsize=(10,5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
    plt.show()

    st.subheader("Heatmap Korelasi Antar Variabel")
    correlation_matrix = dataset.select_dtypes(include=[np.number]).corr()
    
    plt.figure(figsize=(10,6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
    st.pyplot(plt)
    plt.show()

    st.markdown("---")
    st.subheader("Statistik Ringkasan")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transaksi", f"{dataset.shape[0]}")
    col2.metric("Total Produk Unik", f"{dataset['product_id'].nunique()}")
    col3.metric("Total Seller", f"{dataset['seller_id'].nunique()}")
    col4.metric("Total Pendapatan", f"Rp {dataset['payment_value'].sum():,.2f}")

    st.markdown("---")

    st.subheader("Data Setelah Filter")
    st.write(filtered_data.head(10))

else:
    st.error("Gagal memuat data dari main_data.csv.")
