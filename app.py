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
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_pessoa TEXT,
            nome_razao TEXT,
            cpf_cnpj TEXT,
            representante_legal TEXT,
            endereco_cliente TEXT,
            enderecos_empreendimentos TEXT,
            numero_proposta TEXT,
            numero_contrato TEXT,
            emite_nf TEXT,
            valor_global REAL,
            forma_pagamento TEXT,
            status_quitacao TEXT,
            data_pagamento_sinal TEXT,
            data_pagamento_entrada TEXT,
            pdf_proposta_nome TEXT,
            pdf_recibo_nome TEXT,
            data_inicio TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS processos_principais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            numero_processo_principal TEXT,
            endereco_empreendimento TEXT,
            servico_contratado TEXT,
            responsavel_principal TEXT,
            status TEXT,
            numero_licenca TEXT,
            numero_despacho TEXT,
            vencimento_licenca TEXT,
            data_inicio TEXT,
            prazo_limite TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS subprocessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processo_principal_id INTEGER,
            orgao_subprocesso TEXT,
            numero_subprocesso TEXT,
            descricao_exigencia TEXT,
            informacao_relevante TEXT,
            responsavel_sub TEXT,
            status TEXT,
            numero_despacho TEXT,
            data_inicio TEXT,
            prazo_fim TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS equipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cargo TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS orgaos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS financeiro (
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
            anexo_boleto_nome TEXT,
            anexo_comprovante_nome TEXT
        )""")
        
        colunas_novas = [
            ("financeiro", "anexo_boleto_nome", "TEXT"),
            ("financeiro", "anexo_comprovante_nome", "TEXT"),
            ("processos_principais", "numero_licenca", "TEXT"),
            ("processos_principais", "numero_despacho", "TEXT"),
            ("processos_principais", "vencimento_licenca", "TEXT"),
            ("subprocessos", "numero_despacho", "TEXT")
        ]
        for tabela, coluna, tipo in colunas_novas:
            try:
                c.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
            except Exception:
                pass

        c.execute("SELECT COUNT(*) FROM clientes")
        if c.fetchone()[0] == 0:
            c.execute("""INSERT INTO clientes (id, tipo_pessoa, nome_razao, cpf_cnpj, representante_legal, endereco_cliente, enderecos_empreendimentos, numero_proposta, numero_contrato, emite_nf, valor_global, forma_pagamento, status_quitacao, data_inicio)
            VALUES (1, 'Pessoa Jurídica', 'CALADO EVENTOS E ADMINISTRAÇÃO LTDA', '12.345.678/0001-90', 'Carlos Calado', 'Av. das Américas, 3500 - Barra da Tijuca, Rio de Janeiro - RJ', '["Unidade Barra: Av. das Américas, 3500 - Bloco 2"]', 'PROP-2026/012', 'CTR-2026/005', 'Sim', 15000.0, 'Parcelado', 'Pendente', '2026-01-15')""")
        
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
    except Exception as e:
        st.error(f"Erro ao inicializar base de dados: {e}")

init_db()

def run_query(query, params=(), fetchall=True):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(query, params)
        data = c.fetchall() if fetchall else None
        conn.commit()
        conn.close()
        return data
    except Exception as e:
        st.error(f"Erro na consulta SQL: {e}")
        return [] if fetchall else None

def run_df(query, params=()):
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def get_clientes():
    df = run_df("SELECT * FROM clientes")
    if df.empty:
        return []
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
    df = run_df("SELECT * FROM processos_principais")
    return df.to_dict(orient="records") if not df.empty else []

def get_processo_por_id(pid):
    procs = get_processos_principais()
    return next((p for p in procs if p["id"] == pid), None)

def get_subprocessos():
    df = run_df("SELECT * FROM subprocessos")
    return df.to_dict(orient="records") if not df.empty else []

def get_equipe():
    df = run_df("SELECT * FROM equipe")
    if df.empty:
        return {}
    return {r["nome"]: r["cargo"] for _, r in df.iterrows()}

def get_orgaos_df():
    return run_df("SELECT * FROM orgaos")

def get_orgaos():
    df = get_orgaos_df()
    return df["nome"].tolist() if not df.empty and "nome" in df.columns else []

def get_financeiro():
    df = run_df("SELECT * FROM financeiro")
    return df.to_dict(orient="records") if not df.empty else []

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

# ------------------------------------------------------------------------------
# 1. BUSCA INTEGRADA 360°
# ------------------------------------------------------------------------------
if menu == "Busca Integrada (Lupa 360°)":
    st.subheader("🔍 Consulta Consolidada por Cliente (Resumo Completo 360°)")
    clientes = get_clientes()
    nombres_clientes = {c["id"]: c["nome_razao"] for c in clientes} if clientes else {}
    cliente_sel_id = st.selectbox("Selecione o Cliente:", [""] + list(nombres_clientes.keys()), format_func=lambda x: nombres_clientes.get(x, "Selecione..."))
    
    if cliente_sel_id != "":
        cliente_obj = get_cliente_por_id(cliente_sel_id)
        if cliente_obj:
            st.markdown(f"### Ficha 360°: {cliente_obj['nome_razao']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write(f"**Tipo:** {cliente_obj.get('tipo_pessoa', 'N/A')}")
                st.write(f"**CPF/CNPJ:** {cliente_obj.get('cpf_cnpj', 'N/A')}")
                st.write(f"**Representante Legal:** {cliente_obj.get('representante_legal') or 'N/A'}")
                st.write(f"**Emissão de NF:** `{cliente_obj.get('emite_nf', 'Não Informado')}`")
            with c2:
                st.write(f"**Proposta:** {cliente_obj.get('numero_proposta') or 'N/A'}")
                st.write(f"**Contrato:** {cliente_obj.get('numero_contrato') or 'N/A'}")
                st.write(f"**Valor Global:** R$ {float(cliente_obj.get('valor_global') or 0):,.2f}")
                st.write(f"**Forma Pagamento:** {cliente_obj.get('forma_pagamento') or 'N/A'} ({cliente_obj.get('status_quitacao') or 'Pendente'})")
            with c3:
                st.write(f"**Endereço Comercial:** {cliente_obj.get('endereco_cliente') or 'N/A'}")
                st.write(f"**Data Sinal:** {cliente_obj.get('data_pagamento_sinal') or 'N/A'} | **Data Entrada:** {cliente_obj.get('data_pagamento_entrada') or 'N/A'}")
                st.write(f"**Doc. Proposta:** {cliente_obj.get('pdf_proposta_nome') or 'Nenhum anexo'}")

            st.divider()
            st.markdown("##### 🏢 Endereços de Empreendimentos Cadastrados")
            ends = cliente_obj.get("enderecos_empreendimentos", [])
            for e in (ends if isinstance(ends, list) else [ends]):
                st.write(f"• {e}")

            st.divider()
            procs = [p for p in get_processos_principais() if p.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Principais ({len(procs)})")
            if procs:
                subs_todos = get_subprocessos()
                for pmc in procs:
                    st.info(f"**Processo:** {pmc.get('numero_processo_principal')} | **Endereço:** {pmc.get('endereco_empreendimento')}\n\n"
                            f"**Serviço:** {pmc.get('servico_contratado')} | **Status:** `{pmc.get('status')}` | **Nº Licença:** {pmc.get('numero_licenca') or 'N/A'} | **Despacho:** {pmc.get('numero_despacho') or 'N/A'} | **Venc. Licença:** {pmc.get('vencimento_licenca') or 'N/A'}")
                    subs_cli = [s for s in subs_todos if s.get("processo_principal_id") == pmc["id"]]
                    for sc in subs_cli:
                        st.write(f" └─ **Subprocesso ({sc.get('orgao_subprocesso')}):** {sc.get('numero_subprocesso')} — Status: `{sc.get('status')}` | Despacho: {sc.get('numero_despacho') or 'N/A'} | Prazo Exigência: {sc.get('prazo_fim') or 'N/A'}")
            else:
                st.info("Nenhum processo cadastrado para este cliente.")

            st.divider()
            fin = [f for f in get_financeiro() if f.get("cliente_id") == cliente_obj["id"]]
            st.markdown(f"##### 💰 Lançamentos Financeiros & Boletos ({len(fin)})")
            if fin:
                df_fin_c = pd.DataFrame(fin)
                colunas_desejadas = ["tipo_documento", "numero_documento", "descricao", "valor", "vencimento", "pagador", "status_pagamento", "anexo_boleto_nome", "anexo_comprovante_nome"]
                cols_f = [c for c in colunas_desejadas if c in df_fin_c.columns]
                st.dataframe(df_fin_c[cols_f], use_container_width=True)
            else:
                st.info("Nenhum lançamento financeiro para este cliente.")

# ------------------------------------------------------------------------------
# 2. CADASTRO DE CLIENTES
# ------------------------------------------------------------------------------
elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes & Múltiplos Endereços")
    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar Novo Cliente", "✏️ Editar Cadastro & Adicionar Endereços", "🗑️ Excluir Cliente"])
    
    with tab1:
        with st.form("form_novo_cliente"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tipo_p = st.selectbox("Tipo de Pessoa *", ["Pessoa Jurídica", "Pessoa Física"])
                nome_raz = st.text_input("Razão Social / Nome Completo *")
                cpf_cnpj = st.text_input("CPF ou CNPJ *")
                rep_legal = st.text_input("Representante Legal (para PJ)")
                end_cli = st.text_input("Endereço Comercial / Sede")
                end_emp_inicial = st.text_input("1º Endereço de Empreendimento / Obra *")

            with col_c2:
                num_prop = st.text_input("Número da Proposta Comercial")
                num_cont = st.text_input("Número do Contrato")
                emite_nf = st.selectbox("Precisa Emitir Nota Fiscal? *", ["Sim", "Não"])
                val_global = st.number_input("Valor Global da Proposta (R$)", min_value=0.0, step=100.0)
                forma_pag = st.selectbox("Forma de Pagamento", ["À Vista", "Parcelado"])
                status_quit = st.selectbox("Status Financeiro do Contrato", ["Pendente", "Sinal Pago", "Parcialmente Pago", "Quitado"])
                dt_sinal = st.date_input("Data de Pagamento do Sinal", value=None)
                dt_entrada = st.date_input("Data de Pagamento da Entrada", value=None)
                pdf_prop = st.file_uploader("Anexar Proposta Assinada (PDF)", type=["pdf"])
                pdf_recibo = st.file_uploader("Anexar Recibos / Notas Fiscais (PDF)", type=["pdf"])

            if st.form_submit_button("Salvar Cliente Completo"):
                if nome_raz.strip():
                    ends_json = json.dumps([end_emp_inicial] if end_emp_inicial else [])
                    run_query("""INSERT INTO clientes (tipo_pessoa, nome_razao, cpf_cnpj, representante_legal, endereco_cliente, enderecos_empreendimentos, numero_proposta, numero_contrato, emite_nf, valor_global, forma_pagamento, status_quitacao, data_pagamento_sinal, data_pagamento_entrada, pdf_proposta_nome, pdf_recibo_nome, data_inicio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                    (tipo_p, nome_raz, cpf_cnpj, rep_legal, end_cli, ends_json, num_prop, num_cont, emite_nf, val_global, forma_pag, status_quit, str(dt_sinal) if dt_sinal else None, str(dt_entrada) if dt_entrada else None, pdf_prop.name if pdf_prop else None, pdf_recibo.name if pdf_recibo else None, str(date.today())), fetchall=False)
                    st.success("Cliente cadastrado com sucesso!")
                    st.rerun()

    with tab2:
        clis = get_clientes()
        if clis:
            map_cli = {c["id"]: f"{c['nome_razao']} ({c['cpf_cnpj']})" for c in clis}
            cli_edit_id = st.selectbox("Selecione o Cliente para Editar:", list(map_cli.keys()), format_func=lambda x: map_cli[x])
            cli_edit_obj = get_cliente_por_id(cli_edit_id)

            if cli_edit_obj:
                with st.form("form_editar_cliente"):
                    c_e1, c_e2 = st.columns(2)
                    with c_e1:
                        edit_nome = st.text_input("Razão Social / Nome", value=cli_edit_obj.get("nome_razao", ""))
                        edit_cpf = st.text_input("CPF / CNPJ", value=cli_edit_obj.get("cpf_cnpj", ""))
                        edit_rep = st.text_input("Representante Legal", value=cli_edit_obj.get("representante_legal", ""))
                        edit_end_c = st.text_input("Endereço Comercial", value=cli_edit_obj.get("endereco_cliente", ""))
                        edit_emite_nf = st.selectbox("Precisa Emitir NF?", ["Sim", "Não"], index=0 if cli_edit_obj.get("emite_nf") == "Sim" else 1)

                    with c_e2:
                        edit_prop = st.text_input("Proposta", value=cli_edit_obj.get("numero_proposta", ""))
                        edit_cont = st.text_input("Contrato", value=cli_edit_obj.get("numero_contrato", ""))
                        edit_val = st.number_input("Valor Global (R$)", value=float(cli_edit_obj.get("valor_global") or 0.0))
                        edit_forma = st.selectbox("Forma Pagamento", ["À Vista", "Parcelado"], index=0 if cli_edit_obj.get("forma_pagamento") == "À Vista" else 1)
                        edit_quit = st.selectbox("Status Quitação", ["Pendente", "Sinal Pago", "Parcialmente Pago", "Quitado"])

                    st.markdown("---")
                    st.markdown("###### 🏢 Endereços Cadastrados para este CNPJ/CPF:")
                    ends = cli_edit_obj.get("enderecos_empreendimentos", [])
                    lista_ends = ends if isinstance(ends, list) else [ends]
                    for idx_e, e_item in enumerate(lista_ends):
                        st.write(f"• **Endereço {idx_e+1}:** {e_item}")

                    novo_end = st.text_input("➕ Adicionar Novo Endereço de Empreendimento para o mesmo CNPJ:")

                    if st.form_submit_button("Salvar Alterações"):
                        if novo_end.strip():
                            lista_ends.append(novo_end.strip())
                        run_query("""UPDATE clientes SET nome_razao=?, cpf_cnpj=?, representante_legal=?, endereco_cliente=?, numero_proposta=?, numero_contrato=?, emite_nf=?, valor_global=?, forma_pagamento=?, status_quitacao=?, enderecos_empreendimentos=?
                        WHERE id=?""", (edit_nome, edit_cpf, edit_rep, edit_end_c, edit_prop, edit_cont, edit_emite_nf, edit_val, edit_forma, edit_quit, json.dumps(lista_ends), cli_edit_id), fetchall=False)
                        st.success("Cadastro e endereços atualizados com sucesso!")
                        st.rerun()

    with tab3:
        clis = get_clientes()
        if clis:
            map_cli_del = {c["id"]: c["nome_razao"] for c in clis}
            cli_del_id = st.selectbox("Cliente a Excluir:", list(map_cli_del.keys()), format_func=lambda x: map_cli_del[x])
            if st.button("Excluir Cliente", type="primary"):
                run_query("DELETE FROM clientes WHERE id=?", (cli_del_id,), fetchall=False)
                st.success("Cliente excluído!")
                st.rerun()

    st.divider()
    df_cli_base = run_df("SELECT * FROM clientes")
    cols_base = [c for c in ["id", "tipo_pessoa", "nome_razao", "cpf_cnpj", "emite_nf", "valor_global", "status_quitacao"] if c in df_cli_base.columns]
    st.dataframe(df_cli_base[cols_base], use_container_width=True)

# ------------------------------------------------------------------------------
# 3. DASHBOARD EXECUTIVO
# ------------------------------------------------------------------------------
elif menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento & Prazos")
    df_p = run_df("SELECT * FROM processos_principais")
    df_sub = run_df("SELECT * FROM subprocessos")
    df_fin = run_df("SELECT * FROM financeiro")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(get_clientes()))
    c2.metric("Processos Principais", len(df_p))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    total_pendente = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty and "status_pagamento" in df_fin.columns else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente:,.2f}")

    st.divider()
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown("##### ⏳ Prazos Próximos de Exigências (Subprocessos)")
        if not df_sub.empty and "prazo_fim" in df_sub.columns:
            subs_prazos = df_sub[df_sub["prazo_fim"].notnull() & (df_sub["prazo_fim"] != "None")][["numero_subprocesso", "orgao_subprocesso", "prazo_fim", "responsavel_sub"]]
            if not subs_prazos.empty:
                st.dataframe(subs_prazos, use_container_width=True)
            else:
                st.info("Nenhum prazo limite registrado nos subprocessos.")
        else:
            st.info("Sem dados de subprocessos.")

    with col_d2:
        st.markdown("##### 📅 Vencimentos de Licenças de Obras")
        if not df_p.empty and "vencimento_licenca" in df_p.columns:
            licencas_prazos = df_p[df_p["vencimento_licenca"].notnull() & (df_p["vencimento_licenca"] != "None")][["numero_processo_principal", "endereco_empreendimento", "numero_licenca", "vencimento_licenca"]]
            if not licencas_prazos.empty:
                st.dataframe(licencas_prazos, use_container_width=True)
            else:
                st.info("Nenhum vencimento de licença registrado.")
        else:
            st.info("Sem dados de processos principais.")

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos por Status")
        if not df_p.empty and "status" in df_p.columns:
            st.bar_chart(df_p["status"].value_counts())
    with col_g2:
        st.markdown("##### Subprocessos por Órgão")
        if not df_sub.empty and "orgao_subprocesso" in df_sub.columns:
            st.bar_chart(df_sub["orgao_subprocesso"].value_counts())

# ------------------------------------------------------------------------------
# 4. ENTRADA PROCESSO PRINCIPAL
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro e Edição de Processos Principais")
    tab_p1, tab_p2 = st.tabs(["➕ Cadastrar Novo Processo", "✏️ Editar Processo Existente"])
    clis = get_clientes()
    dict_cli = {c["id"]: f"{c['nome_razao']} ({c['cpf_cnpj']})" for c in clis} if clis else {}
    lista_eq = list(get_equipe().keys())

    with tab_p1:
        if dict_cli:
            cli_id_p = st.selectbox("Cliente *", list(dict_cli.keys()), format_func=lambda x: dict_cli[x])
            cli_obj_p = get_cliente_por_id(cli_id_p)
            ends = cli_obj_p.get("enderecos_empreendimentos", []) if cli_obj_p else []
            lista_ends_p = ends if isinstance(ends, list) else [ends]
            
            with st.form("form_p_novo"):
                st.info("Nota: O mesmo endereço pode ter múltiplos processos principais (Demolição, Remembramento, Licenciamento, etc.)")
                c_p1, c_p2 = st.columns(2)
                with c_p1:
                    end_p = st.selectbox("Endereço do Empreendimento *", lista_ends_p)
                    num_p = st.text_input("Nº Processo Principal *", placeholder="Ex: 04/001.234/2026")
                    serv_p = st.text_input("Serviço Contratado *", placeholder="Ex: Licenciamento de Obra / Demolição / Mais Valia")
                    resp_p = st.selectbox("Responsável *", lista_eq if lista_eq else ["Anna"])
                with c_p2:
                    st_p = st.selectbox("Status Inicial", STATUS_OPCOES, index=2)
                    num_lic = st.text_input("Número da Licença Emitida")
                    num_desp = st.text_input("Número do Despacho")
                    venc_lic = st.date_input("Data de Vencimento da Licença", value=None)

                if st.form_submit_button("Cadastrar e Salvar Processo"):
                    if num_p.strip():
                        run_query("""INSERT INTO processos_principais (cliente_id, numero_processo_principal, endereco_empreendimento, servico_contratado, responsavel_principal, status, numero_licenca, numero_despacho, vencimento_licenca, data_inicio)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (cli_id_p, num_p, end_p, serv_p, resp_p, st_p, num_lic, num_desp, str(venc_lic) if venc_lic else None, str(date.today())), fetchall=False)
                        st.success("Processo Principal cadastrado!")
                        st.rerun()
        else:
            st.info("Cadastre um cliente antes de criar um processo.")

    with tab_p2:
        procs = get_processos_principais()
        if procs:
            dict_procs = {p["id"]: f"{p['numero_processo_principal']} — {p['servico_contratado']} ({p['endereco_empreendimento']})" for p in procs}
            p_edit_id = st.selectbox("Selecione o Processo:", list(dict_procs.keys()), format_func=lambda x: dict_procs[x])
            obj_p = get_processo_por_id(p_edit_id)
            if obj_p:
                with st.form("form_p_edit"):
                    c_pe1, c_pe2 = st.columns(2)
                    with c_pe1:
                        edit_num = st.text_input("Nº Processo Principal", value=obj_p.get("numero_processo_principal", ""))
                        edit_serv = st.text_input("Serviço Contratado", value=obj_p.get("servico_contratado", ""))
                        edit_lic = st.text_input("Número da Licença", value=obj_p.get("numero_licenca", ""))
                    with c_pe2:
                        edit_desp = st.text_input("Número do Despacho", value=obj_p.get("numero_despacho", ""))
                        st_idx = STATUS_OPCOES.index(obj_p["status"]) if obj_p.get("status") in STATUS_OPCOES else 0
                        edit_st = st.selectbox("Status", STATUS_OPCOES, index=st_idx)

                    if st.form_submit_button("Atualizar Processo"):
                        run_query("UPDATE processos_principais SET numero_processo_principal=?, servico_contratado=?, numero_licenca=?, numero_despacho=?, status=? WHERE id=?", (edit_num, edit_serv, edit_lic, edit_desp, edit_st, p_edit_id), fetchall=False)
                        st.success("Atualizado com sucesso!")
                        st.rerun()

# ------------------------------------------------------------------------------
# 5. FILA INDIVIDUAL
# ------------------------------------------------------------------------------
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    equipe_map = get_equipe()
    if equipe_map:
        user_sel = st.selectbox("Selecionar Integrante:", list(equipe_map.keys()))
        procs = [p for p in get_processos_principais() if p.get("responsavel_principal") == user_sel]
        subs = [s for s in get_subprocessos() if s.get("responsavel_sub") == user_sel]
        
        st.markdown(f"##### Processos Principais sob Responsabilidade de {user_sel} ({len(procs)})")
        if procs:
            for p in procs:
                cli_p = get_cliente_por_id(p['cliente_id'])
                nome_c = cli_p['nome_razao'] if cli_p else 'N/A'
                st.info(f"**Cliente:** {nome_c} | **Nº Processo:** {p.get('numero_processo_principal')} | **Endereço:** {p.get('endereco_empreendimento')} | **Status:** {p.get('status')}")
        else:
            st.write("Nenhum processo principal atribuído a este integrante.")
            
        st.markdown(f"##### Subprocessos / Exigências sob Responsabilidade de {user_sel} ({len(subs)})")
        if subs:
            for s in subs:
                proc_mae = get_processo_por_id(s.get("processo_principal_id"))
                cli_mae = get_cliente_por_id(proc_mae["cliente_id"]) if proc_mae else None
                nome_cli_sub = cli_mae["nome_razao"] if cli_mae else "N/A"
                num_proc_mae = proc_mae["numero_processo_principal"] if proc_mae else "N/A"
                end_sub = proc_mae["endereco_empreendimento"] if proc_mae else "N/A"
                
                st.warning(f"**Cliente:** {nome_cli_sub} | **Processo Mae:** {num_proc_mae} | **Endereço:** {end_sub}\n\n"
                           f"**Órgão:** {s.get('orgao_subprocesso')} | **Nº Subprocesso:** {s.get('numero_subprocesso')} | **Exigência:** {s.get('descricao_exigencia')} | **Prazo:** {s.get('prazo_fim') or 'N/A'}")
        else:
            st.write("Nenhum subprocesso atribuído a este integrante.")

# ------------------------------------------------------------------------------
# 6. GESTÃO DA EQUIPE
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("##### Integrantes Cadastrados")
        for n, c in list(get_equipe().items()):
            c_f1, c_f2 = st.columns([4, 1])
            with c_f1:
                st.write(f"👤 **{n}** — *{c}*")
            with c_f2:
                if st.button("Excluir", key=f"del_eq_{n}"):
                    run_query("DELETE FROM equipe WHERE nome=?", (n,), fetchall=False)
                    st.rerun()
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

# ------------------------------------------------------------------------------
# 7. GESTÃO DE ÓRGÃOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro & Edição de Órgãos")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("##### Órgãos Mapeados")
        df_o = get_orgaos_df()
        for _, row in df_o.iterrows():
            c_o1, c_o2 = st.columns([4, 1])
            with c_o1:
                st.write(f"🏛️ **{row['nome']}**")
            with c_o2:
                if st.button("Excluir", key=f"del_o_{row['id']}"):
                    run_query("DELETE FROM orgaos WHERE id=?", (row['id'],), fetchall=False)
                    st.rerun()
    with col2:
        st.markdown("##### Adicionar / Editar Órgão")
        with st.form("form_org"):
            novo_o = st.text_input("Nome do Órgão *")
            if st.form_submit_button("Cadastrar"):
                if novo_o.strip():
                    run_query("INSERT INTO orgaos (nome) VALUES (?)", (novo_o.strip(),), fetchall=False)
                    st.success("Órgão adicionado!")
                    st.rerun()

# ------------------------------------------------------------------------------
# 8. GESTÃO DE SUBPROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Restrições Vinculadas")
    tab_s1, tab_s2 = st.tabs(["➕ Cadastrar Subprocesso", "📋 Listar Subprocessos"])
    procs = get_processos_principais()
    
    with tab_s1:
        if procs:
            dict_p_sub = {}
            for p in procs:
                c_mae = get_cliente_por_id(p["cliente_id"])
                dict_p_sub[p["id"]] = f"{c_mae['nome_razao'] if c_mae else 'Cliente'} | Proc: {p['numero_processo_principal']} | {p['endereco_empreendimento']}"
            
            with st.form("form_sub_novo"):
                pid_sub = st.selectbox("Selecione o Processo Principal Vinculado *", list(dict_p_sub.keys()), format_func=lambda x: dict_p_sub[x])
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    orgao_s = st.selectbox("Órgão *", get_orgaos())
                    num_s = st.text_input("Nº Subprocesso")
                    desc_s = st.text_area("Descrição da Exigência *")
                with c_s2:
                    resp_s = st.selectbox("Responsável *", list(get_equipe().keys()))
                    num_desp_s = st.text_input("Número do Despacho")
                    prazo_f_s = st.date_input("Prazo Limite para Cumprimento", value=None)

                if st.form_submit_button("Salvar Subprocesso"):
                    run_query("""INSERT INTO subprocessos (processo_principal_id, orgao_subprocesso, numero_subprocesso, descricao_exigencia, responsavel_sub, status, numero_despacho, data_inicio, prazo_fim)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (pid_sub, orgao_s, num_s, desc_s, resp_s, "Em Tramitação", num_desp_s, str(date.today()), str(prazo_f_s) if prazo_f_s else None), fetchall=False)
                    st.success("Subprocesso cadastrado com sucesso!")
                    st.rerun()
        else:
            st.info("É necessário ter ao menos um Processo Principal cadastrado.")

    with tab_s2:
        subs = get_subprocessos()
        if subs:
            dados_subs = []
            for s in subs:
                p_m = get_processo_por_id(s.get("processo_principal_id"))
                c_m = get_cliente_por_id(p_m["cliente_id"]) if p_m else None
                dados_subs.append({
                    "Cliente": c_m["nome_razao"] if c_m else "N/A",
                    "Processo Principal": p_m["numero_processo_principal"] if p_m else "N/A",
                    "Endereço": p_m["endereco_empreendimento"] if p_m else "N/A",
                    "Órgão": s.get("orgao_subprocesso"),
                    "Nº Subprocesso": s.get("numero_subprocesso"),
                    "Exigência": s.get("descricao_exigencia"),
                    "Responsável": s.get("responsavel_sub"),
                    "Status": s.get("status"),
                    "Prazo Limite": s.get("prazo_fim")
                })
            st.dataframe(pd.DataFrame(dados_subs), use_container_width=True)
        else:
            st.info("Nenhum subprocesso cadastrado.")

# ------------------------------------------------------------------------------
# 9. MÓDULO FINANCEIRO
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, Boletos e Comprovantes")
    tab_f1, tab_f2 = st.tabs(["📋 Extrato Financeiro Completo", "➕ Novo Lançamento Financeiro"])
    
    with tab_f1:
        fin = get_financeiro()
        if fin:
            dados_f = []
            for item in fin:
                c_f = get_cliente_por_id(item.get("cliente_id"))
                p_f = get_processo_por_id(item.get("processo_principal_id"))
                dados_f.append({
                    "Cliente": c_f["nome_razao"] if c_f else "N/A",
                    "Processo Principal": p_f["numero_processo_principal"] if p_f else "Geral/Sede",
                    "Endereço": p_f["endereco_empreendimento"] if p_f else (c_f["endereco_cliente"] if c_f else "N/A"),
                    "Tipo Encargo": item.get("tipo_documento"),
                    "Nº Doc/Boleto": item.get("numero_documento"),
                    "Descrição": item.get("descricao"),
                    "Valor (R$)": item.get("valor"),
                    "Vencimento": item.get("vencimento"),
                    "Pagador": item.get("pagador"),
                    "Status": item.get("status_pagamento"),
                    "Boleto Anexo": item.get("anexo_boleto_nome"),
                    "Comprovante Anexo": item.get("anexo_comprovante_nome")
                })
            st.dataframe(pd.DataFrame(dados_f), use_container_width=True)
        else:
            st.info("Nenhum lançamento financeiro registrado.")
            
    with tab_f2:
        clis = get_clientes()
        procs = get_processos_principais()
        if clis:
            dict_cli_f = {c["id"]: c["nome_razao"] for c in clis}
            cli_f_id = st.selectbox("Cliente *", list(dict_cli_f.keys()), format_func=lambda x: dict_cli_f[x])
            
            procs_do_cli
