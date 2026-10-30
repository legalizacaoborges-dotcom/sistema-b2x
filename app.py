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

# Base de Clientes (Aceita múltiplos endereços por CNPJ)
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

# Base de Processos Mãe (SMDU / LICIN / Prefeitura)
if "processos_mae" not in st.session_state:
    st.session_state.processos_mae = [
        {
            "id": 1,
            "cliente_id": 1,
            "cliente_nome": "CALADO EVENTOS E ADMINISTRAÇÃO LTDA",
            "numero_processo_mae": "04/001.555/2026 (SMDU/LICIN)",
            "endereco_empreendimento": "Unidade Barra: Av. das Américas, 3500 - Bloco 2",
            "servico_contratado": "Licença de Obra e Modificação com Acréscimo",
            "responsavel_mae": "Anna",
            "status": "4. Em Exigência / Aguardando Documentos",
            "data_inicio": date(2026, 2, 1),
            "prazo_limite": date(2026, 12, 15),
            "despachos": [
                {"data": "2026-03-10", "texto": "Publicado despacho de exigências no SEI.RIO exigindo parecer do CBMERJ e GEO-RIO."}
            ]
        }
    ]

# Base de Subprocessos (Exigências/Órgãos com Descrição, Notas e Info Relevante)
if "subprocessos" not in st.session_state:
    st.session_state.subprocessos = [
        {
            "id": 101,
            "processo_mae_id": 1,
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

# Base Financeira (Taxas, DARM, Boletos, RRT/ART)
if "financeiro" not in st.session_state:
    st.session_state.financeiro = [
        {
            "id": 1,
            "processo_mae_id": 1,
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
        "Entrada Processo Mãe (LICIN/SMDU)",
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
    
    df_mae = pd.DataFrame(st.session_state.processos_mae)
    df_sub = pd.DataFrame(st.session_state.subprocessos)
    df_fin = pd.DataFrame(st.session_state.financeiro)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes Cadastrados", len(st.session_state.clientes))
    c2.metric("Processos Mãe (SMDU/LICIN)", len(df_mae))
    c3.metric("Subprocessos / Restrições", len(df_sub))
    
    total_pendente_fin = df_fin[df_fin["status_pagamento"] == "Pendente"]["valor"].sum() if not df_fin.empty else 0.0
    c4.metric("Taxas Pendentes (R$)", f"R$ {total_pendente_fin:,.2f}")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### Processos Mãe por Status")
        if not df_mae.empty:
            status_counts = df_mae["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty:
            sub_counts = df_sub["orgao_subprocesso"].value_counts().reset_index()
            sub_counts.columns = ["Órgão", "Quantidade"]
            st.bar_chart(sub_counts.set_index("Órgão"))

# ------------------------------------------------------------------------------
# 2. ENTRADA PROCESSO MÃE (LICIN / SMDU / PREFEITURA)
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Mãe (LICIN/SMDU)":
    st.subheader("Cadastro de Processo Mãe (SMDU / LICIN / SEI.RIO)")
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else []
    lista_equipe_nomes = list(st.session_state.equipe.keys())
    
    if lista_clientes_nomes:
        with st.form("form_processo_mae"):
            st.markdown("##### 1. Identificação do Cliente e Empreendimento")
            c_pm1, c_pm2 = st.columns(2)
            
            with c_pm1:
                cliente_sel_nome = st.selectbox("Cliente Cadastrado *", lista_clientes_nomes)
                cliente_obj = next(c for c in st.session_state.clientes if c["nome_razao"] == cliente_sel_nome)
                
                end_opcoes = cliente_obj["enderecos_empreendimentos"] + ["+ Adicionar Novo Endereço para este Cliente"]
                end_sel = st.selectbox("Endereço do Empreendimento / Obra *", end_opcoes)
                
                if end_sel == "+ Adicionar Novo Endereço para este Cliente":
                    novo_end_input = st.text_input("Digite o Novo Endereço do Empreendimento:")
                else:
                    novo_end_input = end_sel

            with c_pm2:
                num_proc_mae = st.text_input("Nº do Processo Mãe (SMDU/LICIN/SEI.RIO) *", placeholder="Ex: 04/001.234/2026")
                servico_mae = st.text_input("Serviço Contratado *", placeholder="Ex: Licença de Obra / Habite-se")

            st.markdown("##### 2. Atribuição e Prazos")
            c_pm3, c_pm4 = st.columns(2)
            with c_pm3:
                resp_mae = st.selectbox("Responsável pelo Processo Mãe *", lista_equipe_nomes)
                data_inc_mae = st.date_input("Data de Início do Processo", value=date.today())
            with c_pm4:
                prazo_mae = st.date_input("Prazo Limite / Validade da Licença", value=None)
                status_mae_init = st.selectbox("Status Inicial", STATUS_OPCOES, index=2)

            btn_salvar_mae = st.form_submit_button("Cadastrar e Sincronizar Processo Mãe")
            
            if btn_salvar_mae:
                if num_proc_mae.strip() != "":
                    if end_sel == "+ Adicionar Novo Endereço para este Cliente" and novo_end_input.strip() != "":
                        cliente_obj["enderecos_empreendimentos"].append(novo_end_input.strip())
                    
                    end_final = novo_end_input.strip() if novo_end_input.strip() != "" else end_sel
                    
                    novo_id_mae = max([p["id"] for p in st.session_state.processos_mae], default=0) + 1
                    st.session_state.processos_mae.append({
                        "id": novo_id_mae,
                        "cliente_id": cliente_obj["id"],
                        "cliente_nome": cliente_obj["nome_razao"],
                        "numero_processo_mae": num_proc_mae,
                        "endereco_empreendimento": end_final,
                        "servico_contratado": servico_mae,
                        "responsavel_mae": resp_mae,
                        "status": status_mae_init,
                        "data_inicio": data_inc_mae,
                        "prazo_limite": prazo_mae,
                        "despachos": []
                    })
                    salvar_dados(pd.DataFrame(st.session_state.processos_mae), "Processos_Mae")
                    st.success("Processo Mãe (LICIN/SMDU) cadastrado e sincronizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o Número do Processo Mãe.")
    else:
        st.warning("Cadastre um cliente primeiro no módulo 'Cadastro de Clientes'.")

# ------------------------------------------------------------------------------
# 3. GESTÃO DE SUBPROCESSOS (DESCRIÇÃO, NOTAS & INFO RELEVANTE)
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Atendimento a Restrições do Processo Mãe")
    
    tab_sub1, tab_sub2 = st.tabs(["➕ Cadastrar Novo Subprocesso", "📋 Gerenciar Subprocessos Existentes"])
    
    with tab_sub1:
        st.markdown("##### Vincular Subprocesso a um Processo Mãe (SMDU/LICIN)")
        
        if st.session_state.processos_mae:
            with st.form("form_novo_subprocesso"):
                opcoes_mae = [f"{pm['numero_processo_mae']} — {pm['cliente_nome']} ({pm['endereco_empreendimento']})" for pm in st.session_state.processos_mae]
                proc_mae_sel_str = st.selectbox("Selecione o Processo Mãe (SMDU/LICIN) *", opcoes_mae)
                
                idx_mae_sel = opcoes_mae.index(proc_mae_sel_str)
                obj_mae_sel = st.session_state.processos_mae[idx_mae_sel]
                
                c_sub1, c_sub2 = st.columns(2)
                with c_sub1:
                    orgao_sub = st.selectbox("Órgão do Subprocesso / Exigência *", st.session_state.lista_orgaos[1:])
                    num_sub = st.text_input("Nº do Subprocesso / Requerimento / Prenotação", placeholder="Ex: CBMERJ-10293 / Prenotação RGI 88302")
                    desc_exigencia = st.text_area("Descrição do Subprocesso / Objeto da Exigência *", placeholder="Descreva os detalhes da exigência...")

                with c_sub2:
                    info_relevante_input = st.text_area("Informação Relevante / Ponto de Atenção", placeholder="Ex: Exigência vinculada à aprovação do parecer técnico da GEO-RIO.")
                    resp_sub = st.selectbox("Responsável pelo Subprocesso *", list(st.session_state.equipe.keys()))
                    data_in_sub = st.date_input("Data de Início do Subprocesso", value=date.today())
                    prazo_fim_sub = st.date_input("Prazo Limite para Atendimento", value=None)

                btn_add_sub = st.form_submit_button("Cadastrar e Vincular Subprocesso na Nuvem")
                
                if btn_add_sub:
                    novo_id_sub = max([s["id"] for s in st.session_state.subprocessos], default=0) + 1
                    st.session_state.subprocessos.append({
                        "id": novo_id_sub,
                        "processo_mae_id": obj_mae_sel["id"],
                        "cliente_id": obj_mae_sel["cliente_id"],
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
                    st.success("Subprocesso vinculado ao Processo Mãe e salvo na nuvem!")
                    st.rerun()
        else:
            st.info("Nenhum Processo Mãe cadastrado para vincular subprocessos.")

    with tab_sub2:
        st.markdown("##### Acompanhamento de Subprocessos por Processo Mãe")
        
        for pm in st.session_state.processos_mae:
            st.markdown(f"#### 🏢 Processo Mãe: `{pm['numero_processo_mae']}` — {pm['cliente_nome']}")
            st.write(f"**Empreendimento:** {pm['endereco_empreendimento']} | **Responsável Mãe:** {pm['responsavel_mae']}")
            
            subs_do_mae = [s for s in st.session_state.subprocessos if s["processo_mae_id"] == pm["id"]]
            
            if subs_do_mae:
                for sub in subs_do_mae:
                    with st.expander(f"📌 Subprocesso: {sub['orgao_subprocesso']} ({sub['numero_subprocesso']}) — Responsável: {sub['responsavel_sub']}"):
                        
                        if sub.get("informacao_relevante"):
                            st.warning(f"⚠️ **Informação Relevante / Ponto de Atenção:** {sub['informacao_relevante']}")
                        
                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            st.markdown("###### Descrição do Subprocesso")
                            st.write(sub['descricao_exigencia'] if sub['descricao_exigencia'] else "Sem descrição cadastrada.")
                            st.write(f"**Data de Início:** {sub['data_inicio'].strftime('%d/%m/%Y') if sub['data_inicio'] else 'N/A'}")
                            st.write(f"**Prazo Limite:** {sub['prazo_fim'].strftime('%d/%m/%Y') if sub['prazo_fim'] else 'N/A'}")
                        
                        with col_s2:
                            novo_st_sub = st.selectbox("Status do Subprocesso", ["Em Tramitação", "Aguardando Documento do Cliente", "Em Exigência", "Concluído / Aprovado"], key=f"st_sub_{sub['id']}")
                            if st.button("Atualizar Status", key=f"btn_st_sub_{sub['id']}"):
                                sub["status"] = novo_st_sub
                                salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                                st.success("Status atualizado na nuvem!")
                                st.rerun()

                        st.markdown("---")
                        st.markdown("###### 📝 Notas e Observações Internas da Equipe")
                        if sub.get("notas_internas"):
                            for nota in sub["notas_internas"]:
                                st.info(f"**[{nota['data']}] por {nota['autor']}:** {nota['texto']}")
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
                            for d in sub["despachos"]:
                                st.write(f"📅 **[{d['data']}]** — {d['texto']}")
                        
                        novo_despacho_txt = st.text_input("Novo Despacho Oficial / Parecer:", key=f"txt_desp_{sub['id']}")
                        if st.button("Inserir Despacho", key=f"btn_desp_{sub['id']}"):
                            if novo_despacho_txt.strip() != "":
                                sub["despachos"].append({
                                    "data": date.today().strftime("%Y-%m-%d"),
                                    "texto": novo_despacho_txt.strip()
                                })
                                st.success("Despacho registrado!")
                                st.rerun()

                        st.markdown("---")
                        st.markdown("###### Documentos & Comprovantes Anexados")
                        if sub.get("documentos"):
                            for doc in sub["documentos"]:
                                st.write(f"📄 **{doc['nome']}** (Data: {doc['data']})")
                        
                        up_doc_sub = st.file_uploader("Anexar Comprovante / Licença (PDF)", type=["pdf", "png", "jpg"], key=f"up_sub_{sub['id']}")
                        if up_doc_sub:
                            if st.button("Salvar Arquivo no Subprocesso", key=f"btn_up_sub_{sub['id']}"):
                                novo_id_d = len(sub.get("documentos", [])) + 1
                                if "documentos" not in sub:
                                    sub["documentos"] = []
                                sub["documentos"].append({"id": novo_id_d, "nome": up_doc_sub.name, "data": date.today().strftime("%Y-%m-%d")})
                                st.success("Documento salvo!")
                                st.rerun()

                        if st.button(f"🚨 Excluir Subprocesso", key=f"del_sub_{sub['id']}", type="primary"):
                            st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s["id"] != sub["id"]]
                            salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                            st.success("Subprocesso removido da nuvem!")
                            st.rerun()
            else:
                st.write("Nenhum subprocesso/exigência vinculado a este Processo Mãe.")
            st.divider()

# ------------------------------------------------------------------------------
# 4. PAINEL GERAL DE PROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Painel Geral de Processos":
    st.subheader("Visão Geral de Processos Mãe e Seus Subprocessos")
    
    for pm in list(st.session_state.processos_mae):
        with st.expander(f"PROCESSO MÃE: {pm['numero_processo_mae']} | {pm['cliente_nome']} — Resp: {pm['responsavel_mae']}"):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                st.write(f"**Empreendimento:** {pm['endereco_empreendimento']}")
                st.write(f"**Serviço Contratado:** {pm['servico_contratado']}")
            with c_p2:
                st.write(f"**Status Mãe:** `{pm['status']}`")
                st.write(f"**Prazo Validade:** {pm['prazo_limite'].strftime('%d/%m/%Y') if pm['prazo_limite'] else 'N/A'}")

            subs = [s for s in st.session_state.subprocessos if s["processo_mae_id"] == pm["id"]]
            st.markdown(f"###### Subprocessos / Restrições Vinculadas ({len(subs)})")
            for sb in subs:
                st.info(f"**Órgão:** {sb['orgao_subprocesso']} | **Nº:** {sb['numero_subprocesso']} | **Resp:** {sb['responsavel_sub']} | **Status:** `{sb['status']}`")

            if st.button(f"🚨 Excluir Processo Mãe e Subprocessos", key=f"del_pm_{pm['id']}", type="primary"):
                st.session_state.processos_mae = [p for p in st.session_state.processos_mae if p["id"] != pm["id"]]
                st.session_state.subprocessos = [s for s in st.session_state.subprocessos if s["processo_mae_id"] != pm["id"]]
                salvar_dados(pd.DataFrame(st.session_state.processos_mae), "Processos_Mae")
                salvar_dados(pd.DataFrame(st.session_state.subprocessos), "Subprocessos")
                st.success("Removidos da nuvem com sucesso!")
                st.rerun()

# ------------------------------------------------------------------------------
# 5. CADASTRO DE CLIENTES
# ------------------------------------------------------------------------------
elif menu == "Cadastro de Clientes":
    st.subheader("Gerenciamento de Clientes e Endereços")
    
    tab_cli1, tab_cli2 = st.tabs(["➕ Cadastrar Novo Cliente", "🗑️ Gerenciar / Excluir Cliente"])
    
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
                end_cli = st.text_input("Endereço Principal do Cliente")
                end_emp_inicial = st.text_input("Endereço do Primeiro Empreendimento / Obra *")

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
            cli_excluir = st.selectbox("Selecione o Cliente para Excluir:", [c["nome_razao"] for c in st.session_state.clientes])
            if st.button(f"🚨 Excluir Cliente '{cli_excluir}'", type="primary"):
                st.session_state.clientes = [c for c in st.session_state.clientes if c["nome_razao"] != cli_excluir]
                salvar_dados(pd.DataFrame(st.session_state.clientes), "Clientes")
                st.success("Cliente removido da nuvem!")
                st.rerun()

    st.divider()
    st.markdown("##### Base Geral de Clientes")
    df_cli_view = pd.DataFrame(st.session_state.clientes)
    if not df_cli_view.empty:
        st.dataframe(df_cli_view[["id", "tipo_pessoa", "nome_razao", "cpf_cnpj", "numero_proposta", "numero_contrato"]], use_container_width=True)

# ------------------------------------------------------------------------------
# 6. BUSCA INTEGRADA (LUPA 360°)
# ------------------------------------------------------------------------------
elif menu == "Busca Integrada (Lupa 360°)":
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
                st.write(f"**Representante:** {cliente_obj['representante_legal'] or 'N/A'}")
            with c_info2:
                st.write(f"**Proposta:** {cliente_obj['numero_proposta']}")
                st.write(f"**Contrato:** {cliente_obj['numero_contrato']}")
            with c_info3:
                st.write(f"**Endereço Comercial:** {cliente_obj['endereco_cliente']}")
                st.write("**Empreendimentos Cadastrados:**")
                for end in cliente_obj["enderecos_empreendimentos"]:
                    st.write(f"• {end}")

            st.divider()
            
            procs_mae_cli = [p for p in st.session_state.processos_mae if p["cliente_id"] == cliente_obj["id"]]
            st.markdown(f"##### 📌 Processos Mãe e Subprocessos ({len(procs_mae_cli)})")
            
            for pmc in procs_mae_cli:
                st.info(f"**Processo Mãe:** {pmc['numero_processo_mae']} | **Empreendimento:** {pmc['endereco_empreendimento']} | **Status:** `{pmc['status']}`")
                subs_cli = [s for s in st.session_state.subprocessos if s["processo_mae_id"] == pmc["id"]]
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
# 7. MÓDULO FINANCEIRO (MARIANA)
# ------------------------------------------------------------------------------
elif menu == "Módulo Financeiro (Mariana)":
    st.subheader("Módulo Financeiro - Controle de Taxas, RRT/ART e Boletos")
    
    tab_fin1, tab_fin2 = st.columns([2, 1])
    
    with tab_fin2:
        st.markdown("##### Novo Lançamento Financeiro")
        with st.form("form_novo_financeiro"):
            cli_fin_nome = st.selectbox("Cliente", [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else ["Nenhum"])
            
            cli_id_sel = next((c["id"] for c in st.session_state.clientes if c["nome_razao"] == cli_fin_nome), 1)
            procs_mae_opcoes = [p["numero_processo_mae"] for p in st.session_state.processos_mae if p["cliente_id"] == cli_id_sel]
            
            proc_mae_fin = st.selectbox("Processo Mãe Relacionado", procs_mae_opcoes if procs_mae_opcoes else ["Nenhum"])
            
            tipo_doc = st.selectbox("Tipo de Encargo", ["DARM / Taxa Municipal", "RRT (CAU)", "ART (CREA)", "Boleto Cartório / RGI", "Honorários / Outros"])
            num_doc = st.text_input("Número do Boleto / RRT / ART / DARM")
            desc_fin = st.text_input("Descrição da Taxa")
            val_fin = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
            venc_fin = st.date_input("Data de Vencimento")
            pagador_fin = st.selectbox("Responsável pelo Pagamento", ["B2x (A Reembolsar)", "Cliente Direto"])
            
            uploaded_file = st.file_uploader("Anexar Comprovante / Guia (PDF)", type=["pdf", "png", "jpg"])
            
            btn_add_fin = st.form_submit_button("Lançar no Financeiro na Nuvem")
            if btn_add_fin:
                novo_id_fin = max([f["id"] for f in st.session_state.financeiro], default=0) + 1
                st.session_state.financeiro.append({
                    "id": novo_id_fin,
                    "processo_mae_id": 1,
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
                st.success("Lançamento financeiro registrado na nuvem com sucesso!")
                st.rerun()

    with tab_fin1:
        st.markdown("##### Painel de Controle de Contas e Taxas")
        if st.session_state.financeiro:
            for item in list(st.session_state.financeiro):
                with st.expander(f"💰 {item['tipo_documento']} — R$ {item['valor']:,.2f} | Vencimento: {item['vencimento'].strftime('%d/%m/%Y')} ({item['status_pagamento']})"):
                    st.write(f"**Nº Documento:** {item['numero_documento']} | **Pagador:** {item['pagador']}")
                    st.write(f"**Descrição:** {item['descricao']}")
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("Marcar como Pago", key=f"btn_pago_{item['id']}"):
                            item['status_pagamento'] = "Pago / Quitado"
                            salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                            st.success("Status atualizado na nuvem!")
                            st.rerun()
                    with c_btn2:
                        if st.button("🗑️ Excluir Lançamento", key=f"btn_del_fin_{item['id']}"):
                            st.session_state.financeiro = [f for f in st.session_state.financeiro if f['id'] != item['id']]
                            salvar_dados(pd.DataFrame(st.session_state.financeiro), "Financeiro")
                            st.success("Lançamento excluído da nuvem!")
                            st.rerun()
        else:
            st.info("Nenhum encargo financeiro registrado.")

# ------------------------------------------------------------------------------
# 8. GESTÃO DE ÓRGÃOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro de Órgãos e Autarquias")
    col_o1, col_o2 = st.columns([2, 1])
    with col_o1:
        for org in list(st.session_state.lista_orgaos):
            c_org1, c_org2 = st.columns([4, 1])
            with c_org1:
                st.write(f"🏛️ **{org}**")
            with c_org2:
                if st.button("Excluir", key=f"del_org_{org}"):
                    st.session_state.lista_orgaos.remove(org)
                    st.rerun()
    with col_o2:
        with st.form("form_novo_orgao"):
            novo_o = st.text_input("Nome do Órgão")
            if st.form_submit_button("Cadastrar"):
                if novo_o.strip():
                    st.session_state.lista_orgaos.append(novo_o.strip())
                    st.rerun()

# ------------------------------------------------------------------------------
# 9. GESTÃO DA EQUIPE
# ------------------------------------------------------------------------------
elif menu == "Gestão da Equipe":
    st.subheader("Gerenciamento de Funcionários")
    col_eq1, col_eq2 = st.columns([2, 1])
    with col_eq1:
        for nome_f, cargo_f in list(st.session_state.equipe.items()):
            st.write(f"👤 **{nome_f}** — *{cargo_f}*")
    with col_eq2:
        with st.form("form_novo_f"):
            nf = st.text_input("Nome")
            cf = st.text_input("Função")
            if st.form_submit_button("Cadastrar Funcionário"):
                if nf.strip():
                    st.session_state.equipe[nf.strip()] = cf.strip()
                    st.rerun()

# ------------------------------------------------------------------------------
# 10. FILA INDIVIDUAL
# ------------------------------------------------------------------------------
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    user_sel = st.selectbox("Selecionar Integrante:", list(st.session_state.equipe.keys()))
    
    subs_meus = [s for s in st.session_state.subprocessos if s["responsavel_sub"] == user_sel]
    maes_meus = [p for p in st.session_state.processos_mae if p["responsavel_mae"] == user_sel]
    
    st.markdown(f"##### Processos Mãe sob Responsabilidade de {user_sel} ({len(maes_meus)})")
    for mm in maes_meus:
        st.info(f"**Nº Processo Mãe:** {mm['numero_processo_mae']} | **Cliente:** {mm['cliente_nome']} | **Status:** {mm['status']}")
        
    st.markdown(f"##### Subprocessos / Exigências sob Responsabilidade de {user_sel} ({len(subs_meus)})")
    for sm in subs_meus:
        st.warning(f"**Órgão:** {sm['orgao_subprocesso']} | **Nº:** {sm['numero_subprocesso']} | **Exigência:** {sm['descricao_exigencia']} | **Status:** {sm['status']}")

# ------------------------------------------------------------------------------
# 11. RELATÓRIOS
# ------------------------------------------------------------------------------
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    df_m = pd.DataFrame(st.session_state.processos_mae)
    if not df_m.empty:
        st.dataframe(df_m[["numero_processo_mae", "cliente_nome", "endereco_empreendimento", "servico_contratado", "responsavel_mae", "status"]], use_container_width=True)
        csv_data = df_m.to_csv(index=False).encode('utf-8')
        st.download_button("Exportar Processos Mãe (CSV)", data=csv_data, file_name="relatorio_processos_mae_b2x.csv", mime="text/csv")
