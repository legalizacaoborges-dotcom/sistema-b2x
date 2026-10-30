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
# INICIALIZAÇÃO E MANUTENÇÃO DAS BASES DE DADOS NA SESSÃO
# ------------------------------------------------------------------------------

# 1. Equipe
if "equipe" not in st.session_state or not st.session_state.equipe:
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
if "lista_orgaos" not in st.session_state or not st.session_state.lista_orgaos:
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
if "clientes" not in st.session_state or not st.session_state.clientes:
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
if "processos_principais" not in st.session_state or not st.session_state.processos_principais:
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

# 5. Subprocessos
if "subprocessos" not in st.session_state or not st.session_state.subprocessos:
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
                {"data": "2026-03-16 10:00", "autor": "Bruno", "texto": "Reunião com o major do DGST marcada para quinta-feira."}
            ],
            "despachos": [
                {"data": "2026-03-20", "texto": "Protocolado projeto de segurança contra incêndio no DGST."}
            ],
            "documentos": [
                {"id": 1, "nome": "Protocolo_CBMERJ.pdf", "data": "2026-03-20"}
            ]
        }
    ]

# Compatibilidade de chaves nos subprocessos antigos
for sub in st.session_state.subprocessos:
    if "processo_principal_id" not in sub and "processo_mae_id" in sub:
        sub["processo_principal_id"] = sub["processo_mae_id"]

# 6. Financeiro
if "financeiro" not in st.session_state or not st.session_state.financeiro:
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
    
    nombres_clientes = [c["nome_razao"] for c in st.session_state.clientes]
    cliente_sel_nome = st.selectbox("Selecione ou Pesquise o Nome do Cliente:", [""] + nombres_clientes)
    
    if cliente_sel_nome != "":
        cliente_obj = next((c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome), None)
        
        if cliente_obj:
            st.markdown(f"### Ficha 360°: {cliente_obj['nome_razao']}")
            
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.write(f"**Tipo:** {cliente_obj['tipo_pessoa']}")
                st.write(f"**CPF/CNPJ:** {cliente_obj['cpf_cnpj']}")
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
            
            procs_p_cli = [p for p in st.session_state.processos_principais if p["cliente_id"] == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais e Subprocessos por Endereço ({len(procs_p_cli)})")
            
            for pmc in procs_p_cli:
                st.info(f"**Endereço:** {pmc['endereco_empreendimento']}\n\n**Processo Principal:** {pmc['numero_processo_principal']} | **Status:** `{pmc['status']}`")
                subs_cli = [s for s in st.session_state.subprocessos if s.get("processo_principal_id", s.get("processo_mae_id")) == pmc["id"]]
                for sc in subs_cli:
                    st.write(f" └─ **Subprocesso ({sc['orgao_subprocesso']}):** {sc['numero_subprocesso']} — Status: `{sc['status']}`")

            st.divider()

            financeiro_cliente = [f for f in st.session_state.financeiro if f["cliente_id"] == cliente_obj["id"]]
            st.markdown(f"##### 💰 Histórico Financeiro ({len(financeiro_cliente)})")
            
            if financeiro_cliente:
                df_fin_cli = pd.DataFrame(financeiro_cliente)
                st.dataframe(
                    df_fin_cli[["tipo_documento", "numero_documento", "descricao", "valor", "vencimento", "pagador", "status_pagamento"]],
                    use_container_width=True
                )

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
                    st.success("Cliente cadastrado e salvo na nuvem com sucesso!")
                    st.rerun()

    with tab_cli2:
        if st.session_state.clientes:
            st.markdown("##### Alterar Dados e Incluir Novos Endereços de Obra/Empreendimento")
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

                    btn_salvar_edicao = st.form_submit_button("Atualizar Cadastro e Endereços na Nuvem")

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
                        st.success("Cadastro do cliente e endereços atualizados com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum cliente cadastrado no momento.")

    with tab_cli3:
        if st.session_state.clientes:
            cli_excluir = st.selectbox("Selecione o Cliente para Excluir:", [c["nome_razao"] for c in st.session_state.clientes], key="sel_cli_del")
            if st.button(f"🚨 Excluir Cliente '{cli_excluir}'", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c["nome_razao"] != cli_excluir]
                salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                st.success("Cliente removido da nuvem!")
                st.rerun()
        else:
            st.info("Nenhum cliente cadastrado no momento.")

    st.divider()
    st.markdown("##### Base Geral de Clientes")
    df_cli_view = pd.DataFrame(st.session_state.clientes)
    if not df_cli_view.empty:
        st.dataframe(df_cli_view[["id", "tipo_pessoa", "nome_razao", "cpf_cnpj", "numero_proposta", "numero_contrato"]], use_container_width=True)

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
    c2.metric("Processos Principais (SMDU/LICIN)", len(df_p))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    
    total_pendente_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
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
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else []
    lista_equipe_nomes = list(st.session_state.equipe.keys())

    with tab_p1:
        if lista_clientes_nomes:
            with st.form("form_processo_principal"):
                st.markdown("##### Identificação do Cliente e Endereço do Empreendimento")
                c_pm1, c_pm2 = st.columns(2)
                
                with c_pm1:
                    cliente_sel_nome = st.selectbox("Cliente Cadastrado *", lista_clientes_nomes)
                    cliente_obj = next(c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome)
                    
                    end_opcoes = cliente_obj.get("enderecos_empreendimentos", []) + ["+ Adicionar Novo Endereço para este Cliente"]
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
                    if num_proc_p.strip() != "":
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
                        st.success("Processo Principal cadastrado e salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("Informe o Número do Processo Principal.")
        else:
            st.warning("Cadastre um cliente primeiro no módulo 'Cadastro de Clientes'.")

    with tab_p2:
        if st.session_state.processos_principais:
            procs_lista = [f"{p['numero_processo_principal']} — {p['cliente_nome']}" for p in st.session_state.processos_principais]
            proc_p_edit_sel = st.selectbox("Selecione o Processo Principal para Editar:", procs_lista, key="sel_p_edit_tab")
            idx_p_e = procs_lista.index(proc_p_edit_sel)
            obj_p_e = st.session_state.processos_principais[idx_p_e]

            with st.form("form_edit_proc_p"):
                c_pe1, c_pe2 = st.columns(2)
                with c_pe1:
                    edit_p_num = st.text_input("Nº Processo Principal", value=obj_p_e['numero_processo_principal'])
                    edit_p_serv = st.text_input("Serviço Contratado", value=obj_p_e['servico_contratado'])
                    edit_p_end = st.text_input("Endereço do Empreendimento", value=obj_p_e['endereco_empreendimento'])
                with c_pe2:
                    idx_r_p = lista_equipe_nomes.index(obj_p_e['responsavel_principal']) if obj_p_e['responsavel_principal'] in lista_equipe_nomes else 0
                    edit_p_resp = st.selectbox("Responsável Principal", lista_equipe_nomes, index=idx_r_p)
                    
                    idx_st_p = STATUS_OPCOES.index(obj_p_e['status']) if obj_p_e['status'] in STATUS_OPCOES else 0
                    edit_p_st = st.selectbox("Status do Processo", STATUS_OPCOES, index=idx_st_p)
                    edit_p_prazo = st.date_input("Prazo Limite / Validade", value=obj_p_e.get('prazo_limite', None))

                btn_salvar_edit_p = st.form_submit_button("Atualizar Processo Principal na Nuvem")
                if btn_salvar_edit_p:
                    obj_p_e['numero_processo_principal'] = edit_p_num
                    obj_p_e['servico_contratado'] = edit_p_serv
                    obj_p_e['endereco_empreendimento'] = edit_p_end
                    obj_p_e['responsavel_principal'] = edit_p_resp
