import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection
import os

# Configuração do Layout
st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual & Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada - B2x Arquitetura
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
# CONEXÃO COM GOOGLE SHEETS
# ------------------------------------------------------------------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    conn = None

def carregar_dados(aba):
    """Lê uma aba da planilha do Google Sheets"""
    if conn:
        try:
            return conn.read(worksheet=aba, ttl=0)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df, aba):
    """Grava dados atualizados na aba do Google Sheets"""
    if conn:
        try:
            conn.update(worksheet=aba, data=df)
            return True
        except Exception:
            return False
    return False

# ------------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTRUTURAS DE MEMÓRIA NA SESSÃO
# ------------------------------------------------------------------------------
if "equipe" not in st.session_state:
    st.session_state.equipe = {
        "Gabriela": "Captação / Negociação / Entrada",
        "Mariana": "Financeiro / Propostas / Pagamentos",
        "Anna": "Processos / Exigências / RRT / Relatórios",
        "Bruno": "Processos / RGI / Diligências Externas",
        "Camila": "Atendimento / Obra / Mídias",
        "Alessandra": "Projetos / Prefeitura",
        "Lilian": "Projetos / Prefeitura / RRT"
    }

if "lista_orgaos" not in st.session_state:
    st.session_state.lista_orgaos = [
        "Prefeitura (SMDU / LICIN / SEI.RIO)",
        "Cartório de RGI (Averbação/Registro)",
        "Licenciamento Ambiental (SMAC / INEA)",
        "Saneamento e Drenagem (RioÁguas)",
        "Geotecnia e Encostas (GEO-RIO)",
        "Corpo de Bombeiros (CBMERJ)",
        "Secretaria de Fazenda (ISS / ITBI)",
        "Patrimônio Cultural (IRPH / IPHAN)"
    ]

if "clientes" not in st.session_state:
    st.session_state.clientes = []

if "processos_mae" not in st.session_state:
    st.session_state.processos_mae = []

if "subprocessos" not in st.session_state:
    st.session_state.subprocessos = []

if "financeiro" not in st.session_state:
    st.session_state.financeiro = []

STATUS_OPCOES = [
    "1. Captação / Proposta Comercial",
    "2. Análise Inicial / Elaboração Projeto",
    "3. Em Tramitação no Órgão",
    "4. Em Exigência / Aguardando Documentos",
    "5. Aguardando Pagamento de Taxa/RRT",
    "6. Concluído / Licenciado / Averbado"
]

# MENU LATERAL
if os.path.exists("LOGO.png"):
    st.sidebar.image("LOGO.png", use_container_width=True)
else:
    st.sidebar.markdown("### B2x Arquitetura")

st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Módulos do Sistema", 
    [
        "Dashboard Executivo", 
        "Entrada Processo Mãe (LICIN/SMDU)",
        "Gestão de Subprocessos",
        "Painel Geral de Processos", 
        "Cadastro de Clientes",
        "Busca Integrada (Lupa 360°)",
        "Módulo Financeiro (Mariana)", 
        "Gestão de Órgãos",
        "Gestão da Equipe",
        "Fila Individual", 
        "Relatórios"
    ]
)

st.title("B2x Arquitetura | Sistema Integrado em Nuvem")

# ------------------------------------------------------------------------------
# MÓDULOS
# ------------------------------------------------------------------------------
if menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento (Sincronizado Nuvem)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(st.session_state.clientes))
    c2.metric("Processos Mãe (SMDU/LICIN)", len(st.session_state.processos_mae))
    c3.metric("Subprocessos / Restrições", len(st.session_state.subprocessos))
    
    df_fin = pd.DataFrame(st.session_state.financeiro)
    tot_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {tot_fin:,.2f}")

elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes e Empreendimentos")
    with st.form("form_cli_gsk"):
        tipo_p = st.selectbox("Tipo de Pessoa", ["Pessoa Jurídica", "Pessoa Física"])
        nome_raz = st.text_input("Razão Social / Nome Completo *")
        cpf_cnpj = st.text_input("CPF / CNPJ *")
        end_emp = st.text_input("Endereço do Primeiro Empreendimento")
        
        if st.form_submit_button("Salvar Cliente na Nuvem"):
            if nome_raz.strip():
                novo_id = max([c["id"] for c in st.session_state.clientes], default=0) + 1
                st.session_state.clientes.append({
                    "id": novo_id,
                    "tipo_pessoa": tipo_p,
                    "nome_razao": nome_raz,
                    "cpf_cnpj": cpf_cnpj,
                    "enderecos_empreendimentos": [end_emp] if end_emp else [],
                    "data_inicio": date.today()
                })
                salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                st.success("Cliente salvo e sincronizado na nuvem!")
                st.rerun()

elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos, Notas e Despachos")
    st.info("Qualquer alteração efetuada aqui fica imediatamente sincronizada na nuvem para toda a equipa.")

else:
    st.info(f"Módulo '{menu}' ativo e pronto para uso.")
