import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import json
import os

st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual & Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #F4F6F8; }
    section[data-testid="stSidebar"] { background-color: #022B3A !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3 { color: #022B3A; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 500; }
    .stMetric { background-color: #FFFFFF; padding: 18px; border-radius: 4px; border-top: 4px solid #E1C3A1; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    div.stButton > button { background-color: #022B3A !important; color: #E1C3A1 !important; border: 1px solid #E1C3A1 !important; border-radius: 4px !important; font-weight: 500 !important; }
    div.stButton > button:hover { background-color: #E1C3A1 !important; color: #022B3A !important; }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "b2x_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, tipo_pessoa TEXT, nome_razao TEXT, cpf_cnpj TEXT,
        representante_legal TEXT, endereco_cliente TEXT, enderecos_empreendimentos TEXT,
        numero_proposta TEXT, numero_contrato TEXT, data_inicio TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS processos_principais (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cliente_id INTEGER, numero_processo_principal TEXT,
        endereco_empreendimento TEXT, servico_contratado TEXT, responsavel_principal TEXT,
        status TEXT, data_inicio TEXT, prazo_limite TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS subprocessos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, processo_principal_id INTEGER, orgao_subprocesso TEXT,
        numero_subprocesso TEXT, descricao_exigencia TEXT, informacao_relevante TEXT,
        responsavel_sub TEXT, status TEXT, data_inicio TEXT, prazo_fim TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS equipe (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cargo TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orgaos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT, processo_principal_id INTEGER, cliente_id INTEGER,
        tipo_documento TEXT, numero_documento TEXT, descricao TEXT, valor REAL,
        vencimento TEXT, pagador TEXT, status_pagamento TEXT, nota_fiscal_emitida TEXT
    )""")
    c.execute("SELECT COUNT(*) FROM clientes")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO clientes (id, tipo_pessoa, nome_razao, cpf_cnpj, representante_legal, endereco_cliente, enderecos_empreendimentos, numero_proposta, numero_contrato, data_inicio)
        VALUES (1, 'Pessoa Jurídica', 'CALADO EVENTOS E ADMINISTRAÇÃO LTDA', '12.345.678/0001-90', 'Carlos Calado', 'Av. das Américas, 3500 - Barra da Tijuca, Rio de Janeiro - RJ', '["Unidade Barra: Av. das Américas, 3500 - Bloco 2"]', 'PROP-2026/012', 'CTR-2026/005', '2026-01-15')""")
    c.execute("SELECT COUNT(*) FROM equipe")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO equipe (nome, cargo) VALUES (?, ?)", [
            ("Gabriela", "Captação / Negociação"), ("Mariana", "Financeiro"), ("Anna", "Processos / Exigências"),
            ("Bruno", "Diligências Externas"), ("Camila", "Atendimento / Obra"), ("Alessandra", "Projetos"), ("Lilian", "Projetos / RRT")
        ])
    c.execute("SELECT COUNT(*) FROM orgaos")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO orgaos (nome) VALUES (?)", [
            ("Prefeitura (SMDU / LICIN / SEI.RIO)",), ("Cartório de RGI",), ("Licenciamento Ambiental (SMAC)",),
            ("Saneamento e Drenagem (RioÁguas)",), ("Geotecnia e Encostas (GEO-RIO)",), ("Corpo de Bombeiros (CBMERJ)",),
            ("Secretaria de Fazenda",), ("Patrimônio Cultural (IRPH)",)
        ])
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetchall=True):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    data = c.fetchall() if fetchall else None
    conn.commit()
    conn.close()
    return data

def run_df(query, params=()):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_clientes():
    df = run_df("SELECT * FROM clientes")
    records = df.to_dict(orient="records")
    for r in records:
        if isinstance(r.get("enderecos_empreendimentos"), str):
            try:
                r["enderecos_empreendimentos"] = json.loads(r["enderecos_empreendimentos"])
            except Exception:
                r["enderecos_empreendimentos"] = [r["enderecos_empreendimentos"]]
    return records

def get_cliente_por_id(cid):
    clis = get_clientes()
    return next((c for c in clis if c["id"] == cid), None)

def get_processos_principais():
    return run_df("SELECT * FROM processos_principais").to_dict(orient="records")

def get_processo_por_id(pid):
    procs = get_processos_principais()
    return next((p for p in procs if p["id"] == pid), None)

def get_subprocessos():
    return run_df("SELECT * FROM subprocessos").to_dict(orient="records")

def get_equipe():
    df = run_df("SELECT * FROM equipe")
    return {r["nome"]: r["cargo"] for _, r in df.iterrows()}

def get_orgaos():
    return run_df("SELECT * FROM orgaos")["nome"].tolist()

def get_financeiro():
    return run_df("SELECT * FROM financeiro").to_dict(orient="records")

STATUS_OPCOES = [
    "1. Captação / Proposta Comercial", "2. Análise Inicial / Elaboração Projeto",
    "3. Em Tramitação no Órgão", "4. Em Exigência / Aguardando Documentos",
    "5. Aguardando Pagamento de Taxa/RRT", "6. Concluído / Licenciado / Averbado"
]

modulos_alfabetico = [
    "Busca Integrada (Lupa 360°)", "Cadastro de Clientes", "Dashboard Executivo",
    "Entrada Processo Principal (LICIN/SMDU)", "Fila Individual", "Gestão da Equipe",
    "Gestão de Órgãos", "Gestão de Subprocessos", "Módulo Financeiro (Mariana)",
    "Painel Geral de Processos", "Relatórios"
]

if os.path.exists("LOGO.png"):
    st.sidebar.image("LOGO.png", use_container_width=True)
else:
    st.sidebar.markdown("### B2x Arquitetura")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos do Sistema", modulos_alfabetico)
st.title("B2x Arquitetura | Sistema de Gestão Processual Sincronizado")

if menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente")
    clientes = get_clientes()
    nombres_clientes = {c["id"]: c
