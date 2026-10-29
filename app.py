import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Configuração de Layout Sobrio e Empresarial
st.set_page_config(
    page_title="B2x Arquitetura - Gestão Processual",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada baseada na Identidade B2x Arquitetura
st.markdown("""
    <style>
    /* Estilo Geral */
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #022B3A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Titulos e Cartões */
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
    
    /* Botões */
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

# 1. BASE DE DADOS DA EQUIPE
EQUIPE = {
    "Gabriela": "Captação / Negociação / Entrada",
    "Mariana": "Financeiro / Propostas / Pagamentos",
    "Anna": "Processos / Exigências / RRT / Relatórios",
    "Bruno": "Processos / RGI / Diligências Externas",
    "Camila": "Atendimento / Obra / Mídias",
    "Alessandra": "Projetos / Prefeitura",
    "Lilian": "Projetos / Prefeitura / RRT"
}

LISTA_INTEGRANTES = list(EQUIPE.keys())

STATUS_OPCOES = [
    "1. Captação / Proposta Comercial",
    "2. Análise Inicial / Elaboração Projeto",
    "3. Em Tramitação no Órgão",
    "4. Em Exigência / Aguardando Documentos",
    "5. Aguardando Pagamento de Taxa/RRT",
    "6. Concluído / Licenciado / Averbado"
]

# Inicialização de Órgãos na Sessão
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

# Inicialização dos Processos
if "processos" not in st.session_state:
    st.session_state.processos = [
        {
            "id": 1,
            "numero_processo": "04/001.234/2026",
            "cliente_empreendimento": "Residencial Barra Park",
            "orgao": "Prefeitura (SEI.RIO / Licenciamento)",
            "tipo_servico": "Concessão de Habite-se",
            "designado_por": "Gabriela",
            "responsavel_atual": "Anna",
            "status": "4. Em Exigência / Aguardando Documentos",
            "prazo_limite": date(2026, 11, 20),
            "restricoes": [
                {
                    "id_sub": 101,
                    "descricao": "Adequar prancha do projeto legal conforme recuo exigido",
                    "orgao_sub": "Prefeitura (SEI.RIO / Licenciamento)",
                    "atribuido_a": "Alessandra",
                    "status_sub": "Em Andamento",
                    "prazo_sub": date(2026, 11, 12)
                },
                {
                    "id_sub": 102,
                    "descricao": "Emitir e recolher RRT de Execução de Obra",
                    "orgao_sub": "Financeiro Interno / Proposta (Mariana)",
                    "atribuido_a": "Anna",
                    "status_sub": "Aguardando Pagamento Mariana",
                    "prazo_sub": date(2026, 11, 10)
                }
            ]
        }
    ]

# MENU LATERAL COM CARREGAMENTO DA LOGO
if os.path.exists("LOGO.png"):
    st.sidebar.image("LOGO.png", use_container_width=True)
else:
    st.sidebar.markdown("### B2x Arquitetura")

st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Módulos do Sistema", 
    ["Dashboard Executivo", "Painel de Processos", "Entrada Rápida", "Gestão de Órgãos", "Fila Individual", "Relatórios"]
)

st.title("B2x Arquitetura | Sistema de Gestão Processual")

# 1. DASHBOARD EXECUTIVO
if menu == "Dashboard Executivo":
    st.subheader("Painel Geral de Acompanhamento")
    
    df_proc = pd.DataFrame(st.session_state.processos)
    todas_restricoes = []
    for p in st.session_state.processos:
        for r in p["restricoes"]:
            r_copy = r.copy()
            r_copy["processo_pai"] = p["numero_processo"]
            r_copy["cliente"] = p["cliente_empreendimento"]
            todas_restricoes.append(r_copy)
    df_rest = pd.DataFrame(todas_restricoes) if todas_restricoes else pd.DataFrame()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Processos em Tramitação", len(df_proc))
    c2.metric("Pendentes de Exigência", len(df_proc[df_proc["status"].str.contains("Exigência")]))
    c3.metric("Aguardando Taxas / Pagamentos", len(df_proc[df_proc["status"].str.contains("Pagamento")]))
    c4.metric("Subprocessos / Exigências", len(df_rest) if not df_rest.empty else 0)

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

# 2. PAINEL DE PROCESSOS
elif menu == "Painel de Processos":
    st.subheader("Listagem e Gestão de Processos")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_resp = st.selectbox("Filtrar por Responsável:", ["Todos"] + LISTA_INTEGRANTES)
    with col_f2:
        filtro_orgao = st.selectbox("Filtrar por Órgão:", ["Todos"] + st.session_state.lista_orgaos)

    processos_exibicao = st.session_state.processos
    if filtro_resp != "Todos":
        processos_exibicao = [p for p in processos_exibicao if p["responsavel_atual"] == filtro_resp]
    if filtro_orgao != "Todos":
        processos_exibicao = [p for p in processos_exibicao if p["orgao"] == filtro_orgao]

    st.divider()

    for proc in processos_exibicao:
        with st.expander(f"PROCESSO: {proc['numero_processo']} | {proc['cliente_empreendimento']} — Responsável: {proc['responsavel_atual']}"):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.write(f"**Cliente / Empreendimento:** {proc['cliente_empreendimento']}")
                st.write(f"**Nº Processo / RGI:** {proc['numero_processo']}")
                st.write(f"**Órgão Principal:** {proc['orgao']}")
            
            with col_b:
                st.write(f"**Serviço Contratado:** {proc['tipo_servico']}")
                st.write(f"**Entrada Registrada por:** {proc['designado_por']}")
                st.write(f"**Prazo Limite:** {proc['prazo_limite'].strftime('%d/%m/%Y') if proc['prazo_limite'] else 'Não informado'}")

            with col_c:
                novo_st = st.selectbox("Atualizar Status", STATUS_OPCOES, index=STATUS_OPCOES.index(proc['status']), key=f"st_{proc['id']}")
                novo_resp = st.selectbox("Reatribuir Responsável", LISTA_INTEGRANTES, index=LISTA_INTEGRANTES.index(proc['responsavel_atual']), key=f"resp_{proc['id']}")
                if st.button("Atualizar Processo", key=f"btn_salvar_{proc['id']}"):
                    proc['status'] = novo_st
                    proc['responsavel_atual'] = novo_resp
                    st.success("Registros atualizados com sucesso.")
                    st.rerun()

            st.markdown("---")
            st.markdown("###### Subprocessos e Exigências Associadas")
            
            if proc["restricoes"]:
                for sub in proc["restricoes"]:
                    c_s1, c_s2, c_s3, c_s4 = st.columns([3, 2, 2, 1])
                    c_s1.write(f"• **Descrição:** {sub['descricao']} ({sub['orgao_sub']})")
                    c_s2.write(f"**Responsável:** {sub['atribuido_a']}")
                    c_s3.write(f"**Prazo:** {sub['prazo_sub'].strftime('%d/%m/%Y') if sub['prazo_sub'] else 'N/A'}")
                    c_s4.write(f"`{sub['status_sub']}`")
            else:
                st.info("Nenhuma exigência técnica cadastrada para este processo.")

            with st.popover("Adicionar Exigência / Subprocesso"):
                with st.form(key=f"form_sub_{proc['id']}"):
                    desc_sub = st.text_input("Descrição do Subprocesso / Exigência")
                    org_sub = st.selectbox("Órgão Competente", st.session_state.lista_orgaos)
                    destinatario = st.selectbox("Atribuir a", LISTA_INTEGRANTES)
                    prazo_s = st.date_input("Prazo de Atendimento")
                    
                    if st.form_submit_button("Salvar Subprocesso"):
                        proc["restricoes"].append({
                            "id_sub": len(proc["restricoes"]) + 101,
                            "descricao": desc_sub,
                            "orgao_sub": org_sub,
                            "atribuido_a": destinatario,
                            "status_sub": "Pendente",
                            "prazo_sub": prazo_s
                        })
                        st.success("Subprocesso vinculado.")
                        st.rerun()

# 3. ENTRADA RÁPIDA DE PROCESSOS
elif menu == "Entrada Rápida":
    st.subheader("Cadastro Inicial de Cliente e Processo")
    
    with st.form("form_entrada_expresso"):
        c_e1, c_e2 = st.columns(2)
        
        with c_e1:
            cliente = st.text_input("Cliente / Empreendimento *", placeholder="Nome do Cliente ou Empreendimento")
            num_proc = st.text_input("Nº do Processo / Prenotação RGI", placeholder="Ex: 04/100.200/2026")
            orgao_p = st.selectbox("Órgão Principal", st.session_state.lista_orgaos)
            
        with c_e2:
            servico = st.text_input("Serviço Contratado", placeholder="Ex: Licença de Obra / Averbação")
            designado = st.selectbox("Atribuir Responsável Inicial", ["Anna", "Bruno", "Alessandra", "Lilian", "Mariana", "Camila"])
            prazo_p = st.date_input("Prazo Limite para Conclusão", value=None)

        obs_iniciais = st.text_area("Observações Iniciais / Detalhes do Escopo")
        
        btn_cadastrar = st.form_submit_button("Cadastrar e Notificar Responsável")
        
        if btn_cadastrar:
            novo_id = len(st.session_state.processos) + 1
            st.session_state.processos.append({
                "id": novo_id,
                "numero_processo": num_proc if num_proc else "Em Tramitação Inicial",
                "cliente_empreendimento": cliente,
                "orgao": orgao_p,
                "tipo_servico": servico,
                "designado_por": "Gabriela",
                "responsavel_atual": designado,
                "status": "2. Análise Inicial / Elaboração Projeto" if designado in ["Alessandra", "Lilian"] else "3. Em Tramitação no Órgão",
                "prazo_limite": prazo_p,
                "restricoes": []
            })
            st.success(f"Processo cadastrado com sucesso e atribuído a {designado}.")

# 4. GESTÃO DE ÓRGÃOS (NOVO MÓDULO)
elif menu == "Gestão de Órgãos":
    st.subheader("Cadastro e Mapeamento de Órgãos Públicos")
    
    col_o1, col_o2 = st.columns([2, 1])
    
    with col_o1:
        st.markdown("##### Órgãos Cadastrados no Sistema")
        df_orgaos = pd.DataFrame({"Órgão / Autarquia / Cartório": st.session_state.lista_orgaos})
        st.dataframe(df_orgaos, use_container_width=True)
        
    with col_o2:
        st.markdown("##### Cadastrar Novo Órgão")
        with st.form("form_novo_orgao"):
            novo_orgao_nome = st.text_input("Nome do Órgão / Secretária / Cartório", placeholder="Ex: SECONSER, Patrimônio Histórico, etc.")
            btn_add_orgao = st.form_submit_button("Inspecionar e Cadastrar")
            
            if btn_add_orgao:
                if novo_orgao_nome.strip() != "":
                    if novo_orgao_nome not in st.session_state.lista_orgaos:
                        st.session_state.lista_orgaos.append(novo_orgao_nome.strip())
                        st.success("Órgão adicionado com sucesso. Já disponível para seleção nos cadastros.")
                        st.rerun()
                    else:
                        st.warning("Este órgão já está cadastrado no sistema.")
                else:
                    st.error("Informe o nome do órgão para prosseguir.")

# 5. FILA INDIVIDUAL DE TRABALHO
elif menu == "Fila Individual":
    st.subheader("Fila de Trabalho por Integrante")
    
    usuario_ativo = st.selectbox("Selecionar Integrante da Equipe:", LISTA_INTEGRANTES)
    st.caption(f"Atribuição principal: {EQUIPE[usuario_ativo]}")
    st.divider()

    meus_processos = [p for p in st.session_state.processos if p["responsavel_atual"] == usuario_ativo]
    
    st.markdown(f"##### Processos sob Responsabilidade Direta ({len(meus_processos)})")
    if meus_processos:
        for mp in meus_processos:
            st.info(f"**Empreendimento:** {mp['cliente_empreendimento']} | **Nº:** {mp['numero_processo']} | **Órgão:** {mp['orgao']} | **Status:** {mp['status']}")
    else:
        st.write("Nenhum processo principal alocado a este integrante no momento.")

    st.divider()

    minhas_tarefas = []
    for p in st.session_state.processos:
        for r in p["restricoes"]:
            if r["atribuido_a"] == usuario_ativo:
                minhas_tarefas.append({
                    "Processo Principal": p["numero_processo"],
                    "Cliente": p["cliente_empreendimento"],
                    "Exigência": r["descricao"],
                    "Órgão": r["orgao_sub"],
                    "Prazo": r["prazo_sub"],
                    "Status": r["status_sub"]
                })
                
    st.markdown(f"##### Exigências e Subprocessos Alocados ({len(minhas_tarefas)})")
    if minhas_tarefas:
        st.table(pd.DataFrame(minhas_tarefas))
    else:
        st.write("Nenhum subprocesso pendente para este integrante.")

# 6. RELATÓRIOS
elif menu == "Relatórios":
    st.subheader("Exportação de Dados Consolidados")
    
    df_completo = pd.DataFrame(st.session_state.processos)
    st.dataframe(df_completo[["numero_processo", "cliente_empreendimento", "orgao", "tipo_servico", "responsavel_atual", "status", "prazo_limite"]], use_container_width=True)
    
    csv_data = df_completo.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar Tabela para Excel / CSV",
        data=csv_data,
        file_name="relatorio_b2x_arquitetura.csv",
        mime="text/csv"
    )