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

def get_orgaos_df():
    return run_df("SELECT * FROM orgaos")

def get_orgaos():
    return get_orgaos_df()["nome"].tolist()

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
                        st.success("Cadastro e
