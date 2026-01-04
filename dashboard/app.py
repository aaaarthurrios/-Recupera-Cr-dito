import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Recupera Crédito",
    page_icon="📊",
    layout="wide"
)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(__file__)
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")
CSS_PATH = os.path.join(BASE_DIR, "styles.css")

# ---------------- CSS ----------------
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .kpi-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e6e9ef;
        }
        .kpi-card h3 {
            margin: 0;
            font-size: 16px;
            color: #555;
        }
        .kpi-card h2 {
            margin-top: 10px;
            font-size: 28px;
            color: #000;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------- HEADER ----------------
col_logo, col_title = st.columns([1, 5])

with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=90)

with col_title:
    st.markdown("""
        <h1 style="margin-bottom:0;">Recupera Crédito</h1>
        <p style="margin-top:0; color:gray;">
        📊 Análise inteligente de inadimplência e recuperação
        </p>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, use_container_width=True)
    st.sidebar.markdown("---")

st.sidebar.title("🔎 Filtros")

uploaded_file = st.sidebar.file_uploader(
    "📂 Envie a base de clientes",
    type=["csv"]
)

# ---------------- LOAD DATA ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    try:
        data_path = os.path.join(BASE_DIR, "data", "dados_credito.csv")
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        st.warning("⚠️ Base não encontrada. Usando dados de exemplo.")
        df = pd.DataFrame({
            "score_credito": [850, 400, 300, 600, 720, 250],
            "dias_atraso": [5, 90, 120, 30, 10, 150],
            "valor_divida": [1000, 5000, 12000, 2500, 800, 20000]
        })

# ---------------- VALIDAÇÃO ----------------
colunas_necessarias = ["score_credito", "dias_atraso", "valor_divida"]

for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"❌ Coluna obrigatória ausente: {col}")
        st.stop()

# ---------------- PROBABILIDADE ----------------
max_dias = df["dias_atraso"].max() or 1

df["prob_recuperacao"] = (
    (df["score_credito"] / 1000) *
    (1 - df["dias_atraso"] / max_dias)
).clip(0, 1)

# ---------------- FILTROS ----------------
score_range = st.sidebar.slider(
    "Score de Crédito",
    int(df["score_credito"].min()),
    int(df["score_credito"].max()),
    (
        int(df["score_credito"].min()),
        int(df["score_credito"].max())
    )
)

df_filtrado = df[df["score_credito"].between(*score_range)]

# ---------------- KPIs ----------------
col1, col2, col3 = st.columns(3)

col1.markdown(
    f"""
    <div class="kpi-card">
        <h3>Total de Clientes</h3>
        <h2>{len(df_filtrado)}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

col2.markdown(
    f"""
    <div class="kpi-card">
        <h3>Dívida Média</h3>
        <h2>R$ {df_filtrado['valor_divida'].mean():,.2f}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

clientes_recuperaveis = (df_filtrado["prob_recuperacao"] >= 0.6).sum()
col3.markdown(
    f"""
    <div class="kpi-card">
        <h3>Clientes Recuperáveis</h3>
        <h2>{clientes_recuperaveis}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- GRÁFICOS ----------------
st.markdown("## 📈 Análises")

if not df_filtrado.empty:
    col_g1, col_g2 = st.columns(2)

    # HISTOGRAMA
    with col_g1:
        fig_hist = px.histogram(
            df_filtrado,
            x="score_credito",
            nbins=20,
            title="Distribuição de Score de Crédito",
            template="plotly_dark"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # GRÁFICO DE PIZZA (DONUT)
    with col_g2:
        df_filtrado["faixa_score"] = pd.cut(
            df_filtrado["score_credito"],
            bins=[0, 300, 500, 700, 1000],
            labels=["Muito Baixo", "Baixo", "Médio", "Alto"]
        )

        divida_por_faixa = (
            df_filtrado
            .groupby("faixa_score", observed=True)["valor_divida"]
            .sum()
            .reset_index()
        )

        fig_pizza = px.pie(
            divida_por_faixa,
            names="faixa_score",
            values="valor_divida",
            title="💰 Distribuição da Dívida por Faixa de Score",
            hole=0.4,
            template="plotly_dark"
        )

        st.plotly_chart(fig_pizza, use_container_width=True)
else:
    st.info("Nenhum dado para exibir com os filtros atuais.")

# ---------------- TABELA ----------------
st.markdown("## 📋 Base de Dados")
st.dataframe(df_filtrado, use_container_width=True)
