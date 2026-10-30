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
# CONEXÃO COM GOOGLE SHEETS
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
# INICIALIZAÇÃO SEGURA DAS BASES DE DADOS NA SESSÃO
# ------------------------------------------------------------------------------

# 1. Equipe
if "equipe" not in st.session_state or not isinstance(st.session_state.equipe, dict):
    st.session_state.equipe = {
        "Gabriela": "Captação / Negociação / Entrada",
        "Mariana": "Financeiro / Propostas / Pagamentos",
        "Anna": "Processos / Exigências / RRT / Relatórios",
        "Bruno": "Processos / RGI / Diligências Externas",
        "Camila": "Atendimento / Obra / Mídias",
        "Alessandra": "Projetos / Prefeitura",
        "Lilian": "Projetos / Prefeitura / RRT"
    }

# 2. Órgãos
if "lista_orgaos" not in st.session_state or not isinstance(st.session_state.lista_orgaos, list):
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

# 3. Clientes
if "clientes" not in st.session_state or not isinstance(st.session_state.clientes, list) or len(st.session_state.clientes) == 0:
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

# 4. Processos Principais
if "processos_principais" not in st.session_state or not isinstance(st.session_state.processos_principais, list) or len(st.session_state.processos_principais) == 0:
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
                {"data": "2026-03-10", "texto": "Publicado despacho de exigências no SEI.RIO."}
            ]
        }
    ]

# 5. Subprocessos
if "subprocessos" not in st.session_state or not isinstance(st.session_state.subprocessos, list) or len(st.session_state.subprocessos) == 0:
    st.session_state.subprocessos = [
        {
            "id": 101,
            "processo_principal_id": 1,
            "cliente_id": 1,
            "orgao_subprocesso": "Corpo de Bombeiros (CBMERJ)",
            "numero_subprocesso": "CBMERJ-2026/99812",
            "descricao_exigencia": "Laudo de Exigências e Certificado de Aprovação",
            "informacao_relevante": "Reserva técnica de incêndio necessária no castelo d'água.",
            "responsavel_sub": "Bruno",
            "status": "Em Tramitação",
            "data_inicio": date(2026, 3, 15),
            "prazo_fim": date(2026, 11, 30),
            "notas_internas": [],
            "despachos": [],
            "documentos": []
        }
    ]

for sub in st.session_state.subprocessos:
    if "processo_principal_id" not in sub and "processo_mae_id" in sub:
        sub["processo_principal_id"] = sub["processo_mae_id"]

# 6. Financeiro
if "financeiro" not in st.session_state or not isinstance(st.session_state.financeiro, list) or len(st.session_state.financeiro) == 0:
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

# MENU LATERAL EM ORDEM ALFABÉTICA
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
# 1. BUSCA INTEGRADA (LUPA 360°)
# ------------------------------------------------------------------------------
if menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente")
    
    nombres_clientes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else []
    cliente_sel_nome = st.selectbox("Selecione ou Pesquise o Nome do Cliente:", [""] + nombres_clientes)
    
    if cliente_sel_nome != "":
        cliente_obj = next((c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome), None)
        
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
                for end in cliente_obj.get("enderecos_empreendimentos", []):
                    st.write(f"• {end}")

            st.divider()
            
            procs_p_cli = [p for p in st.session_state.processos_principais if p.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais e Subprocessos ({len(procs_p_cli)})")
            
            if procs_p_cli:
                for pmc in procs_p_cli:
                    st.info(f"**Endereço:** {pmc.get('endereco_empreendimento', 'N/A')}\n\n**Processo Principal:** {pmc.get('numero_processo_principal', 'N/A')} | **Status:** `{pmc.get('status', 'N/A')}`")
                    subs_cli = [s for s in st.session_state.subprocessos if s.get("processo_principal_id", s.get("processo_mae_id")) == pmc["id"]]
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
    else:
        st.info("Selecione um cliente acima para visualizar a ficha completa.")

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
                    st.session_state.clientes.append({
                        "id": novo_id_cli,
                        "tipo_pessoa": tipo_p,
                        "nome_razao": nome_raz,
                        "cpf_cnpj": cpf_cnpj,
                        "representante_legal": rep_legal,
                        "endereco_cliente": end_cli,
                        "enderecos_empreendimentos": [end_emp_inicial] if end_emp_inicial else [],
                        "numero_proposta": num_prop,
                        "numero_contrato": num_cont,
                        "data_inicio": date.today()
                    })
                    salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe a Razão Social ou Nome do Cliente.")

    with tab_cli2:
        if st.session_state.clientes:
            st.markdown("##### Alterar Dados e Incluir Novos Endereços de Obra / Empreendimento")
            cli_edit_nome = st.selectbox("Selecione o Cliente para Editar:", [c["nome_razao"] for c in st.session_state.clientes], key="sel_cli_edit")
            cli_edit_obj = next((c for c in st.session_state.clientes if c["nome_razao"] == cli_edit_nome), None)

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
                    for idx_end, end_atual in enumerate(cli_edit_obj.get("enderecos_empreendimentos", [])):
                        st.write(f"• **Endereço {idx_end + 1}:** {end_atual}")

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
                            if "enderecos_empreendimentos" not in cli_edit_obj:
                                cli_edit_obj["enderecos_empreendimentos"] = []
                            cli_edit_obj["enderecos_empreendimentos"].append(novo_end_incluir.strip())

                        salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                        st.success("Cadastro atualizado com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum cliente cadastrado no momento.")

    with tab_cli3:
        if st.session_state.clientes:
            cli_excluir = st.selectbox("Selecione o Cliente para Excluir:", [c["nome_razao"] for c in st.session_state.clientes], key="sel_cli_del")
            if st.button(f"🚨 Excluir Cliente '{cli_excluir}'", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c["nome_razao"] != cli_excluir]
                salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                st.success("Cliente removido com sucesso!")
                st.rerun()
        else:
            st.info("Nenhum cliente cadastrado no momento.")

    st.divider()
    st.markdown("##### Base Geral de Clientes")
    df_cli_view = pd.DataFrame(st.session_state.clientes)
    if not df_cli_view.empty:
        st.dataframe(df_cli_view[["id", "tipo_pessoa", "nome_razao", "cpf_cnpj", "numero_proposta", "numero_contrato"]], use_container_width=True)
    else:
        st.info("Nenhum cliente na base de dados.")

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
    
    total_pendente_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty and "status_pagamento" in df_fin.columns else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente_fin:,.2f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos Principais por Status")
        if not df_p.empty and "status" in df_p.columns:
            status_counts = df_p["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))
        else:
            st.info("Nenhum processo cadastrado para exibição do gráfico.")

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            sub_counts = df_sub["orgao_subprocesso"].value_counts().reset_index()
            sub_counts.columns = ["Órgão", "Quantidade"]
            st.bar_chart(sub_counts.set_index("Órgão"))
        else:
            st.info("Nenhum subprocesso cadastrado para exibição do gráfico.")

# ------------------------------------------------------------------------------
# 4. ENTRADA PROCESSO PRINCIPAL
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro e Edição de Processos Principais (SMDU / LICIN / SEI.RIO)")
    
    tab_p1, tab_p2 = st.tabs(["➕ Cadastrar Novo Processo", "✏️ Editar Processo Existente"])
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else ["Cadastre um Cliente Primeiro"]
    lista_equipe_nomes = list(st.session_state.equipe.keys()) if st.session_state.equipe else ["Anna"]

    with tab_p1:
        with st.form("form_processo_principal"):
            st.markdown("##### Identificação do Cliente e Endereço do Empreendimento")
            c_pm1, c_pm2 = st.columns(2)
            
            with c_pm1:
                cliente_sel_nome = st.selectbox("Cliente Cadastrado *", lista_clientes_nomes)
                cliente_obj = next((c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome), None)
                
                end_opcoes = cliente_obj.get("enderecos_empreendimentos", []) + ["+ Adicionar Novo Endereço para este Cliente"] if cliente_obj else ["Endereço Padrão"]
                end_sel = st.selectbox("Endereço do Empreendimento / Obra *", end_opcoes)
                
                if end_sel == "+ Adicionar Novo Endereço para este Cliente":
                    novo_end_input = st.text_input("Digite o Novo Endereço do Empreendimento:")
                else:
                    novo_end_input = end_sel

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
                if cliente_obj and num_proc_p.strip() != "":
                    if end_sel == "+ Adicionar Novo Endereço para este Cliente" and novo_end_input.strip() != "":
                        if "enderecos_empreendimentos" not in cliente_obj:
                            cliente_obj["enderecos_empreendimentos"] = []
                        cliente_obj["enderecos_empreendimentos"].append(novo_end_input.strip())
                    
                    end_final = novo_end_input.strip() if novo_end_input.strip() != "" else end_sel
                    
                    novo_id_p = max([p["id"] for p in st.session_state.processos_principais], default=0) + 1
                    st.session_state.processos_principais.append({
                        "id": novo_id_p,
                        "cliente_id": cliente_obj["id"],
                        "cliente_nome": cliente_obj["nome_razao"],
                        "numero_processo_principal": num_proc_p,
                        "endereco_empreendimento": end_final,
                        "servico_contratado": servico_p,
                        "responsavel_principal": resp_p,
                        "status": status_p_init,
                        "data_inicio": data_inc_p,
                        "prazo_limite": prazo_p,
                        "despachos": []
                    })
                    salvar_dados(pd.DataFrame(st.session_state.processos_principais), "Processos_Principais")
                    salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                    st.success("Processo Principal cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Selecione um cliente válido e informe o Número do Processo Principal.")

    with tab_p2:
        if st.session_state.processos_principais:
            procs_lista = [f"{p['numero_processo_principal']} — {p['cliente_nome']}" for p in st.session_state.processos_principais]
            proc_p_edit_sel = st.selectbox("Selecione o Processo Principal para Editar:", procs_lista, key="sel_p_edit_tab")
            idx_p_e = procs_lista.index(proc_p_edit_sel)
            obj_p_e = st.session_state.processos_principais[idx_p_e]

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
                    edit_p_prazo = st.date_input("Prazo Limite / Validade", value=obj_p_e.get('prazo_limite', None))

                btn_salvar_edit_p = st.form_submit_button("Atualizar Processo Principal")
                if btn_salvar_edit_p:
                    obj_p_e['numero_processo_principal'] = edit_p_num
                    obj_p_e['servico_contratado'] = edit_p_serv
                    obj_p_e['endereco_empreendimento'] = edit_p_end
                    obj_p_e['responsavel_principal'] = edit_p_resp
                    obj_p_e['status'] = edit_p_st
                    obj_p_e['prazo_limite'] = edit_p_prazo

                    salvar_dados(pd.DataFrame(st.session_state.processos_principais), "Processos_Principais")
                    st.success("Processo Principal atualizado com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum processo cadastrado para editar.")

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
            st.info(f"**Nº Processo Principal:** {pm.get('numero_processo_principal', 'N/A')} | **Cliente:** {pm.get('cliente_nome', 'N/A')} | **Endereço:** {pm.get('endereco_empreendimento', 'N/A')} | **Status:** {pm.get('status', 'N/A')}")
    else:
        st.write("Nenhum processo principal sob responsabilidade deste integrante.")

    st.markdown(f"##### Subprocessos / Exigências sob Responsabilidade de {user_sel} ({len(subs_meus)})")
    if subs_meus:
        for sm in subs_meus:
            st.warning(f"**Órgão:** {sm.get('orgao_subprocesso', 'Órgão')} | **Nº:** {sm.get('numero_subprocesso', 'N/A')} | **Exigência:** {sm.get('descricao_exigencia', 'Sem descrição')} | **Status:** {sm.get('status', 'N/A')}")
    else:
        st.write("Nenhum subprocesso sob responsabilidade deste integrante.")

# ------------------------------------------------------------------------------
# 6. GESTÃO DA EQUIPE
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col_eq1, col_eq2 = st.columns([2, 1])
    with col_eq1:
        st.markdown("##### Integrantes Atuais")
        if st.session_state.equipe:
            for nome_f, cargo_f in list(st.session_state.equipe.items()):
                c_f1, c_f2 = st.columns([4, 1])
                with c_f1:
                    st.write(f"👤 **{nome_f}** — *{cargo_f}*")
                with c_f2:
                    if st.button("Excluir", key=f"del_eq_{nome_f}"):
                        del st.session_state.equipe[nome_f]
                        st.rerun()
        else:
            st.info("Nenhum integrante cadastrado.")

    with col_eq2:
        st.markdown("##### Cadastrar Novo Integrante")
        with st.form("form_novo_f"):
            nf = st.text_input("Nome *")
            cf = st.text_input("Função / Cargo *")
            if st.form_submit_button("Cadastrar Funcionário"):
                if nf.strip():
                    st.session_state.equipe[nf.strip()] = cf.strip()
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
        if st.session_state.lista_orgaos:
            for org in list(st.session_state.lista_orgaos):
                c_org1, c_org2 = st.columns([4, 1])
                with c_org1:
                    st.write(f"🏛️ **{org}**")
                with c_org2:
                    if st.button("Excluir", key=f"del_org_{org}"):
                        st.session_state.lista_orgaos.remove(org)
                        st.rerun()
        else:
            st.info("Nenhum órgão cadastrado.")

    with col_o2:
        st.markdown("##### Cadastrar Novo Órgão")
        with st.form("form_novo_orgao"):
            novo_o = st.text_input("Nome do Órgão / Autarquia *")
            if st.form_submit_button("Cadastrar Órgão"):
                if novo_o.strip():
                    st.session_state.lista_orgaos.append(novo_o.strip())
                    st.success("Órgão adicionado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 8. GESTÃO DE SUBPROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Atendimento a Restrições do Processo Principal")
    
    tab_sub1, tab_sub2 = st.tabs(["➕ Cadastrar Novo Subprocesso", "📋 Gerenciar Subprocessos Existentes"])
    
    with tab_sub1:
        st.markdown("##### Vincular Subprocesso a um Processo Principal (SMDU/LICIN)")
        
        if st.session_state.processos_principais:
            with st.form("form_novo_subprocesso"):
                opcoes_p = [f"{p['numero_processo_principal']} — {p['cliente_nome']} ({p['endereco_empreendimento']})" for p in st.session_state.processos_principais]
                proc_p_sel_str = st.selectbox("Selecione o Processo Principal (SMDU/LICIN) e Endereço *", opcoes_p)
                
                idx_p_sel = opcoes_p.index(proc_p_sel_str)
                obj_p_sel = st.session_state.processos_principais[idx_p_sel]
                
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
                    st.session_state.subprocessos.append({
                        "id": novo_id_sub,
                        "processo_principal_id": obj_p_sel["id"],
                        "cliente_id": obj_p_sel["cliente_id"],
                        "orgao_subprocesso": orgao_sub,
                        "numero_subprocesso": num_sub if num_sub else "Aguardando Número",
                        "descricao_exigencia": desc_exigencia,
                        "informacao_relevante": info_relevante_input,
                        "responsavel_sub": resp_sub,
                        "status": "Em Tramitação",
                        "data_inicio": data_in_sub,
                        "prazo_fim": prazo_fim_sub,
                        "notas_internas": [],
                        "despachos": [],
                        "documentos": []
                    })
                    salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                    st.success("Subprocesso vinculado e salvo com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum Processo Principal cadastrado para vincular subprocessos.")

    with tab_sub2:
        st.markdown("##### Acompanhamento de Subprocessos por Processo Principal")
        
        if st.session_state.processos_principais:
            for pm in st.session_state.processos_principais:
                st.markdown(f"#### 🏢 Processo Principal: `{pm.get('numero_processo_principal', 'N/A')}` — {pm.get('cliente_nome', 'N/A')}")
                st.write(f"**Endereço do Empreendimento:** {pm.get('endereco_empreendimento', 'N/A')} | **Responsável:** {pm.get('responsavel_principal', 'N/A')}")
                
                subs_do_p = [s for s in st.session_state.subprocessos if s.get("processo_principal_id", s.get("processo_mae_id")) == pm["id"]]
                
                if subs_do_p:
                    for sub in subs_do_p:
                        with st.expander(f"📌 Subprocesso: {sub.get('orgao_subprocesso', 'Órgão')} ({sub.get('numero_subprocesso', 'N/A')}) — Responsável: {sub.get('responsavel_sub', 'N/A')}"):
                            
                            if sub.get("informacao_relevante"):
                                st.warning(f"⚠️ **Informação Relevante / Ponto de Atenção:** {sub['informacao_relevante']}")
                            
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.markdown("###### Descrição do Subprocesso")
                                st.write(sub.get('descricao_exigencia', 'Sem descrição cadastrada.'))
                                st.write(f"**Data de Início:** {sub['data_inicio'].strftime('%d/%m/%Y') if sub.get('data_inicio') else 'N/A'}")
                                st.write(f"**Prazo Limite:** {sub['prazo_fim'].strftime('%d/%m/%Y') if sub.get('prazo_fim') else 'N/A'}")
                            
                            with col_s2:
                                status_sub_atual = sub.get('status', 'Em Tramitação')
                                opcoes_st = ["Em Tramitação", "Aguardando Documento do Cliente", "Em Exigência", "Concluído / Aprovado"]
                                idx_st = opcoes_st.index(status_sub_atual) if status_sub_atual in opcoes_st else 0
                                novo_st_sub = st.selectbox("Status do Subprocesso", opcoes_st, index=idx_st, key=f"st_sub_{sub['id']}")
                                if st.button("Atualizar Status", key=f"btn_st_sub_{sub['id']}"):
                                    sub["status"] = novo_st_sub
                                    salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                    st.success("Status atualizado!")
                                    st.rerun()

                            # POP-OVER DE EDIÇÃO DE DADOS DO SUBPROCESSO
                            with st.popover("✏️ Editar Dados do Subprocesso"):
                                with st.form(key=f"form_edit_sub_{sub['id']}"):
                                    st.markdown("##### Editar Informações Cadastradas")
                                    
                                    idx_orgao = st.session_state.lista_orgaos.index(sub['orgao_subprocesso']) if sub.get('orgao_subprocesso') in st.session_state.lista_orgaos else 0
                                    edit_orgao = st.selectbox("Órgão do Subprocesso", st.session_state.lista_orgaos, index=idx_orgao)
                                    edit_num_sub = st.text_input("Nº do Subprocesso", value=sub.get('numero_subprocesso', ''))
                                    edit_desc = st.text_area("Descrição / Objeto da Exigência", value=sub.get('descricao_exigencia', ''))
                                    edit_info_rel = st.text_area("Informação Relevante / Ponto de Atenção", value=sub.get('informacao_relevante', ''))
                                    
                                    equipe_lista = list(st.session_state.equipe.keys())
                                    idx_resp = equipe_lista.index(sub['responsavel_sub']) if sub.get('responsavel_sub') in equipe_lista else 0
                                    edit_resp = st.selectbox("Responsável pelo Subprocesso", equipe_lista, index=idx_resp)
                                    
                                    edit_dt_ini = st.date_input("Data de Início", value=sub.get('data_inicio', date.today()))
                                    edit_dt_fim = st.date_input("Prazo Limite", value=sub.get('prazo_fim', None))
                                    
                                    btn_salvar_sub_edit = st.form_submit_button("Salvar Alterações")
                                    
                                    if btn_salvar_sub_edit:
                                        sub['orgao_subprocesso'] = edit_orgao
                                        sub['numero_subprocesso'] = edit_num_sub
                                        sub['descricao_exigencia'] = edit_desc
                                        sub['informacao_relevante'] = edit_info_rel
                                        sub['responsavel_sub'] = edit_resp
                                        sub['data_inicio'] = edit_dt_ini
                                        sub['prazo_fim'] = edit_dt_fim
                                        
                                        salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                        st.success("Subprocesso atualizado!")
                                        st.rerun()

                            st.markdown("---")
                            st.markdown("###### 📝 Notas e Observações Internas da Equipe")
                            if sub.get("notas_internas"):
                                for idx_n, nota in enumerate(sub["notas_internas"]):
                                    col_nt1, col_nt2 = st.columns([5, 1])
                                    with col_nt1:
                                        st.info(f"**[{nota['data']}] por {nota['autor']}:** {nota['texto']}")
                                    with col_nt2:
                                        if st.button("🗑️", key=f"del_nota_{sub['id']}_{idx_n}"):
                                            sub["notas_internas"].pop(idx_n)
                                            salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                            st.rerun()
                            else:
                                st.write("Nenhuma nota cadastrada.")
                            
                            c_n1, c_n2 = st.columns([3, 1])
                            with c_n1:
                                nova_nota_txt = st.text_input("Inserir Nova Nota Interna:", key=f"txt_nota_{sub['id']}")
                            with c_n2:
                                autor_nota = st.selectbox("Autor:", list(st.session_state.equipe.keys()), key=f"aut_nota_{sub['id']}")
                                
                            if st.button("Salvar Nota Interna", key=f"btn_nota_{sub['id']}"):
                                if nova_nota_txt.strip() != "":
                                    if "notas_internas" not in sub:
                                        sub["notas_internas"] = []
                                    sub["notas_internas"].append({
                                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                        "autor": autor_nota,
                                        "texto": nova_nota_txt.strip()
                                    })
                                    st.success("Nota interna adicionada!")
                                    st.rerun()

                            st.markdown("---")
                            st.markdown("###### Despachos & Histórico de Acompanhamento Oficial")
                            if sub.get("despachos"):
                                for idx_d, d in enumerate(sub["despachos"]):
                                    col_dp1, col_dp2 = st.columns([5, 1])
                                    with col_dp1:
                                        st.write(f"📅 **[{d['data']}]** — {d['texto']}")
                                    with col_dp2:
                                        if st.button("🗑️", key=f"del_desp_{sub['id']}_{idx_d}"):
                                            sub["despachos"].pop(idx_d)
                                            salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                            st.rerun()
                            
                            novo_despacho_txt = st.text_input("Novo Despacho Oficial / Parecer:", key=f"txt_desp_{sub['id']}")
                            if st.button("Inserir Despacho", key=f"btn_desp_{sub['id']}"):
                                if novo_despacho_txt.strip() != "":
                                    if "despachos" not in sub:
                                        sub["despachos"] = []
                                    sub["despachos"].append({
                                        "data": date.today().strftime("%Y-%m-%d"),
                                        "texto": novo_despacho_txt.strip()
                                    })
                                    st.success("Despacho registrado!")
                                    st.rerun()

                            st.markdown("---")
                            st.markdown("###### Documentos & Comprovantes Anexados")
                            if sub.get("documentos"):
                                for idx_doc, doc in enumerate(sub["documentos"]):
                                    col_dc1, col_dc2 = st.columns([5, 1])
                                    with col_dc1:
                                        st.write(f"📄 **{doc['nome']}** (Data: {doc['data']})")
                                    with col_dc2:
                                        if st.button("🗑️ Excluir Doc", key=f"del_doc_{sub['id']}_{idx_doc}"):
                                            sub["documentos"].pop(idx_doc)
                                            salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                            st.rerun()
                            else:
                                st.write("Nenhum documento anexado ainda.")
                            
                            up_doc_sub = st.file_uploader("Anexar Comprovante / Licença (PDF)", type=["pdf", "png", "jpg"], key=f"up_sub_{sub['id']}")
                            if up_doc_sub:
                                if st.button("Salvar Arquivo no Subprocesso", key=f"btn_up_sub_{sub['id']}"):
                                    novo_id_d = len(sub.get("documentos", [])) + 1
                                    if "documentos" not in sub:
                                        sub["documentos"] = []
                                    sub["documentos"].append({"id": novo_id_d, "nome": up_doc_sub.name, "data": date.today().strftime("%Y-%m-%d")})
                                    st.success("Documento salvo!")
                                    st.rerun()

                            if st.button(f"🚨 Excluir Subprocesso Completo", key=f"del_sub_{sub['id']}", type="primary"):
                                st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s["id"] != sub["id"]]
                                salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                st.success("Subprocesso removido!")
                                st.rerun()
                else:
                    st.write("Nenhum subprocesso/exigência vinculado a este Processo Principal.")
                st.divider()
        else:
            st.info("Nenhum Processo Principal cadastrado no momento.")

# ------------------------------------------------------------------------------
# 9. MÓDULO FINANCEIRO (MARIANA)
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, RRT/ART e Boletos")
    
    tab_fin1, tab_fin2 = st.columns([2, 1])
    
    with tab_fin2:
        st.markdown("##### Novo Lançamento Financeiro")
        with st.form("form_novo_financeiro"):
            cli_fin_nome = st.selectbox("Cliente", [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum"])
            
            cli_id_sel = next((c["id"] for c in st.session_state.clientes if c["nome_razao"] == cli_fin_nome), 1)
            procs_p_opcoes = [f"{p['numero_processo_principal']} ({p['endereco_empreendimento']})" for p in st.session_state.processos_principais if p.get("cliente_id") == cli_id_sel]
            
            proc_p_fin = st.selectbox("Processo Principal e Endereço Relacionado", procs_p_opcoes if procs_p_opcoes else ["Nenhum"])
            
            tipo_doc = st.selectbox("Tipo de Encargo", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
            num_doc = st.text_input("Número do Boleto / RRT / ART / DARM")
            desc_fin = st.text_input("Descrição da Taxa")
            val_fin = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
            venc_fin = st.date_input("Data de Vencimento")
            pagador_fin = st.selectbox("Responsável pelo Pagamento", ["B2x (A Reembolsar)", "Cliente Direto"])
            
            uploaded_file = st.file_uploader("Anexar Comprovante / Guia (PDF)", type=["pdf", "png", "jpg"])
            
            btn_add_fin = st.form_submit_button("Lançar no Financeiro")
            if btn_add_fin:
                novo_id_fin = max([f["id"] for f in st.session_state.financeiro], default=0) + 1
                st.session_state.financeiro.append({
                    "id": novo_id_fin,
                    "processo_principal_id": 1,
                    "subprocesso_id": None,
                    "cliente_id": cli_id_sel,
                    "tipo_documento": tipo_doc,
                    "numero_documento": num_doc,
                    "descricao": desc_fin,
                    "valor": val_fin,
                    "vencimento": venc_fin,
                    "pagador": pagador_fin,
                    "status_pagamento": "Pendente",
                    "nota_fiscal_emitida": "Não",
                    "comprovante_anexado": uploaded_file.name if uploaded_file else None
                })
                salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                st.success("Lançamento financeiro registrado com sucesso!")
                st.rerun()

    with tab_fin1:
        st.markdown("##### Painel de Controle de Contas e Taxas")
        if st.session_state.financeiro:
            for item in list(st.session_state.financeiro):
                venc_txt = item['vencimento'].strftime('%d/%m/%Y') if item.get('vencimento') and isinstance(item['vencimento'], (date, datetime)) else 'N/A'
                with st.expander(f"💰 {item.get('tipo_documento', 'Encargo')} — R$ {item.get('valor', 0.0):,.2f} | Vencimento: {venc_txt} ({item.get('status_pagamento', 'Pendente')})"):
                    st.write(f"**Nº Documento:** {item.get('numero_documento', 'N/A')} | **Pagador:** {item.get('pagador', 'N/A')}")
                    st.write(f"**Descrição:** {item.get('descricao', 'N/A')}")
                    
                    c_btn1, c_btn2, c_btn3 = st.columns(3)
                    with c_btn1:
                        if st.button("Marcar como Pago", key=f"btn_pago_{item['id']}"):
                            item['status_pagamento'] = "Pago / Quitado"
                            salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                            st.success("Status atualizado!")
                            st.rerun()
                    with c_btn2:
                        with st.popover("✏️ Editar Lançamento"):
                            with st.form(key=f"form_edit_fin_{item['id']}"):
                                op_tipos = ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"]
                                e_tipo = st.selectbox("Tipo", op_tipos, index=op_tipos.index(item['tipo_documento']) if item.get('tipo_documento') in op_tipos else 0)
                                e_num = st.text_input("Nº Documento", value=item.get('numero_documento', ''))
                                e_desc = st.text_input("Descrição", value=item.get('descricao', ''))
                                e_val = st.number_input("Valor (R$)", value=float(item.get('valor', 0.0)))
                                e_venc = st.date_input("Vencimento", value=item.get('vencimento', date.today()))
                                e_pag = st.selectbox("Pagador", ["B2x (A Reembolsar)", "Cliente Direto"], index=0 if item.get('pagador') == "B2x (A Reembolsar)" else 1)
                                
                                if st.form_submit_button("Salvar Edição"):
                                    item['tipo_documento'] = e_tipo
                                    item['numero_documento'] = e_num
                                    item['descricao'] = e_desc
                                    item['valor'] = e_val
                                    item['vencimento'] = e_venc
                                    item['pagador'] = e_pag
                                    salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                                    st.success("Lançamento atualizado!")
                                    st.rerun()
                    with c_btn3:
                        if st.button("🗑️ Excluir", key=f"btn_del_fin_{item['id']}"):
                            st.session_state.financeiro = [f for f in st.session_state.financeiro if f['id'] != item['id']]
                            salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                            st.success("Lançamento excluído!")
                            st.rerun()
        else:
            st.info("Nenhum encargo financeiro registrado.")

# ------------------------------------------------------------------------------
# 10. PAINEL GERAL DE PROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Painel Geral de Processos":
    st.subheader("Visão Geral de Processos Principais e Seus Subprocessos por Endereço")
    
    if st.session_state.processos_principais:
        for pm in list(st.session_state.processos_principais):
            prazo_txt = pm['prazo_limite'].strftime('%d/%m/%Y') if pm.get('prazo_limite') and isinstance(pm['prazo_limite'], (date, datetime)) else 'N/A'
            with st.expander(f"PROCESSO PRINCIPAL: {pm.get('numero_processo_principal', 'N/A')} | {pm.get('cliente_nome', 'N/A')} — Resp: {pm.get('responsavel_principal', 'N/A')}"):
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    st.write(f"**Endereço do Empreendimento:** {pm.get('endereco_empreendimento', 'N/A')}")
                    st.write(f"**Serviço Contratado:** {pm.get('servico_contratado', 'N/A')}")
                with c_p2:
                    st.write(f"**Status Principal:** `{pm.get('status', 'N/A')}`")
                    st.write(f"**Prazo Validade:** {prazo_txt}")

                subs = [s for s in st.session_state.subprocessos if s.get("processo_principal_id", s.get("processo_mae_id")) == pm["id"]]
                st.markdown(f"###### Subprocessos / Restrições Vinculadas ({len(subs)})")
                if subs:
                    for sb in subs:
                        st.info(f"**Órgão:** {sb.get('orgao_subprocesso', 'Órgão')} | **Nº:** {sb.get('numero_subprocesso', 'N/A')} | **Resp:** {sb.get('responsavel_sub', 'N/A')} | **Status:** `{sb.get('status', 'N/A')}`")
                else:
                    st.write("Nenhum subprocesso/exigência vinculado.")

                if st.button(f"🚨 Excluir Processo Principal e Subprocessos", key=f"del_pm_{pm['id']}", type="primary"):
                    st.session_state.processos_principais = [p for p in st.session_state.processos_principais if p["id"] != pm["id"]]
                    st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s.get("processo_principal_id", s.get("processo_mae_id")) != pm["id"]]
                    salvar_dados(pd.DataFrame(st.session_state.processos_principais), "Processos_Principais")
                    salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                    st.success("Removidos com sucesso!")
                    st.rerun()
    else:
        st.info("Nenhum Processo Principal cadastrado.")

# ------------------------------------------------------------------------------
# 11. RELATÓRIOS
# ------------------------------------------------------------------------------
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    df_m = pd.DataFrame(st.session_state.processos_principais)
    if not df_m.empty and "numero_processo_principal" in df_m.columns:
        st.dataframe(df_m[["numero_processo_principal", "cliente_nome", "endereco_empreendimento", "servico_contratado", "responsavel_principal", "status"]], use_container_width=True)
        csv_data = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar Processos Principais (CSV)", data=csv_data, file_name="relatorio_processos_principais_b2x.csv", mime="text/csv")
    else:
        st.info("Nenhum processo cadastrado para emissão de relatório.")
