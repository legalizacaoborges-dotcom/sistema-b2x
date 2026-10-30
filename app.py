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

# Estilização CSS
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
    
    # Tabela Clientes
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
    
    # Tabela Processos Principais
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
    
    # Tabela Subprocessos
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
    
    # Tabela Equipe
    c.execute("""
        CREATE TABLE IF NOT EXISTS equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cargo TEXT
        )
    """)
    
    # Tabela Órgãos
    c.execute("""
        CREATE TABLE IF NOT EXISTS orgaos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )
    """)
    
    # Tabela Financeiro
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
    
    # Carga de dados iniciais padrão se estiver vazio
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
# FUNÇÕES DE LEITURA E ESCRITA NO BANCO SQLITE
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

# Helper para ler clientes
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
# 1. BUSCA INTEGRADA (LUPA 360°)
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

            if st.form_submit_button("Salvar Cliente"):
                if nome_raz.strip() != "":
                    ends_json = json.dumps([end_emp_inicial] if end_emp_inicial else [])
                    run_query("""
                        INSERT INTO clientes (tipo_pessoa, nome_razao, cpf_cnpj, representante_legal, endereco_cliente, enderecos_empreendimentos, numero_proposta, numero_contrato, data_inicio)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (tipo_p, nome_raz, cpf_cnpj, rep_legal, end_cli, ends_json, num_prop, num_cont, str(date.today())), fetchall=False)
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    with tab_cli2:
        clis = get_clientes()
        if clis:
            map_cli = {c["id"]: c["nome_razao"] for c in clis}
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
                    st.markdown("###### 🏢 Endereços de Empreendimentos Cadastrados:")
                    ends = cli_edit_obj.get("enderecos_empreendimentos", [])
                    if isinstance(ends, list):
                        for idx_end, end_atual in enumerate(ends):
                            st.write(f"• **Endereço {idx_end + 1}:** {end_atual}")
                    else:
                        st.write(f"• **Endereço 1:** {ends}")

                    novo_end_incluir = st.text_input("➕ Adicionar Novo Endereço de Empreendimento / Obra:")

                    if st.form_submit_button("Atualizar Cadastro e Endereços"):
                        lista_ends = ends if isinstance(ends, list) else [ends]
                        if novo_end_incluir.strip():
                            lista_ends.append(novo_end_incluir.strip())

                        run_query("""
                            UPDATE clientes SET nome_razao=?, cpf_cnpj=?, representante_legal=?, numero_proposta=?, numero_contrato=?, endereco_cliente=?, enderecos_empreendimentos=?
                            WHERE id=?
                        """, (edit_nome_raz, edit_cpf_cnpj, edit_rep_legal, edit_num_prop, edit_num_cont, edit_end_cli, json.dumps(lista_ends), cli_edit_id), fetchall=False)
                        st.success("Cadastro atualizado com sucesso!")
                        st.rerun()

    with tab_cli3:
        clis = get_clientes()
        if clis:
            map_cli_del = {c["id"]: c["nome_razao"] for c in clis}
            cli_excluir_id = st.selectbox("Selecione o Cliente para Excluir:", list(map_cli_del.keys()), format_func=lambda x: map_cli_del[x])
            if st.button("🚨 Excluir Cliente Selecionado", type="primary"):
                run_query("DELETE FROM clientes WHERE id=?", (cli_excluir_id,), fetchall=False)
                st.success("Cliente removido com sucesso!")
                st.rerun()

    st.divider()
    st.markdown("##### Base Geral de Clientes")
    df_cli_view = run_df("SELECT id, tipo_pessoa, nome_razao, cpf_cnpj, numero_proposta, numero_contrato FROM clientes")
    st.dataframe(df_cli_view, use_container_width=True)

# ------------------------------------------------------------------------------
# 3. DASHBOARD EXECUTIVO
# ------------------------------------------------------------------------------
elif menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento")
    df_p = run_df("SELECT * FROM processos_principais")
    df_sub = run_df("SELECT * FROM subprocessos")
    df_fin = run_df("SELECT * FROM financeiro")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(get_clientes()))
    c2.metric("Processos Principais", len(df_p))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    
    total_pendente = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente:,.2f}")

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos Principais por Status")
        if not df_p.empty and "status" in df_p.columns:
            st.bar_chart(df_p["status"].value_counts())

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            st.bar_chart(df_sub["orgao_subprocesso"].value_counts())

# ------------------------------------------------------------------------------
# 4. ENTRADA PROCESSO PRINCIPAL
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro e Edição de Processos Principais")
    tab_p1, tab_p2 = st.tabs(["➕ Cadastrar Novo Processo", "✏️ Editar Processo Existente"])
    
    clis = get_clientes()
    dict_clientes = {c["id"]: c["nome_razao"] for c in clis} if clis else {}
    equipe_dict = get_equipe()
    lista_equipe_nomes = list(equipe_dict.keys()) if equipe_dict else ["Anna"]

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
                    num_proc_p = st.text_input("Nº do Processo Principal *", placeholder="Ex: 04/001.234/2026")
                    servico_p = st.text_input("Serviço Contratado *", placeholder="Ex: Licença de Obra / Habite-se")

                st.markdown("##### Atribuição e Prazos")
                c_pm3, c_pm4 = st.columns(2)
                with c_pm3:
                    resp_p = st.selectbox("Responsável pelo Processo Principal *", lista_equipe_nomes)
                    data_inc_p = st.date_input("Data de Início do Processo", value=date.today())
                with c_pm4:
                    prazo_p = st.date_input("Prazo Limite / Validade da Licença", value=None)
                    status_p_init = st.selectbox("Status Inicial", STATUS_OPCOES, index=2)

                if st.form_submit_button("Cadastrar e Salvar Processo"):
                    if num_proc_p.strip() != "":
                        if end_sel == "+ Adicionar Novo Endereço para este Cliente":
                            end_final = novo_end_input.strip() if novo_end_input.strip() != "" else "Endereço Não Informado"
                            lista_atual = enderecos_disponiveis
                            lista_atual.append(end_final)
                            run_query("UPDATE clientes SET enderecos_empreendimentos=? WHERE id=?", (json.dumps(lista_atual), cli_selecionado_id), fetchall=False)
                        else:
                            end_final = end_sel
                        
                        run_query("""
                            INSERT INTO processos_principais (cliente_id, numero_processo_principal, endereco_empreendimento, servico_contratado, responsavel_principal, status, data_inicio, prazo_limite)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (cli_selecionado_id, num_proc_p, end_final, servico_p, resp_p, status_p_init, str(data_inc_p), str(prazo_p) if prazo_p else None), fetchall=False)
                        
                        st.success("Processo Principal cadastrado com sucesso!")
                        st.rerun()

    with tab_p2:
        procs = get_processos_principais()
        if procs:
            dict_procs = {p["id"]: f"{p['numero_processo_principal']} — {get_cliente_por_id(p['cliente_id'])['nome_razao'] if get_cliente_por_id(p['cliente_id']) else 'Cliente'}" for p in procs}
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

                    if st.form_submit_button("Atualizar Processo Principal"):
                        run_query("""
                            UPDATE processos_principais SET numero_processo_principal=?, servico_contratado=?, endereco_empreendimento=?, responsavel_principal=?, status=?
                            WHERE id=?
                        """, (edit_p_num, edit_p_serv, edit_p_end, edit_p_resp, edit_p_st, proc_p_edit_id), fetchall=False)
                        st.success("Processo Principal atualizado!")
                        st.rerun()

# ------------------------------------------------------------------------------
# 5. FILA INDIVIDUAL
# ------------------------------------------------------------------------------
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    equipe_dict = get_equipe()
    user_sel = st.selectbox("Selecionar Integrante:", list(equipe_dict.keys()))
    
    subs_meus = [s for s in get_subprocessos() if s.get("responsavel_sub") == user_sel]
    principais_meus = [p for p in get_processos_principais() if p.get("responsavel_principal") == user_sel]
    
    st.markdown(f"##### Processos Principais sob Responsabilidade de {user_sel} ({len(principais_meus)})")
    if principais_meus:
        for pm in principais_meus:
            cli_p = get_cliente_por_id(pm['cliente_id'])
            st.info(f"**Nº Processo:** {pm.get('numero_processo_principal')} | **Cliente:** {cli_p['nome_razao'] if cli_p else 'N/A'} | **Endereço:** {pm.get('endereco_empreendimento')} | **Status:** {pm.get('status')}")

    st.markdown(f"##### Subprocessos / Exigências sob Responsabilidade de {user_sel} ({len(subs_meus)})")
    if subs_meus:
        for sm in subs_meus:
            st.warning(f"**Órgão:** {sm.get('orgao_subprocesso')} | **Nº:** {sm.get('numero_subprocesso')} | **Exigência:** {sm.get('descricao_exigencia')} | **Status:** {sm.get('status')}")

# ------------------------------------------------------------------------------
# 6. GESTÃO DA EQUIPE
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col_eq1, col_eq2 = st.columns([2, 1])
    with col_eq1:
        st.markdown("##### Integrantes Atuais")
        for nome_f, cargo_f in list(get_equipe().items()):
            c_f1, c_f2 = st.columns([4, 1])
            with c_f1:
                st.write(f"👤 **{nome_f}** — *{cargo_f}*")
            with c_f2:
                if st.button("Excluir", key=f"del_eq_{nome_f}"):
                    run_query("DELETE FROM equipe WHERE nome=?", (nome_f,), fetchall=False)
                    st.rerun()

    with col_eq2:
        st.markdown("##### Cadastrar Novo Integrante")
        with st.form("form_novo_f"):
            nf = st.text_input("Nome *")
            cf = st.text_input("Função / Cargo *")
            if st.form_submit_button("Cadastrar Funcionário"):
                if nf.strip():
                    run_query("INSERT INTO equipe (nome, cargo) VALUES (?, ?)", (nf.strip(), cf.strip()), fetchall=False)
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
        for org in get_orgaos():
            c_org1, c_org2 = st.columns([4, 1])
            with c_org1:
                st.write(f"🏛️ **{org}**")
            with c_org2:
                if st.button("Excluir", key=f"del_org_{org}"):
                    run_query("DELETE FROM orgaos WHERE nome=?", (org,), fetchall=False)
                    st.rerun()

    with col_o2:
        st.markdown("##### Cadastrar Novo Órgão")
        with st.form("form_novo_orgao"):
            novo_o = st.text_input("Nome do Órgão / Autarquia *")
            if st.form_submit_button("Cadastrar Órgão"):
                if novo_o.strip():
                    run_query("INSERT INTO orgaos (nome) VALUES (?)", (novo_o.strip(),), fetchall=False)
                    st.success("Órgão adicionado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 8. GESTÃO DE SUBPROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Atendimento a Restrições do Processo Principal")
    tab_sub1, tab_sub2 = st.tabs(["➕ Cadastrar Novo Subprocesso", "📋 Gerenciar Subprocessos Existentes"])
    
    procs = get_processos_principais()
    orgaos_lista = get_orgaos()
    equipe_list = list(get_equipe().keys())

    with tab_sub1:
        if procs:
            dict_p_sub = {p["id"]: f"{p['numero_processo_principal']} — {get_cliente_por_id(p['cliente_id'])['nome_razao'] if get_cliente_por_id(p['cliente_id']) else 'Cliente'} ({p['endereco_empreendimento']})" for p in procs}
            
            with st.form("form_novo_subprocesso"):
                proc_p_id_sel = st.selectbox("Selecione o Processo Principal *", list(dict_p_sub.keys()), format_func=lambda x: dict_p_sub[x])
                c_sub1, c_sub2 = st.columns(2)
                with c_sub1:
                    orgao_sub = st.selectbox("Órgão do Subprocesso *", orgaos_lista)
                    num_sub = st.text_input("Nº do Subprocesso", placeholder="Ex: CBMERJ-10293")
                    desc_exigencia = st.text_area("Descrição da Exigência *")

                with c_sub2:
                    info_relevante_input = st.text_area("Ponto de Atenção")
                    resp_sub = st.selectbox("Responsável pelo Subprocesso *", equipe_list)
                    data_in_sub = st.date_input("Data de Início", value=date.today())
                    prazo_fim_sub = st.date_input("Prazo Limite", value=None)

                if st.form_submit_button("Cadastrar Subprocesso"):
                    run_query("""
                        INSERT INTO subprocessos (processo_principal_id, orgao_subprocesso, numero_subprocesso, descricao_exigencia, informacao_relevante, responsavel_sub, status, data_inicio, prazo_fim)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (proc_p_id_sel, orgao_sub, num_sub if num_sub else "Aguardando Número", desc_exigencia, info_relevante_input, resp_sub, "Em Tramitação", str(data_in_sub), str(prazo_fim_sub) if prazo_fim_sub else None), fetchall=False)
                    st.success("Subprocesso cadastrado com sucesso!")
                    st.rerun()

    with tab_sub2:
        if procs:
            subs_todos = get_subprocessos()
            for pm in procs:
                cli_mae = get_cliente_por_id(pm['cliente_id'])
                st.markdown(f"#### 🏢 Processo Principal: `{pm.get('numero_processo_principal')}` — {cli_mae['nome_razao'] if cli_mae else 'Cliente'}")
                st.write(f"**Endereço:** {pm.get('endereco_empreendimento')} | **Responsável:** {pm.get('responsavel_principal')}")
                
                subs_do_p = [s for s in subs_todos if s.get("processo_principal_id") == pm["id"]]
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
                                run_query("UPDATE subprocessos SET status=? WHERE id=?", (novo_st_sub, sub["id"]), fetchall=False)
                                st.success("Status atualizado!")
                                st.rerun()

                            if st.button(f"🚨 Excluir Subprocesso", key=f"del_sub_{sub['id']}", type="primary"):
                                run_query("DELETE FROM subprocessos WHERE id=?", (sub["id"],), fetchall=False)
                                st.success("Subprocesso removido!")
                                st.rerun()
                else:
                    st.write("Nenhum subprocesso vinculado.")
                st.divider()

# ------------------------------------------------------------------------------
# 9. MÓDULO FINANCEIRO (MARIANA)
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, RRT/ART e Boletos")
    tab_fin1, tab_fin2 = st.columns([2, 1])
    
    clis = get_clientes()
    procs = get_processos_principais()

    with tab_fin2:
        st.markdown("##### Novo Lançamento Financeiro")
        dict_clientes_fin = {c["id"]: c["nome_razao"] for c in clis} if clis else {}
        
        if dict_clientes_fin:
            cli_fin_id = st.selectbox("Cliente", list(dict_clientes_fin.keys()), format_func=lambda x: dict_clientes_fin[x], key="select_cli_fin")
            procs_p_opcoes = {p["id"]: f"{p['numero_processo_principal']} ({p['endereco_empreendimento']})" for p in procs if p.get("cliente_id") == cli_fin_id}
            
            with st.form("form_novo_financeiro"):
                proc_p_fin_id = st.selectbox("Processo Principal Relacionado", list(procs_p_opcoes.keys()), format_func=lambda x: procs_p_opcoes[x]) if procs_p_opcoes else None
                tipo_doc = st.selectbox("Tipo de Encargo", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
                num_doc = st.text_input("Número do Boleto / RRT / DARM")
                desc_fin = st.text_input("Descrição da Taxa")
                val_fin = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
                venc_fin = st.date_input("Data de Vencimento")
                pagador_fin = st.selectbox("Responsável pelo Pagamento", ["B2x (A Reembolsar)", "Cliente Direto"])
                
                if st.form_submit_button("Lançar no Financeiro"):
                    run_query("""
                        INSERT INTO financeiro (processo_principal_id, cliente_id, tipo_documento, numero_documento, descricao, valor, vencimento, pagador, status_pagamento, nota_fiscal_emitida)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (proc_p_fin_id, cli_fin_id, tipo_doc, num_doc, desc_fin, val_fin, str(venc_fin), pagador_fin, "Pendente", "Não"), fetchall=False)
                    st.success("Lançamento registrado com sucesso!")
                    st.rerun()

    with tab_fin1:
        st.markdown("##### Painel de Controle de Contas e Taxas")
        fin = get_financeiro()
        if fin:
            for item in fin:
                cli_f = get_cliente_por_id(item.get("cliente_id"))
                with st.expander(f"💰 {item.get('tipo_documento')} — R$ {float(item.get('valor', 0)):,.2f} | Cliente: {cli_f['nome_razao'] if cli_f else 'N/A'} ({item.get('status_pagamento')})"):
                    st.write(f"**Nº Documento:** {item.get('numero_documento')} | **Pagador:** {item.get('pagador')}")
                    st.write(f"**Descrição:** {item.get('descricao')}")
                    st.write(f"**Vencimento:** {item.get('vencimento')}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("Marcar como Pago", key=f"btn_pago_{item['id']}"):
                            run_query("UPDATE financeiro SET status_pagamento='Pago / Quitado' WHERE id=?", (item['id'],), fetchall=False)
                            st.success("Status atualizado!")
                            st.rerun()
                    with c_btn2:
                        if st.button("🗑️ Excluir", key=f"btn_del_fin_{item['id']}"):
                            run_query("DELETE FROM financeiro WHERE id=?", (item['id'],), fetchall=False)
                            st.success("Lançamento excluído!")
                            st.rerun()

# ------------------------------------------------------------------------------
# 10. PAINEL GERAL DE PROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Painel Geral de Processos":
    st.subheader("Visão Geral de Processos Principais e Seus Subprocessos por Endereço")
    procs = get_processos_principais()
    subs_todos = get_subprocessos()
    
    if procs:
        for pm in procs:
            cli_m = get_cliente_por_id(pm['cliente_id'])
            with st.expander(f"PROCESSO PRINCIPAL: {pm.get('numero_processo_principal')} | {cli_m['nome_razao'] if cli_m else 'Cliente'} — Resp: {pm.get('responsavel_principal')}"):
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    st.write(f"**Endereço do Empreendimento:** {pm.get('endereco_empreendimento')}")
                    st.write(f"**Serviço Contratado:** {pm.get('servico_contratado')}")
                with c_p2:
                    st.write(f"**Status Principal:** `{pm.get('status')}`")

                subs = [s for s in subs_todos if s.get("processo_principal_id") == pm["id"]]
                st.markdown(f"###### Subprocessos / Restrições Vinculadas ({len(subs)})")
                if subs:
                    for sb in subs:
                        st.info(f"**Órgão:** {sb.get('orgao_subprocesso')} | **Nº:** {sb.get('numero_subprocesso')} | **Resp:** {sb.get('responsavel_sub')} | **Status:** `{sb.get('status')}`")

                if st.button(f"🚨 Excluir Processo Principal e Subprocessos", key=f"del_pm_{pm['id']}", type="primary"):
                    run_query("DELETE FROM processos_principais WHERE id=?", (pm["id"],), fetchall=False)
                    run_query("DELETE FROM subprocessos WHERE processo_principal_id=?", (pm["id"],), fetchall=False)
                    st.success("Removidos com sucesso!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 11. RELATÓRIOS
# ------------------------------------------------------------------------------
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    procs = get_processos_principais()
    if procs:
        dados_relatorio = []
        for p in procs:
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
