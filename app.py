import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection
import os
import json

# Configuração de Layout
st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual & Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada - Identidade Visual B2x Arquitetura
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
# CONEXÃO E PERSISTÊNCIA REAL COM GOOGLE SHEETS
# ------------------------------------------------------------------------------
@st.cache_resource
def get_connection():
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        return None

conn = get_connection()

def carregar_aba(aba_nome):
    if conn:
        try:
            df = conn.read(worksheet=aba_nome, ttl=0)
            if df is not None and not df.empty:
                records = df.to_dict(orient="records")
                # Tratar conversão de colunas JSON/listas
                for r in records:
                    for k, v in r.items():
                        if isinstance(v, str) and (v.startswith("[") or v.startswith("{")):
                            try:
                                r[k] = json.loads(v)
                            except:
                                pass
                return records
        except Exception:
            pass
    return None

def salvar_aba(lista_dados, aba_nome):
    if conn and isinstance(lista_dados, list):
        try:
            df = pd.DataFrame(lista_dados)
            if not df.empty:
                # Converter colunas com objetos/listas/datas em formato serializável
                for col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) 
                        else str(x) if isinstance(x, (date, datetime)) 
                        else "" if pd.isna(x) else x
                    )
                conn.update(worksheet=aba_nome, data=df)
                return True
        except Exception as e:
            st.error(f"Erro ao salvar na nuvem ({aba_nome}): {e}")
            return False
    return False

# ------------------------------------------------------------------------------
# CARREGAMENTO INICIAL DOS DADOS DA NUVEM / FALLBACK SE VAZIO
# ------------------------------------------------------------------------------

# 1. Clientes
if "clientes" not in st.session_state:
    dados = carregar_aba("Clientes")
    if dados:
        st.session_state.clientes = dados
    else:
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
                "data_inicio": "2026-01-15"
            }
        ]

# 2. Processos Principais
if "processos_principais" not in st.session_state:
    dados = carregar_aba("Processos_Principais")
    if dados:
        st.session_state.processos_principais = dados
    else:
        st.session_state.processos_principais = [
            {
                "id": 1,
                "cliente_id": 1,
                "numero_processo_principal": "04/001.555/2026 (SMDU/LICIN)",
                "endereco_empreendimento": "Unidade Barra: Av. das Américas, 3500 - Bloco 2",
                "servico_contratado": "Licença de Obra e Modificação com Acréscimo",
                "responsavel_principal": "Anna",
                "status": "4. Em Exigência / Aguardando Documentos",
                "data_inicio": "2026-02-01",
                "prazo_limite": "2026-12-15"
            }
        ]

# 3. Subprocessos
if "subprocessos" not in st.session_state:
    dados = carregar_aba("Subprocessos")
    if dados:
        st.session_state.subprocessos = dados
    else:
        st.session_state.subprocessos = [
            {
                "id": 101,
                "processo_principal_id": 1,
                "orgao_subprocesso": "Corpo de Bombeiros (CBMERJ)",
                "numero_subprocesso": "CBMERJ-2026/99812",
                "descricao_exigencia": "Laudo de Exigências e Certificado de Aprovação",
                "informacao_relevante": "Reserva técnica de incêndio necessária no castelo d'água.",
                "responsavel_sub": "Bruno",
                "status": "Em Tramitação",
                "data_inicio": "2026-03-15",
                "prazo_fim": "2026-11-30"
            }
        ]

# 4. Equipe
if "equipe" not in st.session_state:
    dados = carregar_aba("Equipe")
    if dados:
        st.session_state.equipe = {item["nome"]: item["cargo"] for item in dados}
    else:
        st.session_state.equipe = {
            "Gabriela": "Captação / Negociação / Entrada",
            "Mariana": "Financeiro / Propostas / Pagamentos",
            "Anna": "Processos / Exigências / RRT / Relatórios",
            "Bruno": "Processos / RGI / Diligências Externas",
            "Camila": "Atendimento / Obra / Mídias",
            "Alessandra": "Projetos / Prefeitura",
            "Lilian": "Projetos / Prefeitura / RRT"
        }

# 5. Órgãos
if "lista_orgaos" not in st.session_state:
    dados = carregar_aba("Orgaos")
    if dados:
        st.session_state.lista_orgaos = [item["nome"] for item in dados]
    else:
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

# 6. Financeiro
if "financeiro" not in st.session_state:
    dados = carregar_aba("Financeiro")
    if dados:
        st.session_state.financeiro = dados
    else:
        st.session_state.financeiro = [
            {
                "id": 1,
                "processo_principal_id": 1,
                "cliente_id": 1,
                "tipo_documento": "DARM / Taxa CBMERJ",
                "numero_documento": "DARM nº 99283-1",
                "descricao": "Taxa de Análise de Projeto CBMERJ",
                "valor": 480.00,
                "vencimento": "2026-11-10",
                "pagador": "B2x (A Reembolsar)",
                "status_pagamento": "Pendente",
                "nota_fiscal_emitida": "Não"
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
# FUNÇÕES DE BUSCA DINÂMICA
# ------------------------------------------------------------------------------
def get_cliente_por_id(cid):
    return next((c for c in st.session_state.clientes if c["id"] == cid), None)

def get_processo_por_id(pid):
    return next((p for p in st.session_state.processos_principais if p["id"] == pid), None)

# ------------------------------------------------------------------------------
# 1. BUSCA INTEGRADA (LUPA 360°)
# ------------------------------------------------------------------------------
if menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente")
    
    nombres_clientes = {c["id"]: c["nome_razao"] for c in st.session_state.clientes} if st.session_state.clientes else {}
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
            
            procs_p_cli = [p for p in st.session_state.processos_principais if p.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais e Subprocessos ({len(procs_p_cli)})")
            
            if procs_p_cli:
                for pmc in procs_p_cli:
                    st.info(f"**Endereço:** {pmc.get('endereco_empreendimento', 'N/A')}\n\n**Processo Principal:** {pmc.get('numero_processo_principal', 'N/A')} | **Status:** `{pmc.get('status', 'N/A')}`")
                    subs_cli = [s for s in st.session_state.subprocessos if s.get("processo_principal_id") == pmc["id"]]
                    for sc in subs_cli:
                        st.write(f" └─ **Subprocesso ({sc.get('orgao_subprocesso', 'Órgão')}):** {sc.get('numero_subprocesso', 'N/A')} — Status: `{sc.get('status', 'N/A')}`")
            else:
                st.info("Nenhum processo cadastrado para este cliente.")

            st.divider()

            financeiro_cliente = [f for f in st.session_state.financeiro if f.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 💰 Histórico Financeiro ({len(financeiro_cliente)})")
            
            if financeiro_cliente:
                df_fin_cli = pd.DataFrame(financeiro_cliente)
                st.dataframe(
                    df_fin_cli[["tipo_documento", "numero_documento", "descricao", "valor", "vencimento", "pagador", "status_pagamento"]],
                    use_container_width=True
                )
            else:
                st.info("Nenhum lançamento financeiro para este cliente.")

# ------------------------------------------------------------------------------
# 2. CADASTRO DE CLIENTES
# ------------------------------------------------------------------------------
elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes e Múltiplos Endereços (Mesmo CNPJ)")
    
    tab_cli1, tab_cli2, tab_cli3 = st.tabs([
        "➕ Cadastrar Novo Cliente", 
        "✏️ Editar Cadastro & Adicionar Endereços", 
        "🗑️ Excluir Cliente"
    ])
    
    with tab_cli1:
        with st.form("form_novo_cliente"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tipo_p = st.selectbox("Tipo de Pessoa *", ["Pessoa Jurídica", "Pessoa Física"])
                nome_raz = st.text_input("Nome Completo ou Razão Social *")
                cpf_cnpj = st.text_input("CPF ou CNPJ *")
                rep_legal = st.text_input("Nome do Representante Legal (para PJ)")

            with col_c2:
                num_prop = st.text_input("Número da Proposta Comercial")
                num_cont = st.text_input("Número do Contrato")
                end_cli = st.text_input("Endereço Comercial / Sede")
                end_emp_inicial = st.text_input("Endereço do 1º Empreendimento / Obra *")

            btn_salvar_cli = st.form_submit_button("Salvar Cliente na Nuvem")
            if btn_salvar_cli:
                if nome_raz.strip() != "":
                    novo_id_cli = max([c["id"] for c in st.session_state.clientes], default=0) + 1
                    novo_cliente = {
                        "id": novo_id_cli,
                        "tipo_pessoa": tipo_p,
                        "nome_razao": nome_raz,
                        "cpf_cnpj": cpf_cnpj,
                        "representante_legal": rep_legal,
                        "endereco_cliente": end_cli,
                        "enderecos_empreendimentos": [end_emp_inicial] if end_emp_inicial else [],
                        "numero_proposta": num_prop,
                        "numero_contrato": num_cont,
                        "data_inicio": str(date.today())
                    }
                    st.session_state.clientes.append(novo_cliente)
                    salvar_aba(st.session_state.clientes, "Clientes")
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    with tab_cli2:
        if st.session_state.clientes:
            map_cli = {c["id"]: c["nome_razao"] for c in st.session_state.clientes}
            cli_edit_id = st.selectbox("Selecione o Cliente para Editar:", list(map_cli.keys()), format_func=lambda x: map_cli[x])
            cli_edit_obj = get_cliente_por_id(cli_edit_id)

            if cli_edit_obj:
                with st.form("form_editar_cliente"):
                    c_e1, c_e2 = st.columns(2)
                    with c_e1:
                        edit_nome_raz = st.text_input("Razão Social / Nome Completo", value=cli_edit_obj.get("nome_razao", ""))
                        edit_cpf_cnpj = st.text_input("CPF / CNPJ", value=cli_edit_obj.get("cpf_cnpj", ""))
                        edit_rep_legal = st.text_input("Representante Legal", value=cli_edit_obj.get("representante_legal", ""))
                    with c_e2:
                        edit_num_prop = st.text_input("Número da Proposta", value=cli_edit_obj.get("numero_proposta", ""))
                        edit_num_cont = st.text_input("Número do Contrato", value=cli_edit_obj.get("numero_contrato", ""))
                        edit_end_cli = st.text_input("Endereço Comercial / Sede", value=cli_edit_obj.get("endereco_cliente", ""))

                    st.markdown("---")
                    st.markdown("###### 🏢 Endereços de Empreendimentos / Obras Cadastrados:")
                    ends = cli_edit_obj.get("enderecos_empreendimentos", [])
                    if isinstance(ends, list):
                        for idx_end, end_atual in enumerate(ends):
                            st.write(f"• **Endereço {idx_end + 1}:** {end_atual}")
                    else:
                        st.write(f"• **Endereço 1:** {ends}")

                    novo_end_incluir = st.text_input("➕ Adicionar Novo Endereço de Empreendimento / Obra:")

                    btn_salvar_edicao = st.form_submit_button("Atualizar Cadastro e Endereços")

                    if btn_salvar_edicao:
                        cli_edit_obj["nome_razao"] = edit_nome_raz
                        cli_edit_obj["cpf_cnpj"] = edit_cpf_cnpj
                        cli_edit_obj["representante_legal"] = edit_rep_legal
                        cli_edit_obj["numero_proposta"] = edit_num_prop
                        cli_edit_obj["numero_contrato"] = edit_num_cont
                        cli_edit_obj["endereco_cliente"] = edit_end_cli

                        if novo_end_incluir.strip():
                            if "enderecos_empreendimentos" not in cli_edit_obj or not isinstance(cli_edit_obj["enderecos_empreendimentos"], list):
                                cli_edit_obj["enderecos_empreendimentos"] = []
                            cli_edit_obj["enderecos_empreendimentos"].append(novo_end_incluir.strip())

                        salvar_aba(st.session_state.clientes, "Clientes")
                        st.success("Cadastro atualizado com sucesso!")
                        st.rerun()

    with tab_cli3:
        if st.session_state.clientes:
            map_cli_del = {c["id"]: c["nome_razao"] for c in st.session_state.clientes}
            cli_excluir_id = st.selectbox("Selecione o Cliente para Excluir:", list(map_cli_del.keys()), format_func=lambda x: map_cli_del[x])
            if st.button("🚨 Excluir Cliente Selecionado", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c["id"] != cli_excluir_id]
                salvar_aba(st.session_state.clientes, "Clientes")
                st.success("Cliente removido com sucesso!")
                st.rerun()

# ------------------------------------------------------------------------------
# 3. DASHBOARD EXECUTIVO
# ------------------------------------------------------------------------------
elif menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento (Sincronizado na Nuvem)")
    
    df_p = pd.DataFrame(st.session_state.processos_principais)
    df_sub = pd.DataFrame(st.session_state.subprocessos)
    df_fin = pd.DataFrame(st.session_state.financeiro)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(st.session_state.clientes))
    c2.metric("Processos Principais", len(df_p))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    
    total_pendente_fin = sum([float(f.get("valor", 0)) for f in st.session_state.financeiro if f.get("status_pagamento") == "Pendente"])
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente_fin:,.2f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos Principais por Status")
        if not df_p.empty and "status" in df_p.columns:
            status_counts = df_p["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            sub_counts = df_sub["orgao_subprocesso"].value_counts().reset_index()
            sub_counts.columns = ["Órgão", "Quantidade"]
            st.bar_chart(sub_counts.set_index("Órgão"))

# ------------------------------------------------------------------------------
# 4. ENTRADA PROCESSO PRINCIPAL (VINCULAÇÃO DINÂMICA DE ENDEREÇOS)
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro e Edição de Processos Principais (SMDU / LICIN / SEI.RIO)")
    
    tab_p1, tab_p2 = st.tabs(["➕ Cadastrar Novo Processo", "✏️ Editar Processo Existente"])
    
    dict_clientes = {c["id"]: c["nome_razao"] for c in st.session_state.clientes} if st.session_state.clientes else {}
    lista_equipe_nomes = list(st.session_state.equipe.keys()) if st.session_state.equipe else ["Anna"]

    with tab_p1:
        if dict_clientes:
            st.markdown("##### Identificação do Cliente e Endereço do Empreendimento")
            
            cli_selecionado_id = st.selectbox("Cliente Cadastrado *", list(dict_clientes.keys()), format_func=lambda x: dict_clientes[x], key="select_cli_p1")
            cliente_obj = get_cliente_por_id(cli_selecionado_id)
            
            raw_ends = cliente_obj.get("enderecos_empreendimentos", []) if cliente_obj else []
            enderecos_disponiveis = raw_ends if isinstance(raw_ends, list) else [raw_ends]
            opcoes_enderecos = enderecos_disponiveis + ["+ Adicionar Novo Endereço para este Cliente"]

            with st.form("form_processo_principal"):
                c_pm1, c_pm2 = st.columns(2)
                
                with c_pm1:
                    end_sel = st.selectbox("Endereço do Empreendimento / Obra *", opcoes_enderecos)
                    novo_end_input = st.text_input("Se selecionou 'Adicionar Novo', digite o endereço aqui:")

                with c_pm2:
                    num_proc_p = st.text_input("Nº do Processo Principal (SMDU/LICIN/SEI.RIO) *", placeholder="Ex: 04/001.234/2026")
                    servico_p = st.text_input("Serviço Contratado *", placeholder="Ex: Licença de Obra / Habite-se")

                st.markdown("##### Atribuição e Prazos")
                c_pm3, c_pm4 = st.columns(2)
                with c_pm3:
                    resp_p = st.selectbox("Responsável pelo Processo Principal *", lista_equipe_nomes)
                    data_inc_p = st.date_input("Data de Início do Processo", value=date.today())
                with c_pm4:
                    prazo_p = st.date_input("Prazo Limite / Validade da Licença", value=None)
                    status_p_init = st.selectbox("Status Inicial", STATUS_OPCOES, index=2)

                btn_salvar_p = st.form_submit_button("Cadastrar e Sincronizar Processo Principal")
                
                if btn_salvar_p:
                    if num_proc_p.strip() != "":
                        if end_sel == "+ Adicionar Novo Endereço para este Cliente":
                            if novo_end_input.strip() != "":
                                end_final = novo_end_input.strip()
                                if not isinstance(cliente_obj.get("enderecos_empreendimentos"), list):
                                    cliente_obj["enderecos_empreendimentos"] = []
                                cliente_obj["enderecos_empreendimentos"].append(end_final)
                                salvar_aba(st.session_state.clientes, "Clientes")
                            else:
                                end_final = "Endereço Não Informado"
                        else:
                            end_final = end_sel
                        
                        novo_id_p = max([p["id"] for p in st.session_state.processos_principais], default=0) + 1
                        novo_p = {
                            "id": novo_id_p,
                            "cliente_id": cliente_obj["id"],
                            "numero_processo_principal": num_proc_p,
                            "endereco_empreendimento": end_final,
                            "servico_contratado": servico_p,
                            "responsavel_principal": resp_p,
                            "status": status_p_init,
                            "data_inicio": str(data_inc_p),
                            "prazo_limite": str(prazo_p) if prazo_p else None
                        }
                        st.session_state.processos_principais.append(novo_p)
                        salvar_aba(st.session_state.processos_principais, "Processos_Principais")
                        st.success("Processo Principal vinculado e salvo na nuvem com sucesso!")
                        st.rerun()
                    else:
                        st.error("Informe o Número do Processo Principal.")
        else:
            st.warning("Nenhum cliente cadastrado. Cadastre um cliente na aba 'Cadastro de Clientes' primeiro.")

    with tab_p2:
        if st.session_state.processos_principais:
            dict_procs = {p["id"]: f"{p['numero_processo_principal']} — {get_cliente_por_id(p['cliente_id'])['nome_razao'] if get_cliente_por_id(p['cliente_id']) else 'Cliente'}" for p in st.session_state.processos_principais}
            proc_p_edit_id = st.selectbox("Selecione o Processo Principal para Editar:", list(dict_procs.keys()), format_func=lambda x: dict_procs[x], key="sel_p_edit_tab")
            obj_p_e = get_processo_por_id(proc_p_edit_id)

            if obj_p_e:
                with st.form("form_edit_proc_p"):
                    c_pe1, c_pe2 = st.columns(2)
                    with c_pe1:
                        edit_p_num = st.text_input("Nº Processo Principal", value=obj_p_e.get('numero_processo_principal', ''))
                        edit_p_serv = st.text_input("Serviço Contratado", value=obj_p_e.get('servico_contratado', ''))
                        edit_p_end = st.text_input("Endereço do Empreendimento", value=obj_p_e.get('endereco_empreendimento', ''))
                    with c_pe2:
                        idx_r_p = lista_equipe_nomes.index(obj_p_e['responsavel_principal']) if obj_p_e.get('responsavel_principal') in lista_equipe_nomes else 0
                        edit_p_resp = st.selectbox("Responsável Principal", lista_equipe_nomes, index=idx_r_p)
                        
                        idx_st_p = STATUS_OPCOES.index(obj_p_e['status']) if obj_p_e.get('status') in STATUS_OPCOES else 0
                        edit_p_st = st.selectbox("Status do Processo", STATUS_OPCOES, index=idx_st_p)

                    btn_salvar_edit_p = st.form_submit_button("Atualizar Processo Principal")
                    if btn_salvar_edit_p:
                        obj_p_e['numero_processo_principal'] = edit_p_num
                        obj_p_e['servico_contratado'] = edit_p_serv
                        obj_p_e['endereco_empreendimento'] = edit_p_end
                        obj_p_e['responsavel_principal'] = edit_p_resp
                        obj_p_e['status'] = edit_p_st

                        salvar_aba(st.session_state.processos_principais, "Processos_Principais")
                        st.success("Processo Principal atualizado!")
                        st.rerun()

# ------------------------------------------------------------------------------
# 5. FILA INDIVIDUAL
# ------------------------------------------------------------------------------
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    user_sel = st.selectbox("Selecionar Integrante:", list(st.session_state.equipe.keys()))
    
    subs_meus = [s for s in st.session_state.subprocessos if s.get("responsavel_sub") == user_sel]
    principais_meus = [p for p in st.session_state.processos_principais if p.get("responsavel_principal") == user_sel]
    
    st.markdown(f"##### Processos Principais sob Responsabilidade de {user_sel} ({len(principais_meus)})")
    if principais_meus:
        for pm in principais_meus:
            cli_p = get_cliente_por_id(pm['cliente_id'])
            st.info(f"**Nº Processo:** {pm.get('numero_processo_principal')} | **Cliente:** {cli_p['nome_razao'] if cli_p else 'N/A'} | **Endereço:** {pm.get('endereco_empreendimento')} | **Status:** {pm.get('status')}")
    else:
        st.write("Nenhum processo principal atribuído.")

    st.markdown(f"##### Subprocessos / Exigências sob Responsabilidade de {user_sel} ({len(subs_meus)})")
    if subs_meus:
        for sm in subs_meus:
            st.warning(f"**Órgão:** {sm.get('orgao_subprocesso')} | **Nº:** {sm.get('numero_subprocesso')} | **Exigência:** {sm.get('descricao_exigencia')} | **Status:** {sm.get('status')}")
    else:
        st.write("Nenhum subprocesso atribuído.")

# ------------------------------------------------------------------------------
# 6. GESTÃO DA EQUIPE
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col_eq1, col_eq2 = st.columns([2, 1])
    with col_eq1:
        st.markdown("##### Integrantes Atuais")
        for nome_f, cargo_f in list(st.session_state.equipe.items()):
            c_f1, c_f2 = st.columns([4, 1])
            with c_f1:
                st.write(f"👤 **{nome_f}** — *{cargo_f}*")
            with c_f2:
                if st.button("Excluir", key=f"del_eq_{nome_f}"):
                    del st.session_state.equipe[nome_f]
                    salvar_aba([{"nome": k, "cargo": v} for k, v in st.session_state.equipe.items()], "Equipe")
                    st.rerun()

    with col_eq2:
        st.markdown("##### Cadastrar Novo Integrante")
        with st.form("form_novo_f"):
            nf = st.text_input("Nome *")
            cf = st.text_input("Função / Cargo *")
            if st.form_submit_button("Cadastrar Funcionário"):
                if nf.strip():
                    st.session_state.equipe[nf.strip()] = cf.strip()
                    salvar_aba([{"nome": k, "cargo": v} for k, v in st.session_state.equipe.items()], "Equipe")
                    st.success("Integrante adicionado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 7. GESTÃO DE ÓRGÃOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro de Órgãos e Autarquias")
    col_o1, col_o2 = st.columns([2, 1])
    with col_o1:
        st.markdown("##### Órgãos Mapeados")
        for org in list(st.session_state.lista_orgaos):
            c_org1, c_org2 = st.columns([4, 1])
            with c_org1:
                st.write(f"🏛️ **{org}**")
            with c_org2:
                if st.button("Excluir", key=f"del_org_{org}"):
                    st.session_state.lista_orgaos.remove(org)
                    salvar_aba([{"nome": o} for o in st.session_state.lista_orgaos], "Orgaos")
                    st.rerun()

    with col_o2:
        st.markdown("##### Cadastrar Novo Órgão")
        with st.form("form_novo_orgao"):
            novo_o = st.text_input("Nome do Órgão / Autarquia *")
            if st.form_submit_button("Cadastrar Órgão"):
                if novo_o.strip():
                    st.session_state.lista_orgaos.append(novo_o.strip())
                    salvar_aba([{"nome": o} for o in st.session_state.lista_orgaos], "Orgaos")
                    st.success("Órgão adicionado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 8. GESTÃO DE SUBPROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Atendimento a Restrições do Processo Principal")
    
    tab_sub1, tab_sub2 = st.tabs(["➕ Cadastrar Novo Subprocesso", "📋 Gerenciar Subprocessos Existentes"])
    
    with tab_sub1:
        if st.session_state.processos_principais:
            dict_p_sub = {p["id"]: f"{p['numero_processo_principal']} — {get_cliente_por_id(p['cliente_id'])['nome_razao'] if get_cliente_por_id(p['cliente_id']) else 'Cliente'} ({p['endereco_empreendimento']})" for p in st.session_state.processos_principais}
            
            with st.form("form_novo_subprocesso"):
                proc_p_id_sel = st.selectbox("Selecione o Processo Principal (SMDU/LICIN) *", list(dict_p_sub.keys()), format_func=lambda x: dict_p_sub[x])
                
                c_sub1, c_sub2 = st.columns(2)
                with c_sub1:
                    orgao_sub = st.selectbox("Órgão do Subprocesso / Exigência *", st.session_state.lista_orgaos)
                    num_sub = st.text_input("Nº do Subprocesso / Requerimento / Prenotação", placeholder="Ex: CBMERJ-10293")
                    desc_exigencia = st.text_area("Descrição do Subprocesso / Objeto da Exigência *")

                with c_sub2:
                    info_relevante_input = st.text_area("Informação Relevante / Ponto de Atenção")
                    resp_sub = st.selectbox("Responsável pelo Subprocesso *", list(st.session_state.equipe.keys()))
                    data_in_sub = st.date_input("Data de Início do Subprocesso", value=date.today())
                    prazo_fim_sub = st.date_input("Prazo Limite para Atendimento", value=None)

                btn_add_sub = st.form_submit_button("Cadastrar e Vincular Subprocesso")
                
                if btn_add_sub:
                    novo_id_sub = max([s["id"] for s in st.session_state.subprocessos], default=0) + 1
                    novo_sub = {
                        "id": novo_id_sub,
                        "processo_principal_id": proc_p_id_sel,
                        "orgao_subprocesso": orgao_sub,
                        "numero_subprocesso": num_sub if num_sub else "Aguardando Número",
                        "descricao_exigencia": desc_exigencia,
                        "informacao_relevante": info_relevante_input,
                        "responsavel_sub": resp_sub,
                        "status": "Em Tramitação",
                        "data_inicio": str(data_in_sub),
                        "prazo_fim": str(prazo_fim_sub) if prazo_fim_sub else None
                    }
                    st.session_state.subprocessos.append(novo_sub)
                    salvar_aba(st.session_state.subprocessos, "Subprocessos")
                    st.success("Subprocesso vinculado com sucesso!")
                    st.rerun()

    with tab_sub2:
        if st.session_state.processos_principais:
            for pm in st.session_state.processos_principais:
                cli_mae = get_cliente_por_id(pm['cliente_id'])
                st.markdown(f"#### 🏢 Processo Principal: `{pm.get('numero_processo_principal')}` — {cli_mae['nome_razao'] if cli_mae else 'Cliente'}")
                st.write(f"**Endereço:** {pm.get('endereco_empreendimento')} | **Responsável:** {pm.get('responsavel_principal')}")
                
                subs_do_p = [s for s in st.session_state.subprocessos if s.get("processo_principal_id") == pm["id"]]
                
                if subs_do_p:
                    for sub in subs_do_p:
                        with st.expander(f"📌 Subprocesso: {sub.get('orgao_subprocesso')} ({sub.get('numero_subprocesso')}) — Responsável: {sub.get('responsavel_sub')}"):
                            st.write(f"**Descrição:** {sub.get('descricao_exigencia')}")
                            if sub.get("informacao_relevante"):
                                st.warning(f"⚠️ **Ponto de Atenção:** {sub['informacao_relevante']}")
                            
                            status_sub_atual = sub.get('status', 'Em Tramitação')
                            opcoes_st = ["Em Tramitação", "Aguardando Documento do Cliente", "Em Exigência", "Concluído / Aprovado"]
                            idx_st = opcoes_st.index(status_sub_atual) if status_sub_atual in opcoes_st else 0
                            novo_st_sub = st.selectbox("Status do Subprocesso", opcoes_st, index=idx_st, key=f"st_sub_{sub['id']}")
                            
                            if st.button("Atualizar Status", key=f"btn_st_sub_{sub['id']}"):
                                sub["status"] = novo_st_sub
                                salvar_aba(st.session_state.subprocessos, "Subprocessos")
                                st.success("Status atualizado!")
                                st.rerun()

                            if st.button(f"🚨 Excluir Subprocesso", key=f"del_sub_{sub['id']}", type="primary"):
                                st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s["id"] != sub["id"]]
                                salvar_aba(st.session_state.subprocessos, "Subprocessos")
                                st.success("Subprocesso removido!")
                                st.rerun()
                else:
                    st.write("Nenhum subprocesso/exigência vinculado a este Processo Principal.")
                st.divider()

# ------------------------------------------------------------------------------
# 9. MÓDULO FINANCEIRO (MARIANA)
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, RRT/ART e Boletos")
    
    tab_fin1, tab_fin2 = st.columns([2, 1])
    
    with tab_fin2:
        st.markdown("##### Novo Lançamento Financeiro")
        dict_clientes_fin = {c["id"]: c["nome_razao"] for c in st.session_state.clientes} if st.session_state.clientes else {}
        
        if dict_clientes_fin:
            cli_fin_id = st.selectbox("Cliente", list(dict_clientes_fin.keys()), format_func=lambda x: dict_clientes_fin[x], key="select_cli_fin")
            procs_p_opcoes = {p["id"]: f"{p['numero_processo_principal']} ({p['endereco_empreendimento']})" for p in st.session_state.processos_principais if p.get("cliente_id") == cli_fin_id}
            
            with st.form("form_novo_financeiro"):
                proc_p_fin_id = st.selectbox("Processo Principal Relacionado", list(procs_p_opcoes.keys()), format_func=lambda x: procs_p_opcoes[x]) if procs_p_opcoes else None
                
                tipo_doc = st.selectbox("Tipo de Encargo", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
                num_doc = st.text_input("Número do Boleto / RRT / ART / DARM")
                desc_fin = st.text_input("Descrição da Taxa")
                val_fin = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
                venc_fin = st.date_input("Data de Vencimento")
                pagador_fin = st.selectbox("Responsável pelo Pagamento", ["B2x (A Reembolsar)", "Cliente Direto"])
                
                btn_add_fin = st.form_submit_button("Lançar no Financeiro")
                if btn_add_fin:
                    novo_id_fin = max([f["id"] for f in st.session_state.financeiro], default=0) + 1
                    novo_fin = {
                        "id": novo_id_fin,
                        "processo_principal_id": proc_p_fin_id,
                        "cliente_id": cli_fin_id,
                        "tipo_documento": tipo_doc,
                        "numero_documento": num_doc,
                        "descricao": desc_fin,
                        "valor": val_fin,
                        "vencimento": str(venc_fin),
                        "pagador": pagador_fin,
                        "status_pagamento": "Pendente",
                        "nota_fiscal_emitida": "Não"
                    }
                    st.session_state.financeiro.append(novo_fin)
                    salvar_aba(st.session_state.financeiro, "Financeiro")
                    st.success("Lançamento registrado com sucesso!")
                    st.rerun()

    with tab_fin1:
        st.markdown("##### Painel de Controle de Contas e Taxas")
        if st.session_state.financeiro:
            for item in list(st.session_state.financeiro):
                cli_f = get_cliente_por_id(item.get("cliente_id"))
                with st.expander(f"💰 {item.get('tipo_documento')} — R$ {float(item.get('valor', 0)):,.2f} | Cliente: {cli_f['nome_razao'] if cli_f else 'N/A'} ({item.get('status_pagamento')})"):
                    st.write(f"**Nº Documento:** {item.get('numero_documento')} | **Pagador:** {item.get('pagador')}")
                    st.write(f"**Descrição:** {item.get('descricao')}")
                    st.write(f"**Vencimento:** {item.get('vencimento')}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("Marcar como Pago", key=f"btn_pago_{item['id']}"):
                            item['status_pagamento'] = "Pago / Quitado"
                            salvar_aba(st.session_state.financeiro, "Financeiro")
                            st.success("Status atualizado!")
                            st.rerun()
                    with c_btn2:
                        if st.button("🗑️ Excluir", key=f"btn_del_fin_{item['id']}"):
                            st.session_state.financeiro = [f for f in st.session_state.financeiro if f['id'] != item['id']]
                            salvar_aba(st.session_state.financeiro, "Financeiro")
                            st.success("Lançamento excluído!")
                            st.rerun()

# ------------------------------------------------------------------------------
# 10. PAINEL GERAL DE PROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Painel Geral de Processos":
    st.subheader("Visão Geral de Processos Principais e Seus Subprocessos por Endereço")
    
    if st.session_state.processos_principais:
        for pm in list(st.session_state.processos_principais):
            cli_m = get_cliente_por_id(pm['cliente_id'])
            with st.expander(f"PROCESSO PRINCIPAL: {pm.get('numero_processo_principal')} | {cli_m['nome_razao'] if cli_m else 'Cliente'} — Resp: {pm.get('responsavel_principal')}"):
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    st.write(f"**Endereço do Empreendimento:** {pm.get('endereco_empreendimento')}")
                    st.write(f"**Serviço Contratado:** {pm.get('servico_contratado')}")
                with c_p2:
                    st.write(f"**Status Principal:** `{pm.get('status')}`")

                subs = [s for s in st.session_state.subprocessos if s.get("processo_principal_id") == pm["id"]]
                st.markdown(f"###### Subprocessos / Restrições Vinculadas ({len(subs)})")
                if subs:
                    for sb in subs:
                        st.info(f"**Órgão:** {sb.get('orgao_subprocesso')} | **Nº:** {sb.get('numero_subprocesso')} | **Resp:** {sb.get('responsavel_sub')} | **Status:** `{sb.get('status')}`")

                if st.button(f"🚨 Excluir Processo Principal e Subprocessos", key=f"del_pm_{pm['id']}", type="primary"):
                    st.session_state.processos_principais = [p for p in st.session_state.processos_principais if p["id"] != pm["id"]]
                    st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s.get("processo_principal_id") != pm["id"]]
                    salvar_aba(st.session_state.processos_principais, "Processos_Principais")
                    salvar_aba(st.session_state.subprocessos, "Subprocessos")
                    st.success("Removidos com sucesso!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 11. RELATÓRIOS
# ------------------------------------------------------------------------------
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    if st.session_state.processos_principais:
        dados_relatorio = []
        for p in st.session_state.processos_principais:
            cli_r = get_cliente_por_id(p['cliente_id'])
            dados_relatorio.append({
                "Nº Processo": p.get("numero_processo_principal"),
                "Cliente": cli_r['nome_razao'] if cli_r else "N/A",
                "Endereço Empreendimento": p.get("endereco_empreendimento"),
                "Serviço Contratado": p.get("servico_contratado"),
                "Responsável": p.get("responsavel_principal"),
                "Status": p.get("status")
            })
        df_m = pd.DataFrame(dados_relatorio)
        st.dataframe(df_m, use_container_width=True)
        csv_data = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar Processos Principais (CSV)", data=csv_data, file_name="relatorio_processos_principais_b2x.csv", mime="text/csv")
    else:
        st.info("Nenhum processo cadastrado para emissão de relatório.")
