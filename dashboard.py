import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# 2. Judul dan Deskripsi
st.title("💰 Personal Finance Analysis Dashboard")
st.markdown("""
Dashboard ini menganalisis pola pengeluaran harian dan pencapaian target bulanan.
Fokus utama: **Analisis Perilaku Akhir Pekan** dan **Tren Momentum (Lag Analysis)**.
""")

# 3. Load Data
@st.cache_data
def load_data():
    # Pastikan file CSV Anda bernama 'dataset.csv' atau ganti sesuai nama file Anda
    df = pd.read_csv('dataset.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()

    # --- SIDEBAR: FILTER ---
    st.sidebar.header("Filter & Target")
    list_month = df['Month'].unique()
    selected_month = st.sidebar.selectbox("Pilih Bulan", options=list_month)
    target_bulanan = st.sidebar.number_input("Target Budget Bulanan (IDR)", value=5000000)

    # Filter data berdasarkan bulan terpilih
    df_filtered = df[df['Month'] == selected_month].sort_values('Date')

    # --- ROW 1: KPI METRICS ---
    # Menghitung angka untuk SMART Question
    total_income = df_filtered['Income'].sum()
    total_spent = df_filtered['Amount_IDR'].sum()
    budget_remaining = target_bulanan - total_spent
    avg_daily_spent = df_filtered['Amount_IDR'].mean()
    
    # Menghitung kenaikan % Weekend vs Weekday (untuk SMART Question 1)
    avg_weekend = df_filtered[df_filtered['is_weekend'] == 1]['Amount_IDR'].mean()
    avg_weekday = df_filtered[df_filtered['is_weekend'] == 0]['Amount_IDR'].mean()
    weekend_increase = ((avg_weekend - avg_weekday) / avg_weekday) * 100 if avg_weekday > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pengeluaran", f"Rp {total_spent:,.0f}")
    col2.metric("Sisa Budget", f"Rp {budget_remaining:,.0f}", delta=f"{- (total_spent/target_bulanan)*100:.1f}% dari target")
    col3.metric("Rata-rata Harian", f"Rp {avg_daily_spent:,.0f}")
    col4.metric("Kenaikan Akhir Pekan", f"{weekend_increase:.1f}%", help="Persentase kenaikan rata-rata belanja di akhir pekan dibanding hari kerja")

    st.divider()

    # --- ROW 2: LINE CHART (TRENS & MOMENTUM) ---
    st.subheader("📈 Tren Pengeluaran: Aktual vs Minggu Lalu")
    st.info("Analisis ini menjawab apakah pengeluaran Anda hari ini mengikuti pola yang sama dengan minggu lalu (Lag 7).")
    
    # Visualisasi Tren Aktual vs Lag 7
    fig_trend = px.line(df_filtered, x='Date', y=['Amount_IDR', 'Amount_IDR_lag_7'],
                        labels={'value': 'Jumlah (IDR)', 'Date': 'Tanggal', 'variable': 'Kategori'},
                        title="Perbandingan Pengeluaran Harian vs Pola Mingguan",
                        line_shape="linear")
    
    # Mempercantik tampilan garis
    fig_trend.update_traces(line=dict(width=3))
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- ROW 3: BAR CHART (BEHAVIORAL ANALYSIS) ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Rata-rata: Hari Kerja vs Akhir Pekan")
        # Mengelompokkan data is_weekend
        weekend_data = df_filtered.groupby('is_weekend')['Amount_IDR'].mean().reset_index()
        weekend_data['is_weekend'] = weekend_data['is_weekend'].map({0: 'Hari Kerja', 1: 'Akhir Pekan'})
        
        fig_weekend = px.bar(weekend_data, x='is_weekend', y='Amount_IDR',
                             color='is_weekend', 
                             text_auto='.2s',
                             title="Mana yang Lebih Boros?",
                             labels={'Amount_IDR': 'Rata-rata Pengeluaran (IDR)', 'is_weekend': ''})
        st.plotly_chart(fig_weekend, use_container_width=True)

    with col_right:
        st.subheader("📅 Rata-rata per Hari dalam Seminggu")
        # Urutan hari agar rapi
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_avg = df_filtered.groupby('Day_of_week')['Amount_IDR'].mean().reindex(day_order).reset_index()
        
        fig_day = px.bar(day_avg, x='Day_of_week', y='Amount_IDR',
                         title="Pola Pengeluaran Mingguan",
                         color='Amount_IDR',
                         labels={'Amount_IDR': 'Rata-rata (IDR)', 'Day_of_week': 'Hari'})
        st.plotly_chart(fig_day, use_container_width=True)

    # --- ROW 4: SMART INSIGHTS ---
    st.divider()
    st.subheader("💡 Kesimpulan Analisis (Action Oriented)")
    
    # Logika sederhana untuk memberikan insight otomatis
    if weekend_increase > 20:
        st.warning(f"**Insight:** Pengeluaran akhir pekan Anda lebih tinggi {weekend_increase:.1f}% dari hari kerja. Pertimbangkan untuk membatasi budget hiburan.")
    else:
        st.success("**Insight:** Pengeluaran akhir pekan Anda terjaga dan stabil dibandingkan hari kerja.")

    if total_spent > target_bulanan:
        st.error(f"**Status Target:** Anda sudah melampaui target bulanan sebesar Rp {abs(budget_remaining):,.0f}!")
    else:
        st.info(f"**Status Target:** Anda masih memiliki sisa Rp {budget_remaining:,.0f} untuk bulan ini.")

except Exception as e:
    st.error(f"Gagal memuat data. Pastikan file 'dataset.csv' sudah ada. Error: {e}")
