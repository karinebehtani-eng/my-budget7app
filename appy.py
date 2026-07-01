import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Karine Budget", page_icon="📊", layout="wide")
st.title("📊 Mon Application de Budget")

FILE_NAME = "karine essaie 1.xlsm.xlsx"

# 2. Load Data Function
@st.cache_data
def load_summary():
    # Read the master annual sheet
    df = pd.read_excel(FILE_NAME, sheet_name='Full Year')
    # Filter rows 0 to 11 (January to December)
    df_months = df.iloc[0:12].copy()
    
    # Clean and convert columns to numbers so charts work perfectly
    cols_to_numeric = ['Salaires', 'Mis à dispo (€)', 'Expenses (€)', 'Debt (€)', 'Savings (€)', 'Casual (€)', 'Net Balance (€)']
    for col in cols_to_numeric:
        if col in df_months.columns:
            df_months[col] = pd.to_numeric(df_months[col], errors='coerce').fillna(0)
    return df_months

try:
    # Load data
    data = load_summary()
    
    # 3. KPI / Metrics Cards
    st.subheader("📌 Aperçu Annuel (Cumulé)")
    total_income = data['Mis à dispo (€)'].sum()
    total_expenses = data['Expenses (€)'].sum() + data['Casual (€)'].sum()
    total_savings = data['Savings (€)'].sum()
    total_net = data['Net Balance (€)'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenus Disponibles", f"{total_income:,.2f} €")
    c2.metric("Dépenses (Fixes + Casual)", f"{total_expenses:,.2f} €")
    c3.metric("Épargne Totale", f"{total_savings:,.2f} €")
    c4.metric("Solde Net Restant", f"{total_net:,.2f} €")
    
    st.write("---")
    
    # 4. Interactive Chart
    st.subheader("📈 Évolution Mensuelle")
    fig = px.line(data, x='Month', y=['Mis à dispo (€)', 'Expenses (€)', 'Casual (€)', 'Savings (€)'],
                  labels={'value': 'Montant (€)', 'variable': 'Catégorie'},
                  title="Tendances de vos finances au fil de l'année")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    
    # 5. Monthly Deep Dive Dropdown
    st.subheader("🔍 Détail d'un Mois Spécifique")
    selected_month = st.selectbox("Sélectionnez un mois pour voir l'onglet Excel correspondant :", data['Month'].unique())
    
    # Pull the exact sheet matching the user selection
    month_df = pd.read_excel(FILE_NAME, sheet_name=selected_month)
    st.dataframe(month_df.dropna(how='all'), use_container_width=True)

except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.info("Vérifiez que le nom de votre fichier Excel sur GitHub correspond exactement à 'karine essaie 1.xlsm.xlsx'")
