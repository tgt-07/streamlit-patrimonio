import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import os

st.set_page_config(layout="centered", page_title="Seu Patrimônio")

st.markdown("""
    <div style='text-align: center;'>
        <h2 style="margin-bottom: 0">Seu patrimônio é:</h2>
    </div>
""", unsafe_allow_html=True)

# Upload de Excel
with st.sidebar:
    uploaded_file = st.file_uploader("\ud83d\udcc1 Upload Excel", type="xlsx", help="Excel com colunas: Empresa, Tipo de Investimento, Valor")
    filtro = st.selectbox("Visualizar por:", ["Tipo de Investimento", "Empresa"], index=0)

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

    limite_percentual = 5
    for i, w in enumerate(wedges):
        percentual_valor = (valores[i] / total) * 100
        if percentual_valor >= limite_percentual:
            angulo = (w.theta2 + w.theta1) / 2
            rad = np.deg2rad(angulo)
            r = 1 - 0.4 / 2
            x = r * np.cos(rad)
            y = r * np.sin(rad)

            valor_formatado = f"R$ {valores[i]:,.0f}".replace(",", ".")
            percentual = f"({round(percentual_valor)}%)"
            texto = f"{valor_formatado}\n{percentual}"

            ax.text(x, y, texto, ha='center', va='center', fontsize=9, fontweight='normal', color='black')

    total_formatado = f"R$ {total:,.0f}".replace(",", ".")
    ax.text(0, 0, total_formatado, ha='center', va='center', fontsize=16, fontweight='bold', color='black')

    ax.axis('equal')
    plt.box(False)
    st.pyplot(fig)

    # Legenda ordenada do maior para o menor
    st.markdown("---")
    legenda = list(zip(categorias, valores, cores))
    legenda.sort(key=lambda x: x[1], reverse=True)
    cols = st.columns(min(4, len(legenda)))
    for i, (categoria, _, cor) in enumerate(legenda):
        with cols[i % len(cols)]:
            st.markdown(f"<div style='display:flex;align-items:center;'>"
                        f"<div style='width:14px;height:14px;background:{cor};border-radius:3px;border:1px solid #ccc;margin-right:6px'></div>"
                        f"<span style='font-size:13px;font-family:sans-serif'>{categoria}</span></div>", unsafe_allow_html=True)

# Lógica de leitura
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        if all(col in df.columns for col in ['Empresa', 'Tipo de Investimento', 'Valor']):
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
            df.to_excel(dados_path, index=False)
            exibir_grafico(df, filtro)
        else:
            st.error("Colunas obrigatórias não encontradas no Excel.")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
elif os.path.exists(dados_path):
    df = pd.read_excel(dados_path)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)
    exibir_grafico(df, filtro)
else:
    st.info("Por favor, envie um arquivo Excel para visualizar o gráfico.")
