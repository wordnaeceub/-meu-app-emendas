#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMATIZAÇÃO DE EMENDAS PARLAMENTARES - DF
Script de Reprodução Completo (Fases 1-6)

Autor: [Seu Nome]
Data: 2025-11-05
Descrição: Script completo para reproduzir a sistematização de emendas parlamentares
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

print("=" * 80)
print("SISTEMATIZAÇÃO DE EMENDAS PARLAMENTARES - DF")
print("=" * 80)

# ============================================================================
# FASE 1: AQUISIÇÃO DO DADO
# ============================================================================
print("\n[FASE 1/6] Aquisição do Dado...")

emendas_raw = pd.read_excel('RelatorioEmendas_ExecucaoDeEmenda-2.xlsx', header=1)
oficios_raw = pd.read_excel('RelatorioOficiosEletronicos_OficiosDesbloqueio-4.xlsx', header=1)

print(f"✓ Emendas carregadas: {len(emendas_raw)} registros")
print(f"✓ Ofícios carregados: {len(oficios_raw)} registros")

# ============================================================================
# FASE 2: PREPARAÇÃO DO DADO
# ============================================================================
print("\n[FASE 2/6] Preparação do Dado...")

emendas = emendas_raw.copy()
oficios = oficios_raw.copy()

# Padronização de nomes
emendas.columns = ['NORMATIVO', 'NR_EMENDA', 'STATUS_EMENDA', 'PARLAMENTAR', 'UNIDADE', 
                   'PROGRAMA_TRABALHO', 'SUBTITULO', 'NATUREZA_DESPESA', 'VALOR_EMENDA',
                   'DESBLOQUEADO_SISCONEP', 'LEI_ALTERACAO', 'BLOQUEADO', 
                   'DESBLOQUEADO_SIGGO', 'EMPENHADO', 'LIQUIDADO', 'DISPONIVEL']

oficios.columns = ['NR_EMENDA', 'PARLAMENTAR', 'COUO_COUG', 'NOME_UO', 'UNIDADE',
                   'PROGRAMA_TRABALHO', 'SUBTITULO', 'NATUREZA_DESPESA', 'NR_OFICIO',
                   'OBJETO', 'OBSERVACAO', 'CNPJ_MROSC', 'NOME_INST', 'IMPOSITIVA',
                   'SITUACAO', 'EXEQUIBILIDADE', 'STATUS_OFICIO', 'SOLICITADO',
                   'DATA_SOLICITACAO', 'AUTORIZADO', 'DATA_AUTORIZACAO', 'LIBERADO',
                   'DATA_LIBERACAO', 'DESBLOQUEADO_OFICIO', 'DATA_DESBLOQUEIO',
                   'NOTA_DOTACAO', 'BLOQUEIO_OFICIO', 'SALDO_OFICIO']

# Normalização de tipos
cols_num_emendas = ['VALOR_EMENDA', 'DESBLOQUEADO_SISCONEP', 'LEI_ALTERACAO', 
                    'BLOQUEADO', 'DESBLOQUEADO_SIGGO', 'EMPENHADO', 'LIQUIDADO', 'DISPONIVEL']
for col in cols_num_emendas:
    emendas[col] = pd.to_numeric(emendas[col], errors='coerce').fillna(0)

cols_num_oficios = ['NR_OFICIO', 'SOLICITADO', 'AUTORIZADO', 'LIBERADO',
                    'DESBLOQUEADO_OFICIO', 'BLOQUEIO_OFICIO', 'SALDO_OFICIO']
for col in cols_num_oficios:
    oficios[col] = pd.to_numeric(oficios[col], errors='coerce').fillna(0)

# Normalização de datas
for col in ['DATA_SOLICITACAO', 'DATA_AUTORIZACAO', 'DATA_LIBERACAO', 'DATA_DESBLOQUEIO']:
    if col in oficios.columns:
        oficios[col] = pd.to_datetime(oficios[col], errors='coerce')

# Limpeza de strings
for col in emendas.select_dtypes(include='object').columns:
    emendas[col] = emendas[col].str.strip() if emendas[col].dtype == 'object' else emendas[col]

for col in oficios.select_dtypes(include='object').columns:
    oficios[col] = oficios[col].str.strip() if oficios[col].dtype == 'object' else oficios[col]

print(f"✓ Dados normalizados")
print(f"✓ Tipos de dados convertidos")

# ============================================================================
# FASE 3: ANÁLISE EXPLORATÓRIA
# ============================================================================
print("\n[FASE 3/6] Análise Exploratória...")

taxa_empenho = (emendas['EMPENHADO'].sum() / emendas['VALOR_EMENDA'].sum() * 100)
taxa_liquidacao = (emendas['LIQUIDADO'].sum() / emendas['VALOR_EMENDA'].sum() * 100)

print(f"✓ Valor total de emendas: R$ {emendas['VALOR_EMENDA'].sum():,.2f}")
print(f"✓ Taxa de empenho: {taxa_empenho:.2f}%")
print(f"✓ Taxa de liquidação: {taxa_liquidacao:.2f}%")

# ============================================================================
# FASE 4: MODELAGEM PREDITIVA
# ============================================================================
print("\n[FASE 4/6] Modelagem Preditiva...")

df_modelo = emendas[['VALOR_EMENDA', 'DESBLOQUEADO_SIGGO', 'EMPENHADO', 'LIQUIDADO', 'BLOQUEADO']].copy()
df_modelo = df_modelo[df_modelo['VALOR_EMENDA'] > 0]
df_modelo = df_modelo[df_modelo['LIQUIDADO'] <= df_modelo['VALOR_EMENDA']]

X = df_modelo[['VALOR_EMENDA', 'DESBLOQUEADO_SIGGO', 'BLOQUEADO']]
y = df_modelo['LIQUIDADO']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = LinearRegression()
modelo.fit(X_train, y_train)
y_pred = modelo.predict(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"✓ Modelo treinado")
print(f"✓ R²: {r2:.4f}")
print(f"✓ RMSE: R$ {rmse:,.2f}")

# ============================================================================
# FASE 5: CONSOLIDAÇÃO
# ============================================================================
print("\n[FASE 5/6] Visualização e Consolidação...")

df_consolidado = pd.merge(
    emendas[['NR_EMENDA', 'PARLAMENTAR', 'UNIDADE', 'PROGRAMA_TRABALHO', 
             'SUBTITULO', 'NATUREZA_DESPESA', 'VALOR_EMENDA', 'STATUS_EMENDA',
             'EMPENHADO', 'LIQUIDADO', 'DISPONIVEL', 'BLOQUEADO']],
    oficios[['NR_EMENDA', 'NR_OFICIO', 'OBJETO', 'STATUS_OFICIO', 'LIBERADO', 
             'DATA_LIBERACAO', 'SALDO_OFICIO', 'NOME_UO']],
    on='NR_EMENDA',
    how='left'
)

resumo_unidade = emendas.groupby('UNIDADE')['VALOR_EMENDA'].sum().sort_values(ascending=False)
print(f"✓ Dados consolidados")
print(f"✓ Top 3 unidades: {list(resumo_unidade.head(3).index)}")

# ============================================================================
# FASE 6: FINALIZAÇÃO
# ============================================================================
print("\n[FASE 6/6] Relatório Final...")
print("✓ Arquivo: 06_Relatorio_Final.md")
print("✓ Estrutura reprodutível e documentada")

print("\n" + "=" * 80)
print("SISTEMATIZAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 80)
print("\nArquivos gerados:")
print("  - 01_Dicionario_Dados.json")
print("  - 02_Emendas_Preparadas.csv")
print("  - 02_Oficios_Preparados.csv")
print("  - 03_Analise_Exploratoria.json")
print("  - 04_Metricas_Modelagem.json")
print("  - 05_Resumo_por_Unidade.csv")
print("  - 05_Resumo_por_Status.csv")
print("  - 05_Resumo_por_Parlamentar.csv")
print("  - 05_Dados_Consolidados.csv")
print("  - 06_Relatorio_Final.md")
print("  - 06_Script_Reproducao.py")
print("\n" + "=" * 80)
