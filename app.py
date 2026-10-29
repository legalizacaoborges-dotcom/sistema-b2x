import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Configuração de Layout Sobrio e Empresarial
st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual & Financeira",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada - Identidade Visual B2x Arquitetura
st.markdown("""
    <style>
    .stApp {
        background-color: #F4F6F8;
    }
    section[data-testid="stSidebar"] {
        background-color: #022B3A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    h1, h2, h3 {
        color: #022B3A;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 500;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 4px;
        border-top: 4px solid #E1C3A1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    div.stButton > button {
        background-color: #022B3A !important;
        color: #E1C3A1 !important;
        border: 1px solid #E1C3A1 !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
    }
    div.stButton > button:hover {
        background-color: #E1C3A1 !important;
        color: #022B3A !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# INICIALIZAÇÃO DAS BASES DE DADOS NA SESSÃO (PERSISTÊNCIA TEMPORÁRIA)
# ------------------------------------------------------------------------------

# 1. Equipe de Funcionários / Responsáveis
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

# 2. Lista de Órgãos
if "lista_orgaos" not in st.session_state:
    st.session_state.lista_orgaos = [
        "Prefeitura (SEI.RIO / Licenciamento)",
        "Cartório do 9º RGI (Averbação/Registro)",
        "Licenciamento Ambiental (SMAC / INEA)",
        "Saneamento e Drenagem (RioÁguas)",
        "Geotecnia e Encostas (GEO-RIO)",
        "Corpo de Bombeiros (CBMERJ)",
        "Secretaria de Fazenda (ISS / ITBI)",
        "Financeiro Interno / Proposta (Mariana)"
    ]

# 3. Base de Clientes
if "clientes" not in st.session_state:
    st.session_state.clientes = [
        {
            "id": 1,
            "tipo_pessoa": "Pessoa Jurídica",
            "nome_razao": "Barra Park Empreendimentos LTDA",
            "cpf_cnpj": "12.345.678/0001-90",
            "representante_legal": "Carlos Eduardo Silva",
            "endereco_cliente": "Av. das Américas, 5000 - Barra da Tijuca, Rio de Janeiro - RJ",
            "endereco_empreendimento": "Rua Projetada A, Lote 12 - Recreio, Rio de Janeiro - RJ",
            "numero_proposta": "PROP-2026/042",
            "numero_contrato": "CTR-2026/018",
            "data_inicio": date(2026, 3, 15)
        }
    ]

# 4. Base de Processos
if "processos" not in st.session_state:
    st.session_state.processos = [
        {
            "id": 1,
            "cliente_id": 1,
            "numero_processo": "04/001.234/2026",
            "cliente_empreendimento": "Barra Park Empreendimentos LTDA",
            "orgao": "Prefeitura (SEI.RIO / Licenciamento)",
            "tipo_servico": "Concessão de Habite-se",
            "designado_por": "Gabriela",
            "responsavel_atual": "Anna",
            "status": "4. Em Exigência / Aguardando Documentos",
            "prazo_limite": date(2026, 11, 20),
            "documentos": [
                {"id": 101, "nome": "Nota_de_Exigencia_01.pdf", "tipo": "Exigência", "data": "2026-10-10"}
            ]
        }
    ]

# 5. Base Financeira
if "financeiro" not in st.session_state:
    st.session_state.financeiro = [
        {
            "id": 1,
            "processo_id": 1,
            "cliente_id": 1,
            "tipo_documento": "RRT (CAU)",
            "numero_documento": "RRT nº 10928374-2026",
            "descricao": "RRT de Execução de Obra e Licenciamento",
            "valor": 115.50,
            "vencimento": date(2026, 11, 10),
            "pagador": "B2x (A Reembolsar)",
            "status_pagamento": "Pendente",
            "nota_fiscal_emitida": "Sim",
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
        "Painel de Processos", 
        "Cadastro de Clientes",
        "Busca Integrada (Lupa 360°)",
        "Módulo Financeiro (Mariana)", 
        "Entrada Rápida", 
        "Gestão de Órgãos",
        "Gestão da Equipe",
        "Fila Individual", 
        "Relatórios"
    ]
)

st.title("B2x Arquitetura | Sistema de Gestão Processual")

# ------------------------------------------------------------------------------
# 1. DASHBOARD EXECUTIVO
# ------------------------------------------------------------------------------
if menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento")
    
    df_proc = pd.DataFrame(st.session_state.processos)
    df_fin = pd.DataFrame(st.session_state.financeiro)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(st.session_state.clientes))
    c2.metric("Processos em Tramitação", len(df_proc))
    c3.metric("Pendentes de Exigência", len(df_proc[df_proc["status"].str.contains("Exigência")]) if not df_proc.empty else 0)
    
    total_pendente_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente_fin:,.2f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Distribuição de Processos por Status")
        if not df_proc.empty:
            status_counts = df_proc["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))

    with col_g2:
        st.markdown("##### Alocação por Integrante da Equipe")
        if not df_proc.empty:
            resp_counts = df_proc["responsavel_atual"].value_counts().reset_index()
            resp_counts.columns = ["Responsável", "Processos"]
            st.bar_chart(resp_counts.set_index("Responsável"))

# ------------------------------------------------------------------------------
# 2. CADASTRO COMPLETO DE CLIENTES (INCLUIR & EXCLUIR)
# ------------------------------------------------------------------------------
elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes (PF / PJ)")
    
    tab_cli1, tab_cli2 = st.tabs(["➕ Cadastrar Novo Cliente", "🗑️ Gerenciar / Excluir Cliente"])
    
    with tab_cli1:
        with st.form("form_novo_cliente"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tipo_p = st.selectbox("Tipo de Pessoa *", ["Pessoa Jurídica", "Pessoa Física"])
                nome_raz = st.text_input("Nome Completo ou Razão Social *")
                cpf_cnpj = st.text_input("CPF ou CNPJ *")
                rep_legal = st.text_input("Nome do Representante Legal (para PJ)")
                data_inc = st.date_input("Data de Início do Contrato", value=date.today())

            with col_c2:
                num_prop = st.text_input("Número da Proposta Comercial", placeholder="Ex: PROP-2026/001")
                num_cont = st.text_input("Número do Contrato", placeholder="Ex: CTR-2026/001")
                end_cli = st.text_input("Endereço do Cliente (Residencial/Comercial)")
                end_emp = st.text_input("Endereço do Empreendimento / Obra")

            btn_salvar_cli = st.form_submit_button("Salvar Cadastro de Cliente")
            
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
                        "endereco_empreendimento": end_emp,
                        "numero_proposta": num_prop,
                        "numero_contrato": num_cont,
                        "data_inicio": data_inc
                    })
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha o Nome / Razão Social do cliente.")

    with tab_cli2:
        st.markdown("##### Exclusão de Cadastro de Cliente")
        if st.session_state.clientes:
            cli_excluir = st.selectbox("Selecione o Cliente que Deseja Excluir:", [c["nome_razao"] for c in st.session_state.clientes])
            if st.button(f"🚨 Excluir Cliente '{cli_excluir}'", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c["nome_razao"] != cli_excluir]
                st.success("Cliente removido do sistema com sucesso!")
                st.rerun()
        else:
            st.info("Nenhum cliente cadastrado.")

    st.divider()
    st.markdown("##### Clientes Cadastrados no Sistema")
    df_cli_view = pd.DataFrame(st.session_state.clientes)
    if not df_cli_view.empty:
        st.dataframe(df_cli_view[["id", "tipo_pessoa", "nome_razao", "cpf_cnpj", "numero_proposta", "numero_contrato"]], use_container_width=True)

# ------------------------------------------------------------------------------
# 3. BUSCA INTEGRADA (LUPA 360°)
# ------------------------------------------------------------------------------
elif menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente")
    
    nombres_clientes = [c["nome_razao"] for c in st.session_state.clientes]
    cliente_sel_nome = st.selectbox("Selecione ou Pesquise o Nome do Cliente:", [""] + nombres_clientes)
    
    if cliente_sel_nome != "":
        cliente_obj = next((c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome), None)
        
        if cliente_obj:
            st.markdown(f"### Ficha Geral: {cliente_obj['nome_razao']}")
            
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.write(f"**Tipo:** {cliente_obj['tipo_pessoa']}")
                st.write(f"**CPF/CNPJ:** {cliente_obj['cpf_cnpj']}")
                st.write(f"**Representante Legal:** {cliente_obj['representante_legal'] or 'N/A'}")
            with c_info2:
                st.write(f"**Nº Proposta Comercial:** {cliente_obj['numero_proposta']}")
                st.write(f"**Nº Contrato:** {cliente_obj['numero_contrato']}")
                st.write(f"**Data de Início:** {cliente_obj['data_inicio'].strftime('%d/%m/%Y') if cliente_obj['data_inicio'] else 'N/A'}")
            with c_info3:
                st.write(f"**Endereço Cliente:** {cliente_obj['endereco_cliente']}")
                st.write(f"**Endereço Obra:** {cliente_obj['endereco_empreendimento']}")

            st.divider()
            
            processos_cliente = [p for p in st.session_state.processos if p["cliente_empreendimento"] == cliente_obj["nome_razao"]]
            st.markdown(f"##### 📌 Processos em Tramitação ({len(processos_cliente)})")
            
            if processos_cliente:
                for pc in processos_cliente:
                    st.info(f"**Nº Processo:** {pc['numero_processo']} | **Órgão:** {pc['orgao']} | **Serviço:** {pc['tipo_servico']} | **Status:** `{pc['status']}`")
            else:
                st.write("Nenhum processo vinculado a este cliente.")

            st.divider()

            financeiro_cliente = [f for f in st.session_state.financeiro if f["cliente_id"] == cliente_obj["id"]]
            st.markdown(f"##### 💰 Histórico Financeiro, Taxas e Encargos ({len(financeiro_cliente)})")
            
            if financeiro_cliente:
                df_fin_cli = pd.DataFrame(financeiro_cliente)
                st.dataframe(
                    df_fin_cli[["tipo_documento", "numero_documento", "descricao", "valor", "vencimento", "pagador", "status_pagamento", "nota_fiscal_emitida"]],
                    use_container_width=True
                )
            else:
                st.write("Nenhum registro financeiro encontrado para este cliente.")

# ------------------------------------------------------------------------------
# 4. MÓDULO FINANCEIRO (INCLUIR, EXCLUIR E QUITAR TAXAS)
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, RRT/ART e Boletos")
    
    tab_fin1, tab_fin2 = st.columns([2, 1])
    
    with tab_fin2:
        st.markdown("##### Novo Lançamento Financeiro")
        with st.form("form_novo_financeiro"):
            cli_fin = st.selectbox("Cliente / Empreendimento", [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum"])
            proc_fin = st.selectbox("Processo Relacionado", [p["numero_processo"] for p in st.session_state.processos] if st.session_state.processos else ["Nenhum"])
            tipo_doc = st.selectbox("Tipo de Encargo", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
            num_doc = st.text_input("Número do Boleto / RRT / ART / DARM")
            desc_fin = st.text_input("Descrição da Taxa / Documento")
            val_fin = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
            venc_fin = st.date_input("Data de Vencimento")
            pagador_fin = st.selectbox("Responsável pelo Pagamento", ["B2x (A Reembolsar)", "Cliente Direto"])
            nf_emitida = st.selectbox("Nota Fiscal Emitida?", ["Sim", "Não", "Não Aplicável"])
            
            uploaded_file = st.file_uploader("Anexar Comprovante ou Guia (PDF/Imagem)", type=["pdf", "png", "jpg"])
            
            btn_add_fin = st.form_submit_button("Lançar no Financeiro")
            if btn_add_fin:
                cli_id_sel = next((c["id"] for c in st.session_state.clientes if c["nome_razao"] == cli_fin), 1)
                proc_id_sel = next((p["id"] for p in st.session_state.processos if p["numero_processo"] == proc_fin), 1)
                
                novo_id_fin = max([f["id"] for f in st.session_state.financeiro], default=0) + 1
                st.session_state.financeiro.append({
                    "id": novo_id_fin,
                    "processo_id": proc_id_sel,
                    "cliente_id": cli_id_sel,
                    "tipo_documento": tipo_doc,
                    "numero_documento": num_doc,
                    "descricao": desc_fin,
                    "valor": val_fin,
                    "vencimento": venc_fin,
                    "pagador": pagador_fin,
                    "status_pagamento": "Pendente",
                    "nota_fiscal_emitida": nf_emitida,
                    "comprovante_anexado": uploaded_file.name if uploaded_file else None
                })
                st.success("Lançamento financeiro registrado com sucesso!")
                st.rerun()

    with tab_fin1:
        st.markdown("##### Painel de Controle de Contas e Taxas")
        if st.session_state.financeiro:
            for item in list(st.session_state.financeiro):
                with st.expander(f"💰 {item['tipo_documento']} — R$ {item['valor']:,.2f} | Vencimento: {item['vencimento'].strftime('%d/%m/%Y')} ({item['status_pagamento']})"):
                    col_mf1, col_mf2 = st.columns(2)
                    with col_mf1:
                        st.write(f"**Nº Documento:** {item['numero_documento']}")
                        st.write(f"**Descrição:** {item['descricao']}")
                        st.write(f"**Pagador:** {item['pagador']}")
                    with col_mf2:
                        st.write(f"**Status Pagamento:** {item['status_pagamento']}")
                        st.write(f"**Nota Fiscal:** {item['nota_fiscal_emitida']}")
                        if item['comprovante_anexado']:
                            st.write(f"**Comprovante:** `{item['comprovante_anexado']}`")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("Marcar como Pago", key=f"btn_pago_{item['id']}"):
                            item['status_pagamento'] = "Pago / Quitado"
                            st.success("Status atualizado para Pago!")
                            st.rerun()
                    with c_btn2:
                        if st.button("🗑️ Excluir Lançamento", key=f"btn_del_fin_{item['id']}"):
                            st.session_state.financeiro = [f for f in st.session_state.financeiro if f['id'] != item['id']]
                            st.success("Lançamento financeiro excluído!")
                            st.rerun()
        else:
            st.info("Nenhum encargo financeiro registrado.")

# ------------------------------------------------------------------------------
# 5. PAINEL DE PROCESSOS (EDITAR, ANEXAR & EXCLUIR ARQUIVOS/PROCESSOS)
# ------------------------------------------------------------------------------
elif menu == "Painel de Processos":
    st.subheader("Listagem e Gestão de Processos")
    
    if st.session_state.processos:
        for proc in list(st.session_state.processos):
            with st.expander(f"PROCESSO: {proc['numero_processo']} | {proc['cliente_empreendimento']} — Responsável: {proc['responsavel_atual']}"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write(f"**Cliente / Empreendimento:** {proc['cliente_empreendimento']}")
                    st.write(f"**Nº Processo:** {proc['numero_processo']}")
                    st.write(f"**Órgão Principal:** {proc['orgao']}")
                with col_b:
                    st.write(f"**Serviço:** {proc['tipo_servico']}")
                    st.write(f"**Entrada por:** {proc['designado_por']}")
                    st.write(f"**Prazo Limite:** {proc['prazo_limite'].strftime('%d/%m/%Y') if proc['prazo_limite'] else 'Não informado'}")
                with col_c:
                    lista_resp = list(st.session_state.equipe.keys())
                    idx_resp = lista_resp.index(proc['responsavel_atual']) if proc['responsavel_atual'] in lista_resp else 0
                    
                    novo_st = st.selectbox("Atualizar Status", STATUS_OPCOES, index=STATUS_OPCOES.index(proc['status']), key=f"st_{proc['id']}")
                    novo_resp = st.selectbox("Reatribuir Responsável", lista_resp, index=idx_resp, key=f"resp_{proc['id']}")
                    
                    if st.button("Salvar Alterações", key=f"btn_salvar_{proc['id']}"):
                        proc['status'] = novo_st
                        proc['responsavel_atual'] = novo_resp
                        st.success("Processo atualizado!")
                        st.rerun()

                st.markdown("---")
                st.markdown("###### Documentos Anexados ao Processo")
                
                if proc.get("documentos"):
                    for doc in list(proc["documentos"]):
                        col_doc1, col_doc2 = st.columns([4, 1])
                        with col_doc1:
                            st.write(f"📄 **{doc['nome']}** ({doc['tipo']}) - Data: {doc['data']}")
                        with col_doc2:
                            if st.button("🗑️ Excluir File", key=f"del_doc_{proc['id']}_{doc['id']}"):
                                proc["documentos"] = [d for d in proc["documentos"] if d["id"] != doc["id"]]
                                st.success("Documento removido!")
                                st.rerun()
                else:
                    st.write("Nenhum documento anexado ainda.")
                    
                uploaded_doc = st.file_uploader("Anexar Licença / Despacho / Relatório (PDF)", type=["pdf", "png", "jpg"], key=f"up_{proc['id']}")
                if uploaded_doc:
                    if st.button("Salvar Documento no Processo", key=f"btn_doc_{proc['id']}"):
                        if "documentos" not in proc:
                            proc["documentos"] = []
                        novo_id_doc = max([d["id"] for d in proc["documentos"]], default=0) + 1
                        proc["documentos"].append({
                            "id": novo_id_doc,
                            "nome": uploaded_doc.name,
                            "tipo": "Documento Oficial / Parecer",
                            "data": date.today().strftime("%Y-%m-%d")
                        })
                        st.success("Documento anexado com sucesso!")
                        st.rerun()

                st.markdown("---")
                if st.button(f"🚨 Excluir Processo {proc['numero_processo']}", key=f"del_proc_{proc['id']}", type="primary"):
                    st.session_state.processos = [p for p in st.session_state.processos if p["id"] != proc["id"]]
                    st.success("Processo excluído do sistema!")
                    st.rerun()
    else:
        st.info("Nenhum processo cadastrado no momento.")

# ------------------------------------------------------------------------------
# 6. ENTRADA RÁPIDA DE PROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Entrada Rápida":
    st.subheader("Cadastro Inicial de Cliente e Processo")
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum Cliente Cadastrado"]
    lista_equipe_nomes = list(st.session_state.equipe.keys())
    
    with st.form("form_entrada_expresso"):
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            cliente_sel = st.selectbox("Cliente Cadastrado", lista_clientes_nomes)
            num_proc = st.text_input("Nº do Processo / Prenotação RGI", placeholder="Ex: 04/100.200/2026")
            orgao_p = st.selectbox("Órgão Principal", st.session_state.lista_orgaos)
        with c_e2:
            servico = st.text_input("Serviço Contratado", placeholder="Ex: Licença de Obra / Averbação")
            designado = st.selectbox("Atribuir Responsável Inicial", lista_equipe_nomes)
            prazo_p = st.date_input("Prazo Limite para Conclusão", value=None)

        btn_cadastrar = st.form_submit_button("Cadastrar e Notificar Responsável")
        if btn_cadastrar:
            novo_id = max([p["id"] for p in st.session_state.processos], default=0) + 1
            st.session_state.processos.append({
                "id": novo_id,
                "cliente_id": 1,
                "numero_processo": num_proc if num_proc else "Em Tramitação Inicial",
                "cliente_empreendimento": cliente_sel,
                "orgao": orgao_p,
                "tipo_servico": servico,
                "designado_por": "Gabriela",
                "responsavel_atual": designado,
                "status": "3. Em Tramitação no Órgão",
                "prazo_limite": prazo_p,
                "documentos": []
            })
            st.success(f"Processo cadastrado e atribuído a {designado}.")
            st.rerun()

# ------------------------------------------------------------------------------
# 7. GESTÃO DE ÓRGÃOS (INCLUIR & EXCLUIR)
# ------------------------------------------------------------------------------
elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro e Mapeamento de Órgãos Públicos")
    col_o1, col_o2 = st.columns([2, 1])
    
    with col_o1:
        st.markdown("##### Órgãos e Cartórios Cadastrados")
        for org in list(st.session_state.lista_orgaos):
            c_org1, c_org2 = st.columns([4, 1])
            with c_org1:
                st.write(f"🏛️ **{org}**")
            with c_org2:
                if st.button("Excluir", key=f"del_org_{org}"):
                    st.session_state.lista_orgaos.remove(org)
                    st.success("Órgão removido!")
                    st.rerun()

    with col_o2:
        st.markdown("##### Adicionar Novo Órgão")
        with st.form("form_novo_orgao"):
            novo_orgao_nome = st.text_input("Nome do Órgão")
            if st.form_submit_button("Cadastrar Órgão"):
                if novo_orgao_nome.strip() != "":
                    st.session_state.lista_orgaos.append(novo_orgao_nome.strip())
                    st.success("Órgão cadastrado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 8. GESTÃO DA EQUIPE (INCLUIR, EDITAR & EXCLUIR FUNCIONÁRIOS)
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários e Responsáveis")
    
    col_eq1, col_eq2 = st.columns([2, 1])
    
    with col_eq1:
        st.markdown("##### Integrantes Atuais da B2x Arquitetura")
        for nome_f, cargo_f in list(st.session_state.equipe.items()):
            with st.expander(f"👤 {nome_f} — {cargo_f}"):
                novo_cargo = st.text_input(f"Editar Função de {nome_f}:", value=cargo_f, key=f"edit_cargo_{nome_f}")
                
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    if st.button(f"Atualizar Cargo", key=f"btn_save_f_{nome_f}"):
                        st.session_state.equipe[nome_f] = novo_cargo
                        st.success("Função atualizada com sucesso!")
                        st.rerun()
                with col_f2:
                    if st.button(f"🗑️ Remover {nome_f}", key=f"btn_del_f_{nome_f}"):
                        del st.session_state.equipe[nome_f]
                        st.success(f"{nome_f} foi removido(a) da equipe!")
                        st.rerun()

    with col_eq2:
        st.markdown("##### Cadastrar Novo Funcionário")
        with st.form("form_novo_funcionario"):
            nome_novo_f = st.text_input("Nome do Funcionário *")
            cargo_novo_f = st.text_input("Função / Atribuição principal *")
            
            if st.form_submit_button("Cadastrar na Equipe"):
                if nome_novo_f.strip() != "":
                    st.session_state.equipe[nome_novo_f.strip()] = cargo_novo_f.strip()
                    st.success(f"{nome_novo_f} adicionado(a) à equipe com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o nome do funcionário.")

# ------------------------------------------------------------------------------
# 9. FILA INDIVIDUAL
# ------------------------------------------------------------------------------
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    lista_equipe_nomes = list(st.session_state.equipe.keys())
    usuario_ativo = st.selectbox("Selecionar Integrante:", lista_equipe_nomes if lista_equipe_nomes else ["Nenhum"])
    
    meus_processos = [p for p in st.session_state.processos if p["responsavel_atual"] == usuario_ativo]
    if meus_processos:
        for mp in meus_processos:
            st.info(f"**Empreendimento:** {mp['cliente_empreendimento']} | **Nº:** {mp['numero_processo']} | **Status:** {mp['status']}")
    else:
        st.write("Nenhum processo alocado a este integrante no momento.")

# ------------------------------------------------------------------------------
# 10. RELATÓRIOS
# ------------------------------------------------------------------------------
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    df_completo = pd.DataFrame(st.session_state.processos)
    if not df_completo.empty:
        st.dataframe(df_completo[["numero_processo", "cliente_empreendimento", "orgao", "tipo_servico", "responsavel_atual", "status", "prazo_limite"]], use_container_width=True)
        csv_data = df_completo.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar Tabela (CSV)", data=csv_data, file_name="relatorio_b2x_arquitetura.csv", mime="text/csv")
    else:
        st.info("Nenhum processo cadastrado para emissão de relatório.")