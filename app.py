import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection
import os

# Configuração de Layout
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
# CONEXÃO COM GOOGLE SHEETS E PERSISTÊNCIA EM NUVEM
# ------------------------------------------------------------------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

def carregar_dados(aba_nome):
    if conn:
        try:
            return conn.read(worksheet=aba_nome, ttl=0)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def salvar_dados(df, aba_nome):
    if conn:
        try:
            conn.update(worksheet=aba_nome, data=df)
            return True
        except Exception:
            return False
    return False

# ------------------------------------------------------------------------------
# INICIALIZAÇÃO DAS BASES DE DADOS NA SESSÃO
# ------------------------------------------------------------------------------

# Equipe de Funcionários / Responsáveis
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

# Lista de Órgãos
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

# Base de Clientes
if "clientes" not in st.session_state:
    st.session_state.clientes = [
        {
            "id": 1,
            "tipo_pessoa": "Pessoa Jurídica",
            "nome_razao": "CALADO EVENTOS E ADMINISTRAÇÃO LTDA",
            "cpf_cnpj": "12.345.678/0001-90",
            "representante_legal": "Carlos Calado",
            "endereco_cliente": "Av. das Américas, 3500 - Barra da Tijuca, Rio de Janeiro - RJ",
            "enderecos_empreendimentos": [
                "Unidade Barra: Av. das Américas, 3500 - Bloco 2",
                "Unidade Recreio: Rua Projetada B, Lote 14"
            ],
            "numero_proposta": "PROP-2026/012",
            "numero_contrato": "CTR-2026/005",
            "data_inicio": date(2026, 1, 15)
        }
    ]

# Base de Processos Principais (SMDU / LICIN / Prefeitura)
if "processos_principais" not in st.session_state:
    st.session_state.processos_principais = [
        {
            "id": 1,
            "cliente_id": 1,
            "cliente_nome": "CALADO EVENTOS E ADMINISTRAÇÃO LTDA",
            "numero_processo_principal": "04/001.555/2026 (SMDU/LICIN)",
            "endereco_empreendimento": "Unidade Barra: Av. das Américas, 3500 - Bloco 2",
            "servico_contratado": "Licença de Obra e Modificação com Acréscimo",
            "responsavel_principal": "Anna",
            "status": "4. Em Exigência / Aguardando Documentos",
            "data_inicio": date(2026, 2, 1),
            "prazo_limite": date(2026, 12, 15),
            "despachos": [
                {"data": "2026-03-10", "texto": "Publicado despacho de exigências no SEI.RIO exigindo parecer do CBMERJ e GEO-RIO."}
            ]
        }
    ]

# Base de Subprocessos
if "subprocessos" not in st.session_state:
    st.session_state.subprocessos = [
        {
            "id": 101,
            "processo_principal_id": 1,
            "cliente_id": 1,
            "orgao_subprocesso": "Corpo de Bombeiros (CBMERJ)",
            "numero_subprocesso": "CBMERJ-2026/99812",
            "descricao_exigencia": "Laudo de Exigências e Certificado de Aprovação do Sistema Contra Incêndio",
            "informacao_relevante": "Atentar para a necessidade de reserva técnica de incêndio no castelo d'água superior.",
            "responsavel_sub": "Bruno",
            "status": "Em Tramitação",
            "data_inicio": date(2026, 3, 15),
            "prazo_fim": date(2026, 11, 30),
            "notas_internas": [
                {"data": "2026-03-16", "autor": "Bruno", "texto": "Reunião com o major do DGST marcada para quinta-feira."}
            ],
            "despachos": [
                {"data": "2026-03-20", "texto": "Protocolado projeto de segurança contra incêndio no DGST."}
            ],
            "documentos": [
                {"id": 1, "nome": "Protocolo_CBMERJ.pdf", "data": "2026-03-20"}
            ]
        }
    ]

# Base Financeira
if "financeiro" not in st.session_state:
    st.session_state.financeiro = [
        {
            "id": 1,
            "processo_principal_id": 1,
            "subprocesso_id": 101,
            "cliente_id": 1,
            "tipo_documento": "DARM / Taxa CBMERJ",
            "numero_documento": "DARM nº 99283-1",
            "descricao": "Taxa de Análise de Projeto CBMERJ",
            "valor": 480.00,
            "vencimento": date(2026, 11, 10),
            "pagador": "B2x (A Reembolsar)",
            "status_pagamento": "Pendente",
            "nota_fiscal_emitida": "Não",
            "comprovante_anexado": None
        }
    ]

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
        "Entrada Processo Principal (LICIN/SMDU)",
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

st.title("B2x Arquitetura | Sistema de Gestão Processual Sincronizado")

# ------------------------------------------------------------------------------
# 1. DASHBOARD EXECUTIVO
# ------------------------------------------------------------------------------
if menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento (Sincronizado na Nuvem)")
    
    df_p = pd.DataFrame(st.session_state.processos_principais)
    df_sub = pd.DataFrame(st.session_state.subprocessos)
    df_fin = pd.DataFrame(st.session_state.financeiro)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(st.session_state.clientes))
    c2.metric("Processos Principais (SMDU/LICIN)", len(df_p))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    
    total_pendente_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente_fin:,.2f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos Principais por Status")
        if not df_p.empty:
            status_counts = df_p["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty:
            sub_counts = df_sub["orgao_subprocesso"].value_counts().reset_index()
            sub_counts.columns = ["Órgão", "Quantidade"]
            st.bar_chart(sub_counts.set_index("Órgão"))

# ------------------------------------------------------------------------------
# 2. ENTRADA PROCESSO PRINCIPAL (LICIN / SMDU / PREFEITURA)
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro de Processo Principal (SMDU / LICIN / SEI.RIO)")
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else []
    lista_equipe_nomes = list(st.session_state.equipe.keys())
    
    if lista_clientes_nomes:
        with st.form("form_processo_principal"):
            st.markdown("##### 1. Identificação do Cliente e Empreendimento")
            c_pm1, c_pm2 = st.columns(2)
            
            with c_pm1:
                cliente_sel_nome = st.selectbox("Cliente Cadastrado *", lista_clientes_nomes)
