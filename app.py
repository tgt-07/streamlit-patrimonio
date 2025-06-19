import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os

st.set_page_config(layout="centered", page_title="Seu Patrimônio")

# Função para formatar valores em reais no padrão brasileiro (com casas decimais)
def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Função para formatar valores sem casas decimais (para rótulos do gráfico)
def formatar_reais_sem_centavos(valor):
    return f"R$ {int(round(valor)):,}".replace(",", ".")

# Nome do arquivo local para persistência
dados_path = "dados_investimentos.xlsx"

# Upload direto sem menu hamburguer
uploaded_file = st.file_uploader("📁 Upload Excel", type="xlsx", help="Excel com colunas: Empresa, Tipo de Investimento, Valor")

# Função para exibir o gráfico de rosca
def exibir_grafico(df, filtro):
    grupo = df.groupby(filtro)['Valor'].sum()
    grupo = grupo[grupo > 0].sort_values(ascending=False)

    if grupo.empty:
        st.warning("Nenhum dado para exibir.")
        return

    valores = grupo.values
    total = sum(valores)

    cores_paleta = ['#4A90E2', '#F5A623', '#D0021B', '#50E3C2', '#B8E986', '#9013FE', '#FF3366']
    cores = cores_paleta * ((len(valores) // len(cores_paleta)) + 1)

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts = ax.pie(
        valores,
        colors=cores[:len(valores)],
        startangle=90,
        radius=1,
        wedgeprops=dict(width=0.4, edgecolor='white')
    )

    total_formatado = formatar_reais(total)
    ax.text(0, 0, total_formatado, ha='center', va='center', fontsize=14, fontweight='bold', color='black')

    for i, p in enumerate(wedges):
        angulo = (p.theta2 + p.theta1) / 2
        rad = np.deg2rad(angulo)
        r = 1 - 0.4 / 2
        x = r * np.cos(rad)
        y = r * np.sin(rad)
        percentual_valor = (valores[i] / total) * 100
        if percentual_valor >= 5:
            valor_formatado = formatar_reais_sem_centavos(valores[i])
            percentual = f"({round(percentual_valor)}%)"
            ax.text(x, y, f"{valor_formatado}\n{percentual}", ha='center', va='center', fontsize=8, color='black')

    ax.axis('equal')
    plt.box(False)
    st.pyplot(fig)

    st.markdown("---")
    categorias = grupo.index.tolist()
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
    total_geral = df['Valor'].sum()
    total_formatado_superior = formatar_reais(total_geral)

    st.markdown(f"""
        <div style='text-align: center; margin-top: -20px; margin-bottom: 20px;'>
            <h4 style="font-weight: normal">Total da carteira</h4>
            <h2 style="margin-top: 0;">{total_formatado_superior}</h2>
        </div>
    """, unsafe_allow_html=True)

    aba = st.tabs(["Produtos", "Carteiras"])
    with aba[0]:
        exibir_grafico(df, "Tipo de Investimento")
    with aba[1]:
        exibir_grafico(df, "Empresa")
else:
    st.info("Por favor, envie um arquivo Excel para visualizar o gráfico.")
