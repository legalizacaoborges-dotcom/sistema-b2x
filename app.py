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

# Base de Clientes
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

# Base de Processos Principais (SMDU / LICIN / Prefeitura)
if "processos_principais" not in st.session_state:
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

# Base de Subprocessos
if "subprocessos" not in st.session_state:
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

# Base Financeira
if "financeiro" not in st.session_state:
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
        "Entrada Processo Principal (LICIN/SMDU)",
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
        if not df_p.empty:
            status_counts = df_p["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Quantidade"]
            st.bar_chart(status_counts.set_index("Status"))

    with col_g2:
        st.markdown("##### Subprocessos por Órgão Restritivo")
        if not df_sub.empty:
            sub_counts = df_sub["orgao_subprocesso"].value_counts().reset_index()
            sub_counts.columns = ["Órgão", "Quantidade"]
            st.bar_chart(sub_counts.set_index("Órgão"))

# ------------------------------------------------------------------------------
# 2. ENTRADA PROCESSO PRINCIPAL (LICIN / SMDU / PREFEITURA)
# ------------------------------------------------------------------------------
elif menu == "Entrada Processo Principal (LICIN/SMDU)":
    st.subheader("Cadastro de Processo Principal (SMDU / LICIN / SEI.RIO)")
    
    lista_clientes_nomes = [c["nome_razao"] for c in st.session_state.clientes] if st.session_state.clientes else []
    lista_equipe_nomes = list(st.session_state.equipe.keys())
    
    if lista_clientes_nomes:
        with st.form("form_processo_principal"):
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
                num_proc_p = st.text_input("Nº do Processo Principal (SMDU/LICIN/SEI.RIO) *", placeholder="Ex: 04/001.234/2026")
                servico_p = st.text_input("Serviço Contratado *", placeholder="Ex: Licença de Obra / Habite-se")

            st.markdown("##### 2. Atribuição e Prazos")
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
                    st.success("Processo Principal (LICIN/SMDU) cadastrado e sincronizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe o Número do Processo Principal.")
    else:
        st.warning("Cadastre um cliente primeiro no módulo 'Cadastro de Clientes'.")

# ------------------------------------------------------------------------------
# 3. GESTÃO DE SUBPROCESSOS
# ------------------------------------------------------------------------------
elif menu == "Gestão de Subprocessos":
    st.subheader("Subprocessos & Atendimento a Restrições do Processo Principal")
    
    tab_sub1, tab_sub2 = st.tabs(["➕ Cadastrar Novo Subprocesso", "📋 Gerenciar Subprocessos Existentes"])
    
    with tab_sub1:
        st.markdown("##### Vincular Subprocesso a um Processo Principal (SMDU/LICIN)")
        
        if st.session_state.processos_principais:
            with st.form("form_novo_subprocesso"):
                opcoes_p = [f"{p['numero_processo_principal']} — {p['cliente_nome']} ({p['endereco_empreendimento']})" for p in st.session_state.processos_principais]
                proc_p_sel_str = st.selectbox("Selecione o Processo Principal (SMDU/LICIN) *", opcoes_p)
                
                idx_p_sel = opcoes_p.index(proc_p_sel_str)
                obj_p_sel = st.session_state.processos_principais[idx_p_sel]
                
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
                    st.success("Subprocesso vinculado ao Processo Principal e salvo na nuvem!")
                    st.rerun()
        else:
            st.info("Nenhum Processo Principal cadastrado para vincular subprocessos.")

    with tab_sub2:
        st.markdown("##### Acompanhamento de Subprocessos por Processo Principal")
        
        for pm in st.session_state.processos_principais:
            st.markdown(f"#### 🏢 Processo Principal: `{pm['numero_processo_principal']}` — {pm['cliente_nome']}")
            st.write(f"**Empreendimento:** {pm['endereco_empreendimento']} | **Responsável:** {pm['responsavel_principal']}")
            
            subs_do_p = [s for s in st.session_state.subprocessos if s["processo_principal_id"] == pm["id"]]
            
            if subs_do_p:
                for sub in subs_do_p:
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
