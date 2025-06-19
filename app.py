import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os

st.set_page_config(layout="centered", page_title="Seu Patrimônio")

# Nome do arquivo local para persistência
dados_path = "dados_investimentos.xlsx"

# Função para exibir o gráfico de rosca
def exibir_grafico(df, filtro):
    grupo = df.groupby(filtro)['Valor'].sum()
    grupo = grupo[grupo > 0].sort_values(ascending=False)

    if grupo.empty:
        st.warning("Nenhum dado para exibir.")
        return

    valores = grupo.values
    categorias = grupo.index.tolist()
    total = sum(valores)

    cores_paleta = ['#4A90E2', '#F5A623', '#D0021B', '#50E3C2', '#B8E986', '#9013FE', '#FF3366']
    cores = cores_paleta * ((len(valores) // len(cores_paleta)) + 1)

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, _ = ax.pie(
        valores,
        colors=cores[:len(valores)],
        startangle=90,
        radius=1,
        wedgeprops=dict(width=0.4, edgecolor='white')
    )

    total_formatado = f"R$ {total:,.0f}".replace(",", ".")
    ax.text(0, 0, total_formatado, ha='center', va='center', fontsize=16, fontweight='bold', color='black')

    ax.axis('equal')
    plt.box(False)
    st.pyplot(fig)

    # Legenda responsiva ordenada do maior para o menor
    st.markdown("---")
    legenda = sorted(zip(categorias, valores, cores), key=lambda x: x[1], reverse=True)

    max_por_linha = 4
    total_itens = len(legenda)
    linhas = (total_itens + max_por_linha - 1) // max_por_linha

    for linha_index in range(linhas):
        inicio = linha_index * max_por_linha
        fim = min(inicio + max_por_linha, total_itens)
        linha = legenda[inicio:fim]
        cols = st.columns(max_por_linha)
        for i in range(max_por_linha):
            if i < len(linha):
                categoria, _, cor = linha[i]
                with cols[i]:
                    st.markdown(f"<div style='display:flex;align-items:center;margin-bottom:4px;'>"
                                f"<div style='width:14px;height:14px;background:{cor};border-radius:3px;border:1px solid #ccc;margin-right:6px'></div>"
                                f"<span style='font-size:13px;font-family:sans-serif'>{categoria}</span></div>", unsafe_allow_html=True)
            else:
                with cols[i]:
                    st.markdown("&nbsp;", unsafe_allow_html=True)

# Upload e aba
with st.sidebar:
    uploaded_file = st.file_uploader("📁 Upload Excel", type="xlsx", help="Excel com colunas: Empresa, Tipo de Investimento, Valor")

# Lógica de leitura
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        if all(col in df.columns for col in ['Empresa', 'Tipo de Investimento', 'Valor']):
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            df.to_excel(dados_path, index=False)
        else:
            st.error("Colunas obrigatórias não encontradas no Excel.")
            df = pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        df = pd.DataFrame()
elif os.path.exists(dados_path):
    df = pd.read_excel(dados_path)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
else:
    df = pd.DataFrame()

if not df.empty:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 0;'>
        <h4 style="font-weight: normal; margin-top: 0px;">Total da carteira</h4>
    </div>
    """, unsafe_allow_html=True)

    cols_tabs = st.columns([1, 1])
    with cols_tabs[0]:
        with st.container():
            aba1, _ = st.tabs(["Produtos", ""])
    with cols_tabs[1]:
        with st.container():
            _, aba2 = st.tabs(["", "Carteiras"])

    with aba1:
        exibir_grafico(df, "Tipo de Investimento")
    with aba2:
        exibir_grafico(df, "Empresa")
else:
    st.info("Por favor, envie um arquivo Excel para visualizar o gráfico.")
