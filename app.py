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
    nombres_clientes = {c["id"]: c["nome_razao"] for c in clientes} if clientes else {}
    cliente_sel_id = st.selectbox("Selecione o Cliente:", [""] + list(nombres_clientes.keys()), format_func=lambda x: nombres_clientes.get(x, "Selecione..."))
    if cliente_sel_id != "":
        cliente_obj = get_cliente_por_id(cliente_sel_id)
        if cliente_obj:
            st.markdown(f"### Ficha 360°: {cliente_obj['nome_razao']}")
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.write(f"**Tipo:** {cliente_obj.get('tipo_pessoa', 'N/A')}")
                st.write(f"**CPF/CNPJ:** {cliente_obj.get('cpf_cnpj', 'N/A')}")
            with c_info2:
                st.write(f"**Proposta:** {cliente_obj.get('numero_proposta') or 'N/A'}")
                st.write(f"**Contrato:** {cliente_obj.get('numero_contrato') or 'N/A'}")
            with c_info3:
                st.write(f"**Endereço Comercial:** {cliente_obj.get('endereco_cliente') or 'N/A'}")

            st.divider()
            procs = [p for p in get_processos_principais() if p.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais ({len(procs)})")
            if procs:
                for pmc in procs:
                    st.info(f"**Processo:** {pmc.get('numero_processo_principal')} | **Endereço:** {pmc.get('endereco_empreendimento')} | **Status:** `{pmc.get('status')}`")
            else:
                st.info("Nenhum processo cadastrado para este cliente.")

elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes")
    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar", "✏️ Editar", "🗑️ Excluir"])
    with tab1:
        with st.form("form_novo_cliente"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tipo_p = st.selectbox("Tipo *", ["Pessoa Jurídica", "Pessoa Física"])
                nome_raz = st.text_input("Razão Social / Nome *")
                cpf_cnpj = st.text_input("CPF / CNPJ *")
            with col_c2:
                num_prop = st.text_input("Nº Proposta")
                end_cli = st.text_input("Endereço Comercial")
                end_emp_inicial = st.text_input("Endereço da Obra *")

            if st.form_submit_button("Salvar Cliente"):
                if nome_raz.strip():
                    ends_json = json.dumps([end_emp_inicial] if end_emp_inicial else [])
                    run_query("""INSERT INTO clientes (tipo_pessoa, nome_razao, cpf_cnpj, endereco_cliente, enderecos_empreendimentos, numero_proposta, data_inicio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (tipo_p, nome_raz, cpf_cnpj, end_cli, ends_json, num_prop, str(date.today())), fetchall=False)
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    with tab2:
        clis = get_clientes()
        if clis:
            map_cli = {c["id"]: c["nome_razao"] for c in clis}
            cli_edit_id = st.selectbox("Selecione o Cliente:", list(map_cli.keys()), format_func=lambda x: map_cli[x])
            cli_edit_obj = get_cliente_por_id(cli_edit_id)
            if cli_edit_obj:
                with st.form("form_editar_cliente"):
                    edit_nome = st.text_input("Nome", value=cli_edit_obj.get("nome_razao", ""))
                    edit_cpf = st.text_input("CPF/CNPJ", value=cli_edit_obj.get("cpf_cnpj", ""))
                    if st.form_submit_button("Atualizar"):
                        run_query("UPDATE clientes SET nome_razao=?, cpf_cnpj=? WHERE id=?", (edit_nome, edit_cpf, cli_edit_id), fetchall=False)
                        st.success("Atualizado!")
                        st.rerun()

    with tab3:
        clis = get_clientes()
        if clis:
            map_cli_del = {c["id"]: c["nome_razao"] for c in clis}
            cli_del_id = st.selectbox("Cliente a Excluir:", list(map_cli_del.keys()), format_func=lambda x: map_cli_del[x])
            if st.button("Excluir Cliente", type="primary"):
                run_query("DELETE FROM clientes WHERE id=?", (cli_del_id,), fetchall=False)
                st.success("Excluído!")
                st.rerun()

    st.divider()
    st.dataframe(run_df("SELECT id, tipo_pessoa, nome_razao, cpf_cnpj FROM clientes"), use_container_width=True)

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
        st.markdown("##### Processos por Status")
        if not df_p.empty and "status" in df_p.columns:
            st.bar_chart(df_p["status"].value_counts())
        else:
            st.info("Nenhum processo cadastrado para exibir o gráfico.")
    with col_g2:
        st.markdown("##### Subprocessos por Órgão")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            st.bar_chart(df_sub["orgao_subprocesso"].value_counts())
        else:
            st.info("Nenhum subprocesso cadastrado para exibir o gráfico.")

elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro e Edição de Processos Principais")
    tab_p1, tab_p2 = st.tabs(["➕ Cadastrar Novo Processo", "✏️ Editar Processo Existente"])
    clis = get_clientes()
    dict_cli = {c["id"]: c["nome_razao"] for c in clis} if clis else {}
    lista_eq = list(get_equipe().keys())

    with tab_p1:
        if dict_cli:
            cli_id_p = st.selectbox("Cliente *", list(dict_cli.keys()), format_func=lambda x: dict_cli[x])
            cli_obj_p = get_cliente_por_id(cli_id_p)
            ends = cli_obj_p.get("enderecos_empreendimentos", []) if cli_obj_p else []
            opcoes_ends = (ends if isinstance(ends, list) else [ends]) + ["+ Novo Endereço"]
            
            with st.form("form_p_novo"):
                end_p = st.selectbox("Endereço da Obra *", opcoes_ends)
                num_p = st.text_input("Nº Processo *")
                serv_p = st.text_input("Serviço *")
                resp_p = st.selectbox("Responsável *", lista_eq if lista_eq else ["Anna"])
                st_p = st.selectbox("Status Inicial", STATUS_OPCOES, index=2)
                
                if st.form_submit_button("Cadastrar e Salvar Processo"):
                    if num_p.strip():
                        run_query("""INSERT INTO processos_principais (cliente_id, numero_processo_principal, endereco_empreendimento, servico_contratado, responsavel_principal, status, data_inicio)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", (cli_id_p, num_p, end_p, serv_p, resp_p, st_p, str(date.today())), fetchall=False)
                        st.success("Processo cadastrado com sucesso!")
                        st.rerun()
        else:
            st.info("Cadastre um cliente antes de criar um processo.")

    with tab_p2:
        procs = get_processos_principais()
        if procs:
            dict_procs = {p["id"]: f"{p['numero_processo_principal']} ({p['endereco_empreendimento']})" for p in procs}
            p_edit_id = st.selectbox("Selecione o Processo:", list(dict_procs.keys()), format_func=lambda x: dict_procs[x])
            obj_p = get_processo_por_id(p_edit_id)
            if obj_p:
                with st.form("form_p_edit"):
                    edit_num = st.text_input("Nº Processo", value=obj_p.get("numero_processo_principal", ""))
                    edit_serv = st.text_input("Serviço", value=obj_p.get("servico_contratado", ""))
                    if st.form_submit_button("Atualizar Processo"):
                        run_query("UPDATE processos_principais SET numero_processo_principal=?, servico_contratado=? WHERE id=?", (edit_num, edit_serv, p_edit_id), fetchall=False)
                        st.success("Atualizado com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum Processo Principal cadastrado ainda para edição.")

elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    equipe_map = get_equipe()
    if equipe_map:
        user_sel = st.selectbox("Selecionar Integrante:", list(equipe_map.keys()))
        procs = [p for p in get_processos_principais() if p.get("responsavel_principal") == user_sel]
        subs = [s for s in get_subprocessos() if s.get("responsavel_sub") == user_sel]
        
        st.markdown(f"##### Processos Principais ({len(procs)})")
        if procs:
            for p in procs:
                st.info(f"**Nº Processo:** {p.get('numero_processo_principal')} | **Status:** {p.get('status')}")
        else:
            st.write("Nenhum processo principal atribuído a este integrante.")
            
        st.markdown(f"##### Subprocessos / Exigências ({len(subs)})")
        if subs:
            for s in subs:
                st.warning(f"**Órgão:** {s.get('orgao_subprocesso')} | **Exigência:** {s.get('descricao_exigencia')}")
        else:
            st.write("Nenhum subprocesso atribuído a este integrante.")

elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("##### Integrantes Cadastrados")
        for n, c in list(get_equipe().items()):
            st.write(f"👤 **{n}** — *{c}*")
    with col2:
        st.markdown("##### Adicionar Integrante")
        with st.form("form_eq"):
            nf = st.text_input("Nome *")
            cf = st.text_input("Cargo *")
            if st.form_submit_button("Adicionar Funcionário"):
                if nf.strip():
                    run_query("INSERT INTO equipe (nome, cargo) VALUES (?, ?)", (nf.strip(), cf.strip()), fetchall=False)
                    st.success("Integrante adicionado!")
                    st.rerun()

elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro de Órgãos")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("##### Órgãos Mapeados")
        for org in get_orgaos():
            st.write(f"🏛️ **{org}**")
    with col2:
        st.markdown("##### Adicionar Órgão")
        with st.form("form_org"):
            novo_o = st.text_input("Nome do Órgão *")
            if st.form_submit_button("Cadastrar"):
                if novo_o.strip():
                    run_query("INSERT INTO orgaos (nome) VALUES (?)", (novo_o.strip(),), fetchall=False)
                    st.success("Órgão adicionado!")
                    st.rerun()

elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Restrições")
    tab_s1, tab_s2 = st.tabs(["➕ Cadastrar Subprocesso", "📋 Listar Subprocessos"])
    procs = get_processos_principais()
    
    with tab_s1:
        if procs:
            dict_p_sub = {p["id"]: f"{p['numero_processo_principal']} ({p['endereco_empreendimento']})" for p in procs}
            with st.form("form_sub_novo"):
                pid_sub = st.selectbox("Processo Principal *", list(dict_p_sub.keys()), format_func=lambda x: dict_p_sub[x])
                orgao_s = st.selectbox("Órgão *", get_orgaos())
                num_s = st.text_input("Nº Subprocesso")
                desc_s = st.text_area("Exigência *")
                resp_s = st.selectbox("Responsável *", list(get_equipe().keys()))
                if st.form_submit_button("Salvar Subprocesso"):
                    run_query("""INSERT INTO subprocessos (processo_principal_id, orgao_subprocesso, numero_subprocesso, descricao_exigencia, responsavel_sub, status, data_inicio)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (pid_sub, orgao_s, num_s, desc_s, resp_s, "Em Tramitação", str(date.today())), fetchall=False)
                    st.success("Cadastrado com sucesso!")
                    st.rerun()
        else:
            st.info("É necessário ter ao menos um Processo Principal cadastrado.")

    with tab_s2:
        subs = get_subprocessos()
        if subs:
            st.dataframe(pd.DataFrame(subs), use_container_width=True)
        else:
            st.info("Nenhum subprocesso cadastrado.")

elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro")
    tab_f1, tab_f2 = st.tabs(["📋 Extrato Financeiro", "➕ Novo Lançamento"])
    
    with tab_f1:
        fin = get_financeiro()
        if fin:
            st.dataframe(pd.DataFrame(fin), use_container_width=True)
        else:
            st.info("Nenhum lançamento financeiro registrado.")
            
    with tab_f2:
        clis = get_clientes()
        if clis:
            dict_cli_f = {c["id"]: c["nome_razao"] for c in clis}
            with st.form("form_fin_novo"):
                cli_f_id = st.selectbox("Cliente *", list(dict_cli_f.keys()), format_func=lambda x: dict_cli_f[x])
                tipo_f = st.selectbox("Tipo *", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
                num_f = st.text_input("Nº Documento / Boleto")
                desc_f =
