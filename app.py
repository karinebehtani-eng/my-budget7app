import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Karine Budget", page_icon="📊", layout="wide")
st.title("📊 Mon Application de Budget")

FILE_NAME = "karine essaie 1.xlsm.xlsx"

# 2. Load Data Function
@st.cache_data
def load_summary():
    df = pd.read_excel(FILE_NAME, sheet_name='Full Year')
    df_months = df.iloc[0:12].copy()
    
    cols_to_numeric = ['Salaires', 'Mis à dispo (€)', 'Expenses (€)', 'Debt (€)', 'Savings (€)', 'Casual (€)', 'Net Balance (€)']
    for col in cols_to_numeric:
        if col in df_months.columns:
            df_months[col] = pd.to_numeric(df_months[col], errors='coerce').fillna(0)
    return df_months

try:
    data = load_summary()
    
    # 3. KPI / Metrics Cards
    st.subheader("📌 Aperçu Annuel (Cumulé)")
    total_income = data['Mis à dispo (€)'].sum()
    total_expenses = data['Expenses (€)'].sum() + data['Casual (€)'].sum()
    total_savings = data['Savings (€)'].sum()
    total_net = data['Net Balance (€)'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenus Disponibles", f"{total_income:,.2f} €")
    c2.metric("Dépenses Totales", f"{total_expenses:,.2f} €")
    c3.metric("Épargne Totale", f"{total_savings:,.2f} €")
    c4.metric("Solde Net Restant", f"{total_net:,.2f} €")
    
    st.write("---")
    
    # 4. Interactive Chart (Using Streamlit's built-in chart!)
    st.subheader("📈 Évolution Mensuelle")
    chart_cols = ['Mis à dispo (€)', 'Expenses (€)', 'Casual (€)', 'Savings (€)']
    chart_data = data[['Month'] + [c for c in chart_cols if c in data.columns]].set_index('Month')
    st.line_chart(chart_data)
    
    st.write("---")
    
    # 5. Monthly Deep Dive Dropdown
    st.subheader("🔍 Détail d'un Mois Spécifique")
    selected_month = st.selectbox("Sélectionnez un mois :", data['Month'].unique())
    
    month_df = pd.read_excel(FILE_NAME, sheet_name=selected_month)
    st.dataframe(month_df.dropna(how='all'), use_container_width=True)

except Exception as e:
    st.error(f"Erreur : {e}")
    
