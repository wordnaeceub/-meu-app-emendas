import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Dashboard Emendas Parlamentares DF",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CARREGAR DADOS
# ============================================================================

@st.cache_data
def carregar_dados():
    """Carrega os dados das emendas e ofícios"""
    emendas = pd.read_csv('02_Emendas_Preparadas.csv')
    oficios = pd.read_csv('02_Oficios_Preparados.csv')
    return emendas, oficios

# Carregar dados
emendas, oficios = carregar_dados()

# ============================================================================
# SIDEBAR - FILTROS
# ============================================================================

st.sidebar.title("🎯 Filtros")
st.sidebar.markdown("---")

# Filtro de Status
status_filter = st.sidebar.multiselect(
    "Status da Emenda",
    options=emendas['STATUS_EMENDA'].unique(),
    default=emendas['STATUS_EMENDA'].unique()
)

# Filtro de Unidade (Top 10)
top_unidades = emendas['UNIDADE'].value_counts().head(10).index.tolist()
unidade_filter = st.sidebar.multiselect(
    "Unidade",
    options=top_unidades,
    default=top_unidades[:3]
)

# Filtrar dados conforme seleção
emendas_filtrado = emendas[
    (emendas['STATUS_EMENDA'].isin(status_filter)) &
    (emendas['UNIDADE'].isin(unidade_filter))
]

# ============================================================================
# HEADER
# ============================================================================

st.markdown("# 📊 Dashboard - Sistematização de Emendas Parlamentares")
st.markdown("### Distrito Federal - Ciclo 2024-2025")
st.markdown("---")

# ============================================================================
# MÉTRICAS PRINCIPAIS (KPIs)
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de Emendas",
        len(emendas_filtrado),
        delta=f"{len(emendas)} registros"
    )

with col2:
    valor_total = emendas_filtrado['VALOR_EMENDA'].sum()
    st.metric(
        "Valor Total",
        f"R$ {valor_total:,.0f}",
        delta=f"Empenho: {emendas_filtrado['EMPENHADO'].sum():,.0f}"
    )

with col3:
    taxa_empenho = (emendas_filtrado['EMPENHADO'].sum() / emendas_filtrado['VALOR_EMENDA'].sum() * 100) if emendas_filtrado['VALOR_EMENDA'].sum() > 0 else 0
    st.metric(
        "Taxa de Empenho",
        f"{taxa_empenho:.1f}%",
        delta=f"Baseline: 66.11%"
    )

with col4:
    taxa_liquidacao = (emendas_filtrado['LIQUIDADO'].sum() / emendas_filtrado['VALOR_EMENDA'].sum() * 100) if emendas_filtrado['VALOR_EMENDA'].sum() > 0 else 0
    st.metric(
        "Taxa de Liquidação",
        f"{taxa_liquidacao:.1f}%",
        delta=f"Baseline: 41.83%"
    )

st.markdown("---")

# ============================================================================
# GRÁFICOS
# ============================================================================

col1, col2 = st.columns(2)

# Gráfico 1: Distribuição por Unidade
with col1:
    st.subheader("💰 Valor por Unidade")
    resumo_unidade = emendas_filtrado.groupby('UNIDADE')['VALOR_EMENDA'].sum().sort_values(ascending=False).head(10)

    fig1 = px.bar(
        x=resumo_unidade.values,
        y=resumo_unidade.index,
        orientation='h',
        labels={'x': 'Valor (R$)', 'y': 'Unidade'},
        color=resumo_unidade.values,
        color_continuous_scale='Blues'
    )
    fig1.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Distribuição por Status
with col2:
    st.subheader("📈 Status da Emenda")
    resumo_status = emendas_filtrado['STATUS_EMENDA'].value_counts()

    fig2 = px.pie(
        values=resumo_status.values,
        names=resumo_status.index,
        hole=0.3,
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

col1, col2 = st.columns(2)

# Gráfico 3: Execução Orçamentária
with col1:
    st.subheader("💳 Execução Orçamentária")

    execucao_data = {
        'Status': ['Valor Emenda', 'Empenhado', 'Liquidado'],
        'Valor': [
            emendas_filtrado['VALOR_EMENDA'].sum(),
            emendas_filtrado['EMPENHADO'].sum(),
            emendas_filtrado['LIQUIDADO'].sum()
        ]
    }
    execucao_df = pd.DataFrame(execucao_data)

    fig3 = px.bar(
        execucao_df,
        x='Status',
        y='Valor',
        color='Status',
        color_discrete_sequence=['#1f77b4', '#2ca02c', '#ff7f0e']
    )
    fig3.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Disponível vs Bloqueado
with col2:
    st.subheader("🔒 Bloqueado vs Disponível")

    bloqueio_data = {
        'Tipo': ['Bloqueado', 'Disponível'],
        'Valor': [
            emendas_filtrado['BLOQUEADO'].sum(),
            emendas_filtrado['DISPONIVEL'].sum()
        ]
    }
    bloqueio_df = pd.DataFrame(bloqueio_data)

    fig4 = px.bar(
        bloqueio_df,
        x='Tipo',
        y='Valor',
        color='Tipo',
        color_discrete_sequence=['#d62728', '#2ca02c']
    )
    fig4.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ============================================================================
# TABELA DE DADOS DETALHADA
# ============================================================================

st.subheader("📋 Dados Detalhados das Emendas")

# Selecionar colunas para exibir
colunas_exibir = [
    'NR_EMENDA', 'PARLAMENTAR', 'UNIDADE', 'VALOR_EMENDA',
    'EMPENHADO', 'LIQUIDADO', 'STATUS_EMENDA'
]

# Formatação para exibição
df_exibir = emendas_filtrado[colunas_exibir].copy()
df_exibir['VALOR_EMENDA'] = df_exibir['VALOR_EMENDA'].apply(lambda x: f"R$ {x:,.2f}")
df_exibir['EMPENHADO'] = df_exibir['EMPENHADO'].apply(lambda x: f"R$ {x:,.2f}")
df_exibir['LIQUIDADO'] = df_exibir['LIQUIDADO'].apply(lambda x: f"R$ {x:,.2f}")

st.dataframe(df_exibir, use_container_width=True, hide_index=True)

# ============================================================================
# ESTATÍSTICAS RESUMIDAS
# ============================================================================

st.markdown("---")
st.subheader("📊 Estatísticas Resumidas")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Valores por Emenda**")
    st.write(f"- Média: R$ {emendas_filtrado['VALOR_EMENDA'].mean():,.0f}")
    st.write(f"- Mediana: R$ {emendas_filtrado['VALOR_EMENDA'].median():,.0f}")
    st.write(f"- Máximo: R$ {emendas_filtrado['VALOR_EMENDA'].max():,.0f}")
    st.write(f"- Mínimo: R$ {emendas_filtrado['VALOR_EMENDA'].min():,.0f}")

with col2:
    st.write("**Execução Financeira**")
    st.write(f"- Total Empenho: R$ {emendas_filtrado['EMPENHADO'].sum():,.0f}")
    st.write(f"- Total Liquidado: R$ {emendas_filtrado['LIQUIDADO'].sum():,.0f}")
    st.write(f"- Total Bloqueado: R$ {emendas_filtrado['BLOQUEADO'].sum():,.0f}")
    st.write(f"- Total Disponível: R$ {emendas_filtrado['DISPONIVEL'].sum():,.0f}")

with col3:
    st.write("**Taxas de Execução**")
    st.write(f"- Empenho: {taxa_empenho:.1f}%")
    st.write(f"- Liquidação: {taxa_liquidacao:.1f}%")
    bloqueio_pct = (emendas_filtrado['BLOQUEADO'].sum() / emendas_filtrado['VALOR_EMENDA'].sum() * 100) if emendas_filtrado['VALOR_EMENDA'].sum() > 0 else 0
    st.write(f"- Bloqueio: {bloqueio_pct:.1f}%")
    st.write(f"- Disponível: {100 - bloqueio_pct - taxa_liquidacao:.1f}%")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
    📊 Dashboard Sistematização de Emendas Parlamentares - DF<br>
    Dados: Ciclo 2024-2025 | Atualizado: """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """<br>
    Licença: CC0 - Domínio Público
    </div>
    """,
    unsafe_allow_html=True
)
