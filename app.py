import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(
    page_title="Dashboard Logística",
    page_icon="📊",
    layout="wide",   # <-- deixa a dashboard em tela cheia
    initial_sidebar_state="expanded"  # Sidebar aberta por padrão
)


# ======================
@st.cache_data(ttl=300)
def carregar_dados():
    sheet_url = "https://docs.google.com/spreadsheets/d/1e_8C_cSCamQk3FKe8mc8I29hpCXzRxLS/gviz/tq?sheet=Planilha1"
    res = requests.get(sheet_url)
    data_str = res.text
    json_str = data_str[47:-2]
    data_json = json.loads(json_str)

    rows = data_json["table"]["rows"]
    cols = [col["label"] for col in data_json["table"]["cols"]]

    df = pd.DataFrame([[c.get("v") if c else None for c in r["c"]] for r in rows], columns=cols)
    return df

df_raw = carregar_dados()
print(df_raw)

# ======================
# 🔹 Normalizar os dados
# ======================

# Converte para numérico onde precisa
for col in ["Peso", "Valor NFe", "Combustível", "Pedágio", "Despesas", "KM viagem"]:
    if col in df_raw.columns:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

# Agrupar por Manifesto
df_raw = df_raw.rename(columns=lambda x: x.strip())  # tira espaços extras
# soma todos as nfe de um manifesto


# Agrupa por Manifesto e Motorista
# Tabela principal (sem filial)
df_manifestos = df_raw[["Manifesto", "Motorista", "Qtd NF", "Peso Manifesto", "Valor Manifesto", "Despesas", "KM viagem"]]
df_manifestos = df_manifestos.drop_duplicates(subset=["Manifesto", "Motorista"])


# Preço do combustível e pedágio fixo
preco_combustivel = 6.02  # R$/km
valor_pedagio = 45.00      # R$ fixo por manifesto

# Cria coluna de Despesas Totais
df_manifestos["Despesas Totais"] = 0

# Calcula Custo por KM
df_manifestos["Custo por KM"] = df_manifestos["Despesas Totais"] / df_manifestos["KM viagem"]




# ======================
# 🔹 Dashboard Streamlit
# ======================

st.title("📊 Dashboard Logística")
col1, col2, col3, col4 = st.columns(4) # 4 colunas indicadores

# Filtros
motorista = st.selectbox("Selecione um motorista", ["Todos"] + df_manifestos["Motorista"].dropna().unique().tolist())
manifesto = st.selectbox("Selecione um manifesto", ["Todos"] + df_manifestos["Manifesto"].dropna().unique().tolist())

df_filtrado = df_manifestos.copy()


if motorista != "Todos":
    st.subheader(f"Motorista selecionado {motorista}")
    df_filtrado = df_filtrado[df_filtrado["Motorista"] == motorista]

if manifesto != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Manifesto"] == manifesto]

st.dataframe(df_filtrado)

# ======================
# 🔹 Tabelas Por filiais
# ======================
st.subheader("Despesas por filiais")



# ======================
# 🔹 KPIs
# ======================
# Indicadores
col1.metric("Total Manifestos", len(df_filtrado["Manifesto"].unique()))
col2.metric("Peso Total", f"{df_filtrado['Peso Manifesto'].sum():,.2f} kg")
col3.metric("Valor Total", f"R$ {df_filtrado['Valor Manifesto'].sum():,.2f}")
col4.metric("Despesas Totais", f"R$ {df_filtrado['Despesas'].sum():,.2f}")