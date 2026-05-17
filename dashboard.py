import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import calendar
from datetime import datetime, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Personal Finance Dashboard (DS Focus)",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Personal Finance Dashboard: Actionable Insights")
st.markdown("Dashboard ini dirancang untuk menyajikan wawasan keuangan yang mendorong aksi, bukan sekadar menampilkan data.")

# --- Dummy Data Generation ---
@st.cache_data
def generate_dummy_data(start_date, end_date):
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    data = {
        'Date': dates,
        'Amount_IDR': np.random.randint(50000, 1000000, size=len(dates)),
        'Income_IDR': np.random.randint(3000000, 15000000, size=len(dates)) / 30, # Daily income approximation
    }
    df = pd.DataFrame(data)
    # Add other necessary columns here to ensure consistency
    df['Day_of_week'] = df['Date'].dt.day_name()
    df['Day_of_month'] = df['Date'].dt.day
    df['is_weekend'] = df['Date'].dt.dayofweek.isin([5, 6]) # Saturday=5, Sunday=6
    df['Amount_IDR_lag_1'] = df['Amount_IDR'].shift(1)
    df['Amount_IDR_lag_7'] = df['Amount_IDR'].shift(7)
    return df

# Set default date range for dummy data
default_end_date = datetime.now()
default_start_date = default_end_date - timedelta(days=90)


# --- Sidebar ---
st.sidebar.header("Pengaturan Dashboard")

st.sidebar.markdown("---")
st.sidebar.subheader("Sumber Data")
uploaded_file = st.sidebar.file_uploader("Upload Dataset Terbaru (CSV)", type=["csv"])
google_drive_file_id = st.sidebar.text_input(
    "Atau masukkan Google Drive File ID untuk CSV publik",
    help="Contoh: 1vHBiYzWSCdtztGV1N6q7Io7oUj_gUA77. Pastikan file CSV di Google Drive bersifat publik dan dapat diakses tanpa login. Untuk mendapatkan link, klik 'Bagikan' > 'Dapatkan link' > 'Siapa saja yang memiliki link'. Salin ID dari URL."
)

df_raw = None
if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        st.sidebar.success("Data berhasil dimuat dari file yang diupload.")
    except Exception as e:
        st.sidebar.error(f"Gagal memuat data dari file yang diupload: {e}")
elif google_drive_file_id:
    try:
        csv_url = f"https://drive.google.com/uc?export=download&id={google_drive_file_id}"
        df_raw = pd.read_csv(csv_url)
        st.sidebar.success(f"Data berhasil dimuat dari Google Drive (ID: {google_drive_file_id}).")
    except Exception as e:
        st.sidebar.error(f"Gagal memuat data dari Google Drive: {e}. Pastikan ID benar dan file publik.")
else:
    st.sidebar.info("Menggunakan data dummy untuk demonstrasi. Silakan upload file CSV atau masukkan Google Drive ID.")

# If no data loaded from upload or drive, generate dummy data
if df_raw is None:
    df_raw = generate_dummy_data(default_start_date, default_end_date)


# --- Common Data Preprocessing for all data sources ---
df = df_raw.copy()

# Ensure 'Date' column is datetime
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
else:
    st.error("Kolom 'Date' tidak ditemukan dalam dataset. Harap pastikan dataset memiliki kolom 'Date'. Menggunakan dummy data.")
    df = generate_dummy_data(default_start_date, default_end_date) # Fallback to dummy if 'Date' is missing

# Ensure essential columns exist
required_columns = ['Amount_IDR', 'Income_IDR']
for col in required_columns:
    if col not in df.columns:
        st.error(f"Kolom '{col}' tidak ditemukan. Harap pastikan dataset memiliki kolom '{col}'. Menggunakan dummy data.")
        df = generate_dummy_data(default_start_date, default_end_date) # Fallback to dummy if critical column is missing
        break

# Create additional features
df['Day_of_week'] = df['Date'].dt.day_name()
df['Day_of_month'] = df['Date'].dt.day
df['is_weekend'] = df['Date'].dt.dayofweek.isin([5, 6])
df['Amount_IDR_lag_1'] = df['Amount_IDR'].shift(1)
df['Amount_IDR_lag_7'] = df['Amount_IDR'].shift(7)

# Sort by date to ensure correct lag calculations
df.sort_values('Date', inplace=True)

# --- Date filtering (Year & Month Selection) ---
if not df.empty:
    st.sidebar.subheader("Filter Periode")
    
    # Ambil daftar tahun yang unik
    df['Year'] = df['Date'].dt.year
    df['Month_Num'] = df['Date'].dt.month
    
    years = sorted(df['Year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("Pilih Tahun", years)

    # Filter bulan yang tersedia di tahun tersebut
    available_months_num = sorted(df[df['Year'] == selected_year]['Month_Num'].unique())
    
    # Mapping angka bulan ke nama bulan
    month_names = [calendar.month_name[m] for m in available_months_num]
    
    selected_month_name = st.sidebar.selectbox("Pilih Bulan", month_names)
    
    # Dapatkan kembali angka bulan dari nama yang dipilih
    selected_month_num = list(calendar.month_name).index(selected_month_name)

    # Proses Filtering Dataframe
    df_filtered = df[
        (df['Year'] == selected_year) & 
        (df['Month_Num'] == selected_month_num)
    ].copy()

    # Tampilkan info rentang tanggal yang sedang aktif di sidebar
    st.sidebar.caption(f"Menampilkan data untuk: {selected_month_name} {selected_year}")
else:
    df_filtered = pd.DataFrame()
    
# --- Data Preprocessing for Dashboard (Example) ---
if not df_filtered.empty:
    current_month_start = df_filtered['Date'].max().replace(day=1)
    df_current_month = df_filtered[df_filtered['Date'] >= current_month_start]
    total_spent_this_month = df_current_month['Amount_IDR'].sum()
    total_income_this_month = df_current_month['Income_IDR'].sum()
    avg_daily_spent = df_filtered['Amount_IDR'].mean()
    last_day_spent = df_filtered['Amount_IDR'].iloc[-1] if not df_filtered.empty else 0
    second_last_day_spent = df_filtered['Amount_IDR_lag_1'].iloc[-1] if len(df_filtered) > 1 else 0
else:
    total_spent_this_month = 0
    total_income_this_month = 0
    avg_daily_spent = 0
    last_day_spent = 0
    second_last_day_spent = 0


# --- 1. Fokus "Status & Kendali" (Monitoring KPI Utama) ---
st.header("1. Status & Kendali: Monitoring KPI Utama")
cols_kpi = st.columns(4)

with cols_kpi[0]:
    st.metric(
        label="Total Pengeluaran Bulan Ini",
        value=f"Rp {total_spent_this_month:,.0f}",
        delta=f"{(total_spent_this_month / monthly_target_budget * 100):.1f}% dari target" if monthly_target_budget > 0 else "N/A"
    )

with cols_kpi[1]:
    # Current vs Target Budget
    st.subheader("Progress Budget Bulanan")
    if monthly_target_budget > 0:
        progress_percent = min(100, (total_spent_this_month / monthly_target_budget) * 100)
    else:
        progress_percent = 0 # Handle division by zero
    st.progress(progress_percent, text=f"{progress_percent:.1f}% dari Rp {monthly_target_budget:,.0f}")
    if total_spent_this_month > monthly_target_budget:
        st.error("⚠️ Budget bulan ini sudah terlampaui!")
    elif progress_percent > 80:
        st.warning("❗ Mendekati batas budget bulan ini.")


with cols_kpi[2]:
    # Daily Velocity
    if not df_current_month.empty:
        # Calculate days in the current month (based on the max date in the filtered data)
        current_month = df_current_month['Date'].max().month
        current_year = df_current_month['Date'].max().year
        days_in_month = (datetime(current_year, current_month % 12 + 1, 1) - timedelta(days=1)).day if current_month < 12 else (datetime(current_year + 1, 1, 1) - timedelta(days=1)).day
        days_passed = df_current_month['Date'].nunique()
        remaining_days = days_in_month - days_passed

        if remaining_days > 0 and (monthly_target_budget - total_spent_this_month) > 0:
            allowed_daily_avg = (monthly_target_budget - total_spent_this_month) / remaining_days
        else:
            allowed_daily_avg = 0 # No remaining budget or days
    else:
        allowed_daily_avg = 0

    st.metric(
        label="Rata-rata Pengeluaran Harian (Sisa Bulan)",
        value=f"Rp {avg_daily_spent:,.0f}",
        delta=f"Target: Rp {allowed_daily_avg:,.0f}",
        delta_color="normal"
    )


with cols_kpi[3]:
    # Burn Rate (Monthly)
    if total_income_this_month > 0:
        burn_rate = (total_spent_this_month / total_income_this_month) * 100
    else:
        burn_rate = 0
    st.metric(
        label="Burn Rate Bulan Ini",
        value=f"{burn_rate:.1f}%",
        delta=f"Pengeluaran kemarin: Rp {last_day_spent:,.0f}", # DS Touch: delta from yesterday
        delta_color="inverse" if last_day_spent > second_last_day_spent else "normal"
    )


# --- 2. Fokus "Analisis Perilaku & Siklus" (Behavioral Patterns) ---
st.header("2. Analisis Perilaku & Siklus: Kapan dan Mengapa Boros?")
cols_behavior = st.columns(1)

with cols_behavior[0]:
    st.subheader("Dampak Akhir Pekan vs Hari Kerja")
    if not df_filtered.empty:
        avg_spent_by_day_type = df_filtered.groupby('is_weekend')['Amount_IDR'].mean().reset_index()
        avg_spent_by_day_type['Day_Type'] = avg_spent_by_day_type['is_weekend'].apply(lambda x: 'Akhir Pekan' if x else 'Hari Kerja')
        fig_weekend = px.bar(
            avg_spent_by_day_type,
            x='Day_Type',
            y='Amount_IDR',
            title='Rata-rata Pengeluaran: Akhir Pekan vs Hari Kerja',
            labels={'Amount_IDR': 'Rata-rata Pengeluaran (IDR)', 'Day_Type': 'Tipe Hari'}
        )
        st.plotly_chart(fig_weekend, use_container_width=True)
    else:
        st.info("Tidak ada data untuk menampilkan analisis perilaku.")

# --- 3. Fokus "Deteksi Anomali & Momentum" (Lag-based Insights) ---
st.header("3. Deteksi Anomali & Momentum: Apakah Pengeluaran Hari Ini Wajar?")

if not df_filtered.empty:
    st.subheader("Tren Pengeluaran vs Tren Mingguan (Lag-7)")
    fig_lag = go.Figure()
    fig_lag.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Amount_IDR'], mode='lines', name='Pengeluaran Aktual'))
    fig_lag.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Amount_IDR_lag_7'], mode='lines', name='Pengeluaran Minggu Lalu', line=dict(dash='dash')))

    fig_lag.update_layout(title='Pengeluaran Harian vs Pengeluaran 7 Hari Lalu',
                          xaxis_title='Tanggal',
                          yaxis_title='Pengeluaran (IDR)')
    st.plotly_chart(fig_lag, use_container_width=True)

    st.subheader("Deteksi Anomali (Z-Score Outlier)")
    df_recent = df_filtered.tail(30).copy()
    if len(df_recent) > 1 and df_recent['Amount_IDR'].std() > 0:
        mean_amount = df_recent['Amount_IDR'].mean()
        std_amount = df_recent['Amount_IDR'].std()
        df_recent['Z_Score'] = (df_recent['Amount_IDR'] - mean_amount) / std_amount
        outliers = df_recent[abs(df_recent['Z_Score']) > 2] 

        if not outliers.empty:
            st.warning("⚠️ Anomali Pengeluaran Terdeteksi! (Z-Score > 2)")
            for _, row in outliers.iterrows():
                st.write(f"Pada {row['Date'].strftime('%Y-%m-%d')}: Pengeluaran sebesar Rp {row['Amount_IDR']:,.0f} (Z-Score: {row['Z_Score']:.2f})")
        else:
            st.success("✅ Tidak ada anomali pengeluaran signifikan terdeteksi dalam 30 hari terakhir.")
    else:
        st.info("Tidak cukup data atau variasi pengeluaran untuk deteksi anomali Z-score yang bermakna.")
else:
    st.info("Tidak ada data untuk deteksi anomali.")


# --- 4. Fokus "Simulasi & Proyeksi" (Forward Looking) ---
st.header("4. Simulasi & Proyeksi: Kondisi Keuangan di Akhir Bulan")

if not df_filtered.empty:
    st.subheader("Proyeksi Pengeluaran Akhir Bulan")
    last_7_days_avg = df_filtered['Amount_IDR'].tail(7).mean()
    
    latest_date = df_filtered['Date'].max()
    
    next_month = latest_date.replace(day=1, month=latest_date.month % 12 + 1) if latest_date.month < 12 else latest_date.replace(year=latest_date.year + 1, month=1, day=1)
    last_day_of_month = next_month - timedelta(days=1)
    
    days_left_in_month = (last_day_of_month - latest_date).days

    if days_left_in_month < 0: 
        days_left_in_month = 0

    projected_spending_remaining = last_7_days_avg * days_left_in_month
    projected_total_spending_month = total_spent_this_month + projected_spending_remaining

    st.write(f"Rata-rata pengeluaran 7 hari terakhir: Rp {last_7_days_avg:,.0f}")
    st.write(f"Proyeksi pengeluaran sisa bulan ({days_left_in_month} hari): Rp {projected_spending_remaining:,.0f}")
    st.write(f"**Total Proyeksi Pengeluaran Bulan Ini:** Rp {projected_total_spending_month:,.0f}")

    # Simple projection chart
    future_dates = [latest_date + timedelta(days=i) for i in range(1, days_left_in_month + 1)]
    projected_df = pd.DataFrame({
        'Date': future_dates,
        'Amount_IDR': [last_7_days_avg] * len(future_dates)
    })

    # Combine actual and projected for plotting
    combined_df = pd.concat([df_filtered[['Date', 'Amount_IDR']], projected_df])
    combined_df = combined_df.sort_values('Date').reset_index(drop=True)

    fig_projection = px.line(combined_df, x='Date', y='Amount_IDR', title='Proyeksi Pengeluaran Harian')
    if not projected_df.empty:
        fig_projection.add_trace(go.Scatter(
            x=projected_df['Date'], y=projected_df['Amount_IDR'], mode='lines',
            name='Proyeksi', line=dict(dash='dot', color='red')
        ))
    st.plotly_chart(fig_projection, use_container_width=True)

    st.subheader("\"What-If\" Analysis: Kurangi Pengeluaran Akhir Pekan")
    reduction_percentage = st.slider("Kurangi pengeluaran akhir pekan sebesar (%) ", 0, 50, 20)

    # Calculate hypothetical savings
    df_weekends = df_filtered[df_filtered['is_weekend'] == True]
    if not df_weekends.empty:
        total_weekend_spending = df_weekends['Amount_IDR'].sum()
        potential_savings_weekend = total_weekend_spending * (reduction_percentage / 100)
        st.success(f"Jika Anda mengurangi pengeluaran akhir pekan sebesar {reduction_percentage}%, Anda berpotensi menghemat sekitar Rp {potential_savings_weekend:,.0f} dalam periode ini.")
    else:
        st.info("Tidak ada pengeluaran akhir pekan dalam data untuk simulasi.")

else:
    st.info("Tidak ada data untuk simulasi dan proyeksi.")


# --- DS Special: Smart Caption (Example) ---
st.header("DS Special: Wawasan Singkat Otomatis")

if not df_filtered.empty:
    avg_weekday_spent = df_filtered[df_filtered['is_weekend'] == False]['Amount_IDR'].mean()
    avg_weekend_spent = df_filtered[df_filtered['is_weekend'] == True]['Amount_IDR'].mean()

    if not pd.isna(avg_weekday_spent) and not pd.isna(avg_weekend_spent) and avg_weekday_spent > 0:
        weekend_vs_weekday_diff_percent = ((avg_weekend_spent - avg_weekday_spent) / avg_weekday_spent) * 100
        caption = f"Bulan ini, pengeluaran akhir pekan Anda **{weekend_vs_weekday_diff_percent:.1f}% {'lebih tinggi' if weekend_vs_weekday_diff_percent > 0 else 'lebih rendah'}** dari hari kerja."
        
        if 'projected_total_spending_month' in locals() and projected_total_spending_month is not None:
            if projected_total_spending_month > monthly_target_budget:
                caption += f" Jika tren ini berlanjut, Anda akan melampaui budget bulanan sebesar Rp {(projected_total_spending_month - monthly_target_budget):,.0f}."
            else:
                caption += f" Anda masih memiliki sisa budget Rp {(monthly_target_budget - projected_total_spending_month):,.0f} bulan ini."
        st.info(caption)
    else:
        st.info("Tidak cukup data atau rata-rata pengeluaran untuk menghasilkan smart caption yang bermakna.")
else:
    st.info("Tidak ada data untuk menghasilkan smart caption.")


# --- Layout Structure Reference (as per user request, mostly implemented above) ---
st.sidebar.markdown("---")
st.sidebar.subheader("Struktur Layout (Referensi)")
st.sidebar.markdown(
    """
    - **Sidebar**: Filter tanggal, input Target Bulanan, upload dataset.
    - **Row 1 (Header)**: KPI Metrics (Budget Left, Spending Today, Monthly Burn Rate).
    - **Row 2 (Main Trend)**: Interactive Line Chart (Amount_IDR vs Lag_7).
    - **Row 3 (Behavior)**: Kolom kiri (Bar Chart Weekend vs Weekday), Kolom kanan (Heatmap Day of Month).
    - **Row 4 (DS Special)**: Tabel berisi "Daftar Anomali" (output dari Z-score outlier).
    """
)
