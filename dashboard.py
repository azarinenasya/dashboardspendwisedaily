import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# 2. Load Data (Ganti dengan file Anda)
# df = pd.read_csv('your_data.csv')
# Simulasi format data berdasarkan kolom yang Anda miliki:
@st.cache_data
def load_data():
    # Pastikan kolom Date bertipe datetime
    # df['Date'] = pd.to_datetime(df['Date'])
    return pd.read_csv('your_dataset.csv') # Sesuaikan nama file

# --- Judul Dashboard ---
st.title("💰 Personal Finance Analysis Dashboard")
st.markdown("Fokus: Efisiensi Harian & Analisis Momentum")

# 3. Sidebar untuk Filter & Input Target
st.sidebar.header("Pengaturan Budget")
target_bulanan = st.sidebar.number_input("Target Budget Bulanan (IDR)", value=5000000)
selected_month = st.sidebar.selectbox("Pilih Bulan", options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], index=0)

# 4. Filter Data Berdasarkan Bulan
# df_filtered = df[df['Month'] == selected_month]

# 5. Row 1: KPI Metrics (SMART Metrics)
col1, col2, col3, col4 = st.columns(4)

# Simulasi Kalkulasi
total_spent = 3200000 # Contoh: df_filtered['Amount_IDR'].sum()
avg_daily = 110000 # Contoh: df_filtered['Amount_IDR'].mean()
budget_left = target_bulanan - total_spent
burn_rate = (total_spent / target_bulanan) * 100

with col1:
    st.metric("Total Pengeluaran", f"Rp {total_spent:,}")
with col2:
    st.metric("Sisa Anggaran", f"Rp {budget_left:,}", delta_color="normal")
with col3:
    st.metric("Rata-rata Harian", f"Rp {avg_daily:,}")
with col4:
    st.metric("Budget Terpakai", f"{burn_rate:.1f}%")

st.divider()

# 6. Row 2: Tren Harian vs Minggu Lalu (Momentum Analysis)
st.subheader("📈 Analisis Momentum: Hari Ini vs Minggu Lalu")
st.caption("Membandingkan pengeluaran harian dengan pola 7 hari sebelumnya (Lag 7)")

# Plotly Line Chart
# fig_trend = px.line(df_filtered, x='Date', y=['Amount_IDR', 'Amount_IDR_lag_7'], 
#                    labels={'value': 'Jumlah (IDR)', 'Date': 'Tanggal'},
#                    title="Actual Spending vs 7-Day Lag")
# st.plotly_chart(fig_trend, use_container_width=True)

# 7. Row 3: Perbandingan Weekend & Hari Kerja (Behavioral Analysis)
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Weekend vs Weekday")
    # Contoh data bar chart
    # weekend_avg = df_filtered.groupby('is_weekend')['Amount_IDR'].mean().reset_index()
    # fig_weekend = px.bar(weekend_avg, x='is_weekend', y='Amount_IDR', 
    #                     color='is_weekend', text_auto='.2s',
    #                     labels={'is_weekend': 'Akhir Pekan (1=Ya)', 'Amount_IDR': 'Rata-rata (IDR)'})
    # st.plotly_chart(fig_weekend, use_container_width=True)
    st.info("Memberikan gambaran apakah Anda cenderung konsumtif di hari libur.")

with col_right:
    st.subheader("📅 Pengeluaran per Hari")
    # day_avg = df_filtered.groupby('Day_of_week')['Amount_IDR'].mean().sort_values()
    # fig_day = px.bar(day_avg, orientation='h', color_discrete_sequence=['#636EFA'])
    # st.plotly_chart(fig_day, use_container_width=True)
    st.info("Melihat hari spesifik yang memiliki rata-rata pengeluaran tertinggi.")

# 8. Row 4: Status Target (Action Oriented)
st.divider()
st.subheader("🎯 Status Target Bulanan")

if burn_rate > 90:
    st.error(f"Peringatan: Anda telah menghabiskan {burn_rate:.1f}% anggaran. Batasi pengeluaran non-primer!")
elif burn_rate > 70:
    st.warning(f"Perhatian: Anggaran terpakai sudah {burn_rate:.1f}%. Tetap waspada.")
else:
    st.success(f"Aman: Anggaran baru terpakai {burn_rate:.1f}%.")

# Tabel Detail (Opsi: Hanya tampilkan 5 transaksi terbesar)
st.write("### 5 Pengeluaran Terbesar Bulan Ini")
# top_5 = df_filtered.sort_values(by='Amount_IDR', ascending=False).head(5)
# st.table(top_5[['Date', 'Amount_IDR', 'Day_of_week']])
