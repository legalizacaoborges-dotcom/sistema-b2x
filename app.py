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
        else:
            st.info("Nenhum processo principal cadastrado no momento para gerar o gráfico.")

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            st.bar_chart(df_sub["orgao_subprocesso"].value_counts())
        else:
            st.info("Nenhum subprocesso cadastrado no momento para gerar o gráfico.")

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
                with st.form("form_edit_proc_p
