import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title='Observatório Demográfico',
    page_icon=' - ',
    layout='wide',
    initial_sidebar_state='auto'
)

CORES = {
    "fundo":            "#0d1117",
    "superficie":       "#161b22",
    "borda":            "#21262d",
    "accent":           "#1f6feb",
    "accent_hover":     "#388bfd",
    "accent_suave":     "rgba(31, 111, 235, 0.15)",
    "texto_primario":   "#e6edf3",
    "texto_secundario": "#8b949e",
    "sucesso":          "#238636",
    "erro":             "#da3633",
    "alerta":           "#9e6a03",
}

ESCALA_HEATMAP='turbo'

MAPA_REGIOES = {
    'Norte': ['AC', 'AM', 'AP', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC'],
}

CAPITAIS_UFS = {
    "AC": "Rio Branco", "AL": "Maceió", "AP": "Macapá", "AM": "Manaus",
    "BA": "Salvador", "CE": "Fortaleza", "DF": "Brasília", "ES": "Vitória",
    "GO": "Goiânia", "MA": "São Luís", "MT": "Cuiabá", "MS": "Campo Grande",
    "MG": "Belo Horizonte", "PA": "Belém", "PB": "João Pessoa", "PR": "Curitiba",
    "PE": "Recife", "PI": "Teresina", "RJ": "Rio de Janeiro", "RN": "Natal",
    "RS": "Porto Alegre", "RO": "Porto Velho", "RR": "Boa Vista", "SC": "Florianópolis",
    "SP": "São Paulo", "SE": "Aracaju", "TO": "Palmas",
}

NOMES_UF = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

st.markdown(f"""
<style>
    .stApp {{
        background-color: {CORES['fundo']};
    }}

    /* Cards de métrica customizados */
    div[data-testid="stMetric"] {{
        background-color: {CORES['superficie']};
        border: 1px solid {CORES['borda']};
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        border-color: {CORES['accent']};
        transform: translateY(-2px);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {CORES['texto_secundario']} !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.72rem !important;
        letter-spacing: 0.04em;
    }}
    div[data-testid="stMetricValue"] {{
        color: {CORES['accent_hover']} !important;
        font-weight: 700;
    }}

    /* Cabeçalho hero */
    .hero-titulo {{
        font-size: 2.3rem;
        font-weight: 800;
        color: {CORES['texto_primario']};
        margin-bottom: 0.1rem;
        letter-spacing: -0.02em;
    }}
    .hero-subtitulo {{
        color: {CORES['texto_secundario']};
        font-size: 1.0rem;
        margin-bottom: 1.6rem;
    }}
    .badge-fonte {{
        display: inline-block;
        background: {CORES['accent_suave']};
        color: {CORES['accent_hover']};
        border: 1px solid {CORES['accent']};
        border-radius: 999px;
        padding: 0.15rem 0.75rem;
        font-size: 0.72rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }}

    /* Cabeçalhos de seção */
    .secao-titulo {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {CORES['texto_primario']};
        margin: 0.4rem 0 0.9rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {CORES['borda']};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {CORES['superficie']};
        border-right: 1px solid {CORES['borda']};
    }}

    /* Botão primário */
    div[data-testid="stSidebar"] button[kind="primary"] {{
        background-color: {CORES['accent']};
        border: none;
        font-weight: 600;
    }}
    div[data-testid="stSidebar"] button[kind="primary"]:hover {{
        background-color: {CORES['accent_hover']};
    }}

    /* Tabela */
    div[data-testid="stDataFrame"] {{
        border: 1px solid {CORES['borda']};
        border-radius: 8px;
    }}

    /* Tabs */
    button[data-baseweb="tab"] {{
        font-weight: 600;
    }}

    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = None
if 'pagina_atual' not in st.session_state:
    st.session_state.pagina_atual = 1
    
    
@st.cache_data(show_spinner=False)
def carregar_csv(arquivo) -> pd.DataFrame:
    """Lê o CSV do Censo de forma otimizada."""
    df = pd.read_csv(arquivo)
    return df

LINHAS_POR_PAGINA = 50

def filtrar_dados(df: pd.DataFrame, uf:str, busca:str) -> pd.DataFrame:
    """Aplica os filtros estruturais de seleção."""
    resultado = df.copy()
    
    if uf != 'TODOS':
        resultado = resultado[resultado['UF'] == uf]
        
    if busca:
        termo = busca.strip().upper()
        nomes_upper = resultado['NOME DO MUNICÍPIO'].str.upper()
        if termo in nomes_upper.values:
            resultado = resultado[nomes_upper == termo]
        else:
            resultado = resultado[nomes_upper.str.contains(termo, na=False)]
            
    return resultado

def calcular_macrorregioes(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega população total por macrorregião — equivalente ao _renderizar_heatmap (caso A)."""
    pop_por_uf = df.groupby("UF")["POP. TOTAL"].sum().to_dict()
    linhas = []
    for regiao, ufs in MAPA_REGIOES.items():
        total = sum(pop_por_uf.get(uf, 0) for uf in ufs)
        linhas.append({"Macrorregião": regiao, "População": total})
    resultado = pd.DataFrame(linhas)
    total_geral = resultado["População"].sum()
    resultado["Percentual"] = (resultado["População"] / total_geral * 100) if total_geral > 0 else 0
    return resultado.sort_values("População", ascending=False)

def calcular_capital_interior(df_global: pd.DataFrame, uf: str) -> pd.DataFrame:
    """Capital vs. Interior de uma UF específica — equivalente ao _renderizar_heatmap (caso B)."""
    df_estado = df_global[df_global["UF"] == uf]
    capital_nome = CAPITAIS_UFS.get(uf, "")

    df_capital = df_estado[df_estado["NOME DO MUNICÍPIO"].str.upper() == capital_nome.upper()]
    pop_capital = df_capital["POP. TOTAL"].sum() if not df_capital.empty else 0

    total_estado = df_estado["POP. TOTAL"].sum()
    pop_interior = total_estado - pop_capital

    dados = pd.DataFrame([
        {"Categoria": f"Capital · {capital_nome}", "População": pop_capital},
        {"Categoria": "Interior", "População": pop_interior},
    ])
    total = dados["População"].sum()
    dados["Percentual"] = (dados["População"] / total * 100) if total > 0 else 0
    return dados.sort_values("População", ascending=False)

st.title('Observatório Demográfico')
st.subheader('Análise de Dados Públicos do IBGE • Censo Demográfico 2022')
st.caption('Edição nativa desenvolvida com componentes padrão do ecossistema Streamlit.')

with st.sidebar:
    st.markdown("### Filtros de Pesquisa")

    arquivo_csv = st.file_uploader(
        "Carregar arquivo *.csv do Censo 2022",
        type=["csv"],
        help="Selecione o arquivo de resultados municipais do IBGE.",
    )

    if arquivo_csv is not None:
        try:
            st.session_state.df = carregar_csv(arquivo_csv)
            st.success(f"{len(st.session_state.df):,} municípios carregados.")
        except Exception as e:
            st.error(f"Erro ao ler o CSV: {e}")
            st.session_state.df = None

    st.divider()

    df = st.session_state.df

    if df is not None:
        opcoes_uf = ["TODOS"] + sorted(df["UF"].unique().tolist())
        uf_selecionada = st.selectbox(
            "Filtrar por UF",
            options=opcoes_uf,
            format_func=lambda uf: "— Todos os Estados —" if uf == "TODOS" else f"{uf} · {NOMES_UF.get(uf, uf)}",
        )

        if uf_selecionada != "TODOS":
            municipios_disponiveis = sorted(
                df[df["UF"] == uf_selecionada]["NOME DO MUNICÍPIO"].unique().tolist()
            )
        else:
            municipios_disponiveis = sorted(df["NOME DO MUNICÍPIO"].unique().tolist())

        busca_municipio = st.selectbox(
            "Buscar por município",
            options=["— Nenhum filtro —"] + municipios_disponiveis,
            help="Selecione um município específico ou deixe sem filtro.",
        )
        termo_busca = "" if busca_municipio == "— Nenhum filtro —" else busca_municipio

        if st.button("Processar Dados", type="primary", use_container_width=True):
            st.session_state.pagina_atual = 1

        st.divider()
        st.caption(
            "Fonte: [Censo Demográfico 2022 — IBGE]"
            "(https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
            "Populacao_e_domicilios_Primeiros_resultados/Resultados_da_2a_apuracao_20231027/) · "
            "Diretoria de Pesquisas (DPE) · Coordenação Técnica do Censo (CTD)"
        )
    else:
        uf_selecionada = "TODOS"
        termo_busca = ""
        st.info("⚙️ Carregue um arquivo CSV do Censo 2022 para começar.")

df = st.session_state.df

if df is None:
    st.warning("⚠️ Nenhuma base carregada. Use o painel lateral para carregar um CSV do Censo 2022.")
    st.stop()
    
df_filtrado = filtrar_dados(df, uf_selecionada, termo_busca)

if len(df_filtrado) == 0:
    st.error(f"⚠️ Nenhum município encontrado para UF={uf_selecionada} | Busca='{termo_busca}'.")
    st.stop()
    
df_filtrado = filtrar_dados(df, uf_selecionada, termo_busca)
    
st.markdown('<div class="secao-titulo">Principais Métricas</div>', unsafe_allow_html=True)

total_coletado = int(df_filtrado["POP. COLETADA"].sum())
total_imputado = int(df_filtrado["POP. IMPUTADA"].sum())
total_geral = int(df_filtrado["POP. TOTAL"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("População Coletada", f"{total_coletado:,}")
col2.metric("População Imputada", f"{total_imputado:,}")
col3.metric("População Total", f"{total_geral:,}")
col4.metric("Municípios Encontrados", f"{len(df_filtrado):,}")

st.write("")

aba_tabela, aba_analitica = st.tabs(["Dados dos Municípios", "Visão Analítica"])

with aba_tabela:
    st.markdown('<div class="secao-titulo">Análise Detalhada por Município</div>', unsafe_allow_html=True)

    total_registros = len(df_filtrado)
    total_paginas = ((total_registros - 1) // LINHAS_POR_PAGINA) + 1

    if st.session_state.pagina_atual > total_paginas:
        st.session_state.pagina_atual = total_paginas
    if st.session_state.pagina_atual < 1:
        st.session_state.pagina_atual = 1

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_a:
        if st.button("← Anterior", disabled=(st.session_state.pagina_atual <= 1), use_container_width=True):
            st.session_state.pagina_atual -= 1
            st.rerun()
    with col_b:
        st.markdown(
            f"<div style='text-align:center; padding-top:0.4rem; color:{CORES['texto_secundario']};'>"
            f"Página {st.session_state.pagina_atual} de {total_paginas} · {total_registros:,} registros</div>",
            unsafe_allow_html=True,
        )
    with col_c:
        if st.button("Próximo →", disabled=(st.session_state.pagina_atual >= total_paginas), use_container_width=True):
            st.session_state.pagina_atual += 1
            st.rerun()

    inicio = (st.session_state.pagina_atual - 1) * LINHAS_POR_PAGINA
    fim = inicio + LINHAS_POR_PAGINA
    df_pagina = df_filtrado.iloc[inicio:fim][
        ["UF", "COD. MUNIC", "NOME DO MUNICÍPIO", "POP. COLETADA", "POP. IMPUTADA", "POP. TOTAL"]
    ].copy()

    for col in ["POP. COLETADA", "POP. IMPUTADA", "POP. TOTAL"]:
        df_pagina[col] = df_pagina[col].apply(lambda x: f"{int(x):,}")

    st.dataframe(
        df_pagina,
        use_container_width=True,
        hide_index=True,
        height=min(50 + len(df_pagina) * 35, 600),
    )

    st.caption(
        f"Tabela demográfica — população coletada, imputada e total por município. "
        f"Exibindo {LINHAS_POR_PAGINA} registros por página."
    )
    
with aba_analitica:
    st.markdown('<div class="secao-titulo">Visão Analítica — Gráficos Interativos com Plotly</div>', unsafe_allow_html=True)

    col_esq, col_dir = st.columns(2, gap="large")

    # --------------------------------------------------
    # GRÁFICO 1 — TOP 5 MUNICÍPIOS (barras horizontais)
    # Equivalente ao _renderizar_top5() do projeto original
    # --------------------------------------------------
    with col_esq:
        if len(df_filtrado) == 1:
            nome_isolado = str(df_filtrado["NOME DO MUNICÍPIO"].iloc[0])
            uf_isolada = str(df_filtrado["UF"].iloc[0])
            st.markdown(f"**Análise Individual · {nome_isolado} ({uf_isolada})**")
            st.caption("Exibindo a magnitude demográfica do município selecionado")
        else:
            titulo_top5 = "Top 5 Municípios Mais Populosos"
            if uf_selecionada != "TODOS":
                titulo_top5 += f" · {uf_selecionada}"
            st.markdown(f"**{titulo_top5}**")
            st.caption("Baseado na Pop. Total · Filtros aplicados")

        top5 = df_filtrado.nlargest(5, "POP. TOTAL").copy()
        top5["Rótulo"] = top5["NOME DO MUNICÍPIO"] + " (" + top5["UF"] + ")"
        top5 = top5.sort_values("POP. TOTAL", ascending=True)  # maior no topo do gráfico horizontal

        fig_top5 = go.Figure(go.Bar(
            x=top5["POP. TOTAL"],
            y=top5["Rótulo"],
            orientation="h",
            marker=dict(
                color=top5["POP. TOTAL"],
                colorscale=ESCALA_HEATMAP,
                line=dict(color=CORES["accent_hover"], width=0.5),
            ),
            text=top5["POP. TOTAL"].apply(lambda x: f"{int(x):,}"),
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate="<b>%{y}</b><br>População: %{x:,}<extra></extra>",
        ))
        fig_top5.update_layout(
            plot_bgcolor=CORES["superficie"],
            paper_bgcolor=CORES["superficie"],
            font=dict(color=CORES["texto_primario"], family="sans-serif"),
            margin=dict(l=10, r=30, t=10, b=10),
            height=320,
            xaxis=dict(showgrid=True, gridcolor=CORES["borda"], title=None, tickformat=",.0f"),
            yaxis=dict(showgrid=False, title=None, automargin=True),
            showlegend=False,
        )
        st.plotly_chart(fig_top5, use_container_width=True, config={"displayModeBar": False})

    # --------------------------------------------------
    # GRÁFICO 2 — MACRORREGIÃO ou CAPITAL x INTERIOR
    # Equivalente ao _renderizar_heatmap() do projeto original.
    # Sem latitude/longitude no CSV: usamos Treemap, que comunica
    # proporção de forma mais rica que um grid de tiles CSS.
    # --------------------------------------------------
    with col_dir:
        if uf_selecionada == "TODOS":
            st.markdown("**Distribuição por Macrorregião**")
            st.caption("Intensidade proporcional à participação no total nacional")
            dados_regiao = calcular_macrorregioes(df_filtrado)
            rotulo_col = "Macrorregião"
        else:
            st.markdown(f"**Distribuição Demográfica · {uf_selecionada}**")
            st.caption("Concentração populacional real entre a Capital e o Interior do Estado")
            dados_regiao = calcular_capital_interior(df, uf_selecionada)
            rotulo_col = "Categoria"

        fig_treemap = px.treemap(
            dados_regiao,
            path=[rotulo_col],
            values="População",
            color="Percentual",
            color_continuous_scale=ESCALA_HEATMAP,
            custom_data=["Percentual"],
        )
        fig_treemap.update_traces(
            texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}%<br>%{value:,.0f} hab.",
            textfont=dict(size=14),
            marker=dict(line=dict(color=CORES["fundo"], width=2)),
            hovertemplate="<b>%{label}</b><br>População: %{value:,.0f}<br>Participação: %{customdata[0]:.1f}%<extra></extra>",
        )
        fig_treemap.update_layout(
            paper_bgcolor=CORES["superficie"],
            plot_bgcolor=CORES["superficie"],
            font=dict(color=CORES["texto_primario"]),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_treemap, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # --------------------------------------------------
    # GRÁFICO EXTRA — Distribuição por UF (aproveitando Plotly)
    # Não existe no projeto original em CSS puro: é um exemplo de
    # como um framework de dados expande rapidamente a análise.
    # --------------------------------------------------
    st.markdown('<div class="secao-titulo">Distribuição Completa por Estado</div>', unsafe_allow_html=True)

    pop_por_uf = (
        df_filtrado.groupby("UF")["POP. TOTAL"]
        .sum()
        .reset_index()
        .sort_values("POP. TOTAL", ascending=False)
    )
    pop_por_uf["UF Completa"] = pop_por_uf["UF"].map(NOMES_UF).fillna(pop_por_uf["UF"])

    fig_uf = px.bar(
        pop_por_uf,
        x="UF Completa",
        y="POP. TOTAL",
        color="POP. TOTAL",
        color_continuous_scale=ESCALA_HEATMAP,
        labels={"POP. TOTAL": "População Total", "UF Completa": ""},
    )
    fig_uf.update_traces(
        hovertemplate="<b>%{x}</b><br>População: %{y:,.0f}<extra></extra>",
        marker_line_color=CORES["accent_hover"],
        marker_line_width=0.5,
    )
    fig_uf.update_layout(
        plot_bgcolor=CORES["superficie"],
        paper_bgcolor=CORES["superficie"],
        font=dict(color=CORES["texto_primario"]),
        margin=dict(l=10, r=10, t=20, b=10),
        height=380,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor=CORES["borda"], tickformat=",.0f"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_uf, use_container_width=True, config={"displayModeBar": False})

st.divider()
st.caption(
    "Observatório Demográfico · Edição Streamlit · Dados públicos do "
    "[Censo Demográfico 2022 — IBGE](https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
    "Populacao_e_domicilios_Primeiros_resultados/Resultados_da_2a_apuracao_20231027/) · "
    "Diretoria de Pesquisas (DPE) · Coordenação Técnica do Censo (CTD)"
)