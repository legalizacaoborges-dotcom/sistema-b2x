import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import json
import os

# Configuração da página
st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual & Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada
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

# ------------------------------------------------------------------------------
# BANCO DE DADOS SQLITE PERSISTENTE
# ------------------------------------------------------------------------------
DB_FILE = "b2x_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_pessoa TEXT,
            nome_razao TEXT,
            cpf_cnpj TEXT,
            representante_legal TEXT,
            endereco_cliente TEXT,
            enderecos_empreendimentos TEXT,
            numero_proposta TEXT,
            numero_contrato TEXT,
            data_inicio TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS processos_principais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            numero_processo_principal TEXT,
            endereco_empreendimento TEXT,
            servico_contratado TEXT,
            responsavel_principal TEXT,
            status TEXT,
            data_inicio TEXT,
            prazo_limite TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS subprocessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processo_principal_id INTEGER,
            orgao_subprocesso TEXT,
            numero_subprocesso TEXT,
            descricao_exigencia TEXT,
            informacao_relevante TEXT,
            responsavel_sub TEXT,
            status TEXT,
            data_inicio TEXT,
            prazo_fim TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cargo TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS orgaos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processo_principal_id INTEGER,
            cliente_id INTEGER,
            tipo_documento TEXT,
            numero_documento TEXT,
            descricao TEXT,
            valor REAL,
            vencimento TEXT,
            pagador TEXT,
            status_pagamento TEXT,
            nota_fiscal_emitida TEXT
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM clientes")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO clientes (id, tipo_pessoa, nome_razao, cpf_cnpj, representante_legal, endereco_cliente, enderecos_empreendimentos, numero_proposta, numero_contrato, data_inicio)
            VALUES (1, 'Pessoa Jurídica', 'CALADO EVENTOS E ADMINISTRAÇÃO LTDA', '12.345.678/0001-90', 'Carlos Calado', 'Av. das Américas, 3500 - Barra da Tijuca, Rio de Janeiro - RJ', '["Unidade Barra: Av. das Américas, 3500 - Bloco 2", "Unidade Recreio: Rua Projetada B, Lote 14"]', 'PROP-2026/012', 'CTR-2026/005', '2026-01-15')
        """)
        
    c.execute("SELECT COUNT(*) FROM equipe")
    if c.fetchone()[0] == 0:
        equipe_padrao = [
            ("Gabriela", "Captação / Negociação / Entrada"),
            ("Mariana", "Financeiro / Propostas / Pagamentos"),
            ("Anna", "Processos / Exigências / RRT / Relatórios"),
            ("Bruno", "Processos / RGI / Diligências Externas"),
            ("Camila", "Atendimento / Obra / Mídias"),
            ("Alessandra", "Projetos / Prefeitura"),
            ("Lilian", "Projetos / Prefeitura / RRT")
        ]
        c.executemany("INSERT INTO equipe (nome, cargo) VALUES (?, ?)", equipe_padrao)
        
    c.execute("SELECT COUNT(*) FROM orgaos")
    if c.fetchone()[0] == 0:
        orgaos_padrao = [
            ("Prefeitura (SMDU / LICIN / SEI.RIO)",),
            ("Cartório de RGI (Averbação/Registro)",),
            ("Licenciamento Ambiental (SMAC / INEA)",),
            ("Saneamento e Drenagem (RioÁguas)",),
            ("Geotecnia e Encostas (GEO-RIO)",),
            ("Corpo de Bombeiros (CBMERJ)",),
            ("Secretaria de Fazenda (ISS / ITBI)",),
            ("Patrimônio Cultural (IRPH / IPHAN)",)
        ]
        c.executemany("INSERT INTO orgaos (nome) VALUES (?)", orgaos_padrao)
        
    conn.commit()
    conn.close()

init_db()

# ------------------------------------------------------------------------------
# FUNÇÕES DE LEITURA E ESCRITA
# ------------------------------------------------------------------------------
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
            except:
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
    df = run_df("SELECT * FROM orgaos")
    return df["nome"].tolist()

def get_financeiro():
    return run_df("SELECT * FROM financeiro").to_dict(orient="records")

STATUS_OPCOES = [
    "1. Captação / Proposta Comercial",
    "2. Análise Inicial / Elaboração Projeto",
    "3. Em Tramitação no Órgão",
    "4. Em Exigência / Aguardando Documentos",
    "5. Aguardando Pagamento de Taxa/RRT",
    "6. Concluído / Licenciado / Averbado"
]

modulos_alfabetico = [
    "Busca Integrada (Lupa 360°)",
    "Cadastro de Clientes",
    "Dashboard Executivo",
    "Entrada Processo Principal (LICIN/SMDU)",
    "Fila Individual",
    "Gestão da Equipe",
    "Gestão de Órgãos",
    "Gestão de Subprocessos",
    "Módulo Financeiro (Mariana)",
    "Painel Geral de Processos",
    "Relatórios"
]

if os.path.exists("LOGO.png"):
    st.sidebar.image("LOGO.png", use_container_width=True)
else:
    st.sidebar.markdown("### B2x Arquitetura")

st.sidebar.markdown("---")
menu = st.sidebar.radio("Módulos do Sistema", modulos_alfabetico)

st.title("B2x Arquitetura | Sistema de Gestão Processual Sincronizado")

# ------------------------------------------------------------------------------
# 1. BUSCA INTEGRADA
# ------------------------------------------------------------------------------
if menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente")
    clientes = get_clientes()
    nombres_clientes = {c["id"]: c["nome_razao"] for c in clientes} if clientes else {}
    cliente_sel_id = st.selectbox("Selecione ou Pesquise o Nome do Cliente:", [""] + list(nombres_clientes.keys()), format_func=lambda x: nombres_clientes.get(x, "Selecione..."))
    
    if cliente_sel_id != "":
        cliente_obj = get_cliente_por_id(cliente_sel_id)
        if cliente_obj:
            st.markdown(f"### Ficha 360°: {cliente_obj['nome_razao']}")
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.write(f"**Tipo:** {cliente_obj.get('tipo_pessoa', 'N/A')}")
                st.write(f"**CPF/CNPJ:** {cliente_obj.get('cpf_cnpj', 'N/A')}")
                st.write(f"**Representante:** {cliente_obj.get('representante_legal') or 'N/A'}")
            with c_info2:
                st.write(f"**Proposta:** {cliente_obj.get('numero_proposta') or 'N/A'}")
                st.write(f"**Contrato:** {cliente_obj.get('numero_contrato') or 'N/A'}")
            with c_info3:
                st.write(f"**Endereço Comercial:** {cliente_obj.get('endereco_cliente') or 'N/A'}")
                st.write("**Empreendimentos / Endereços de Obra:**")
                ends = cliente_obj.get("enderecos_empreendimentos", [])
                if isinstance(ends, list):
                    for end in ends:
                        st.write(f"• {end}")
                else:
                    st.write(f"• {ends}")

            st.divider()
            procs = [p for p in get_processos_principais() if p.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais e Subprocessos ({len(procs)})")
            
            if procs:
                subs_todos = get_subprocessos()
                for pmc in procs:
                    st.info(f"**Endereço:** {pmc.get('endereco_empreendimento', 'N/A')}\n\n**Processo Principal:** {pmc.get('numero_processo_principal', 'N/A')} | **Status:** `{pmc.get('status', 'N/A')}`")
                    subs_cli = [s for s in subs_todos if s.get("processo_principal_id") == pmc["id"]]
                    for sc in subs_cli:
                        st.write(f" └─ **Subprocesso ({sc.get('orgao_subprocesso', 'Órgão')}):** {sc.get('numero_subprocesso', 'N/A')} — Status: `{sc.get('status', 'N/A')}`")
            else:
                st.info("Nenhum processo cadastrado para este cliente.")

            st.divider()
            fin = [f for f in get_financeiro() if f.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 💰 Histórico Financeiro ({len(fin)})")
            if fin:
                st.dataframe(pd.DataFrame(fin)[["tipo_documento", "numero_documento", "descricao", "valor", "vencimento", "pagador", "status_pagamento"]], use_container_width=True)
            else:
                st.info("Nenhum lançamento financeiro para este cliente.")

# ------------------------------------------------------------------------------
# 2. CADASTRO DE CLIENTES
# ------------------------------------------------------------------------------
elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes e Múltiplos Endereços")
    tab_cli1, tab_cli2, tab_cli3 = st.tabs(["➕ Cadastrar Novo Cliente", "✏️ Editar Cadastro & Adicionar Endereços", "🗑️ Excluir Cliente"])
    
    with tab_cli1:
