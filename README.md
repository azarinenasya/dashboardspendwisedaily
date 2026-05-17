# Personal Finance Tracker & Analysis Dashboard
Dashboard ini menyajikan analisis keuangan pribadi, fokus pada efisiensi pengeluaran harian, pola perilaku pengeluaran di akhir pekan, serta pengendalian anggaran terhadap target bulanan menggunakan metode time-series lag analysis.

## Setup Environment - Anaconda
```bash
conda create --name finance-tracker-env python=3.9
conda activate finance-tracker-env
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir personal_finance_dashboard
cd personal_finance_dashboard
pip install virtualenv
virtualenv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## requirements.txt
Anda dapat membuat file requirements.txt dengan konten berikut:
```
streamlit
pandas
matplotlib
seaborn
plotly
numpy
```

## Run Streamlit App
1. Simpan kode Streamlit Anda ke dalam sebuah file Python, misalnya dashboard.py.
2. Pastikan dataset Anda berada di direktori yang sama atau jalur (path) yang sesuai di dalam kode.
3. Jalankan aplikasi menggunakan perintah berikut di terminal:
```bash
streamlit run dashboard.py
```
