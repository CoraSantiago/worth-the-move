import streamlit as st
import html
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse
import streamlit.components.v1 as components
import plotly.graph_objects as go
import re
from urllib.parse import urlparse
import streamlit as st
from noxus_kb import kb_list_documents, load_df_by_exact_name
from i18n import tr, render_language_buttons

_URL_RE = re.compile(r"https?://[^\s\]\)\"'>]+", re.IGNORECASE)

@st.cache_data(ttl=300)  # 5 min: reduz MUITO as chamadas
def _cached_kb_names(status="trained"):
    docs = kb_list_documents(status=status)
    return [((d.get("name") or "").strip()) for d in docs if (d.get("name") or "").strip()]

@st.cache_data(ttl=900, show_spinner=False)
def cached_load_df_by_exact_name(doc_name: str):
    """
    Cacheia o download/conversão do documento da KB por nome.
    Assim, trocar idioma rerenderiza a tela sem bater de novo na KB/Noxus.
    """
    if not doc_name:
        return None, None

    return load_df_by_exact_name(doc_name)

def resolve_doc_exact(base_place: str, suffix: str, status="trained") -> str | None:
    base_place = (base_place or "").strip()
    suffix = (suffix or "").strip()
    prefix = f"{base_place} - {suffix}".lower()

    try:
        names = _cached_kb_names(status=status)
    except Exception:
        # fallback: se Noxus cair, usa a última lista boa (se existir)
        names = st.session_state.get("_kb_names_cache", [])

    # guarda cache “manual” também
    if names:
        st.session_state["_kb_names_cache"] = names

    candidates = [n for n in names if n.lower().startswith(prefix)]
    if not candidates:
        return None
    candidates.sort(key=len)
    return candidates[0]

st.set_page_config(
    page_title="Worth the Move?",
    layout="wide",
    initial_sidebar_state="expanded",
)


HAZARD_CONFIG = {
    "Heatwave": {
        "label": "Heatwave",
        "suffixes": ["Heatwave"],
    },
    "Flood": {
        "label": "Flood / Heavy Rain",
        "suffixes": ["Flood", "Floods", "Heavy Rain"],
    },
    "Wildfire": {
        "label": "Wildfire",
        "suffixes": ["Wildfire"],
    },
    "Storm": {
        "label": "Storm / Severe Wind",
        "suffixes": ["Storm", "Severe Wind", "Hurricane"],
    },
    "WinterStorm": {
        "label": "Winter Storm / Blizzard",
        "suffixes": ["WinterStorm", "Winter Storm", "Snowstorm", "Blizzard"],
    },
    "Seismo": {
        "label": "Earthquake",
        "suffixes": ["Seismo", "Earthquake"],
    },
    "Eruption": {
        "label": "Volcanic Risk",
        "suffixes": ["Eruption", "Volcano", "Volcanic"],
    },
}


def resolve_doc_by_suffixes(base_place: str, suffixes: list[str]) -> str | None:
    for suffix in suffixes:
        exact = resolve_doc_exact(base_place, suffix)
        if exact:
            return exact
    return None



st.markdown("""
<style>

/* =========================
   Compacta o topo da página Analysis
   sem mexer nos botões de idioma
   ========================= */

section.main > div[data-testid="stMainBlockContainer"],
div[data-testid="stMainBlockContainer"],
.block-container {
  padding-top: 1.4rem !important;
}

/* Título do local */
h1 {
  margin-top: 0 !important;
  margin-bottom: 1.1rem !important;
  line-height: 1.1 !important;
}

/* Reduz respiro entre título e aba */
div[data-testid="stTabs"] {
  margin-top: 0.2rem !important;
}

/* Reduz altura visual da área das tabs */
div[data-testid="stTabs"] [role="tablist"] {
  margin-bottom: 0.6rem !important;
}

/* Aproxima o conteúdo da aba */
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  padding-top: 0.8rem !important;
}
            
/* =========================
   Sidebar look (dark + clean)
   ========================= */

/* Mantém teu hide do collapse (pode deixar) */
[data-testid="collapsedControl"]{ display:none !important; }
[data-testid="stSidebarCollapseButton"]{ display:none !important; }
section[data-testid="stSidebar"] button[kind="header"]{ display:none !important; }
section[data-testid="stSidebar"] [aria-label="Collapse sidebar"]{ display:none !important; }
section[data-testid="stSidebar"] [aria-label="Expand sidebar"]{ display:none !important; }

/* (Opcional) remove o "centrão" que você aplicou pra tudo ficar igual print
   Se você quiser continuar centralizado, apaga este bloco. */
section[data-testid="stSidebar"] > div:first-child{
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;  /* 👈 centraliza verticalmente */
  height: 100vh !important;            /* 👈 ocupa a altura toda */
  padding-top: 0 !important;           /* 👈 evita ficar alto demais */
  padding-bottom: 0 !important;
}
            
section[data-testid="stSidebar"] .block-container{
  padding-top: 0.25rem !important;
  padding-bottom: 0.25rem !important;
}
section[data-testid="stSidebar"] .block-container{
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* =========================
   1) Botão do Streamlit (st.button)
   ========================= */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button{
  width: 100%;
  height: 44px;

  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.10);

  background: rgba(255,255,255,0.06);
  color: rgba(255,255,255,0.92);

  font-weight: 600;
  font-size: 0.95rem;

  transition: transform 80ms ease, background 120ms ease, border-color 120ms ease;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover{
  background: rgba(255,255,255,0.10);
  border-color: rgba(255,255,255,0.16);
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button:active{
  transform: translateY(1px);
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus{
  outline: none !important;
  box-shadow: 0 0 0 2px rgba(138,180,248,0.25);
}

/* =========================
   2) Selectbox (baseweb) -> cara de input pill igual print
   ========================= */

/* Label (Saved analyses) */
section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"]{
  color: rgba(255,255,255,0.78) !important;
  font-weight: 600 !important;
  font-size: 0.90rem !important;
  margin-bottom: 6px !important;
}

/* A "caixa" do select */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div{
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;

  background: rgba(255,255,255,0.06) !important;
}

/* Texto dentro do select */
section[data-testid="stSidebar"] div[data-baseweb="select"] *{
  color: rgba(255,255,255,0.92) !important;
}

/* Hover do select */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover{
  background: rgba(255,255,255,0.10) !important;
  border-color: rgba(255,255,255,0.16) !important;
}

/* Remove “glow” exagerado padrão */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within{
  box-shadow: 0 0 0 2px rgba(138,180,248,0.25) !important;
}

/* =========================
   3) Divider mais suave (opcional)
   ========================= */
section[data-testid="stSidebar"] hr{
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.10);
  margin: 14px 0;
}

/* =========================
   Sidebar refinada / fixa
   ========================= */

section[data-testid="stSidebar"] {
  width: 330px !important;
  min-width: 330px !important;
  max-width: 330px !important;
  background: #292a33 !important;
}

section[data-testid="stSidebar"] > div:first-child {
  width: 330px !important;
  min-width: 330px !important;
  max-width: 330px !important;

  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  height: 100vh !important;

  padding-left: 18px !important;
  padding-right: 18px !important;
  box-sizing: border-box !important;
}

section[data-testid="stSidebar"] .block-container {
  padding-left: 0 !important;
  padding-right: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}

/* Espaço entre blocos */
.wtm-sidebar-spacer {
  height: 30px;
}

/* Título: análises salvas */
.wtm-sidebar-section-title {
  text-align: center;
  font-size: 1.08rem;
  font-weight: 900;
  letter-spacing: 0.01em;
  color: rgba(255,255,255,0.98);
  margin-bottom: 14px;
}



/* Selectbox fechado */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  min-height: 56px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(122,214,201,0.42) !important;
  background: rgba(255,255,255,0.075) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.16);
}

/* Texto dentro do selectbox */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
  font-size: 1rem !important;
  font-weight: 850 !important;
  color: rgba(255,255,255,0.98) !important;
}

/* Hover/focus do select */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
  background: rgba(255,255,255,0.105) !important;
  border-color: rgba(122,214,201,0.75) !important;
}

section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
  box-shadow: 0 0 0 2px rgba(122,214,201,0.22) !important;
}

/* Dropdown aberto */
ul[data-testid="stSelectboxVirtualDropdown"] * {
  font-size: 0.95rem !important;
  line-height: 1.25 !important;
}

ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"] {
  min-height: 42px !important;
}

/* Botão voltar */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
  width: 100%;
  height: 58px;
  border-radius: 18px;
  border: 1px solid rgba(122,214,201,0.34);
  background: linear-gradient(135deg, rgba(255,255,255,0.085), rgba(255,255,255,0.045));
  color: rgba(255,255,255,0.98);
  font-weight: 900;
  font-size: 1.05rem;
  letter-spacing: 0.01em;
  box-shadow: 0 10px 26px rgba(0,0,0,0.16);
  transition: all 0.18s ease;
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
  background: linear-gradient(135deg, rgba(44,143,134,0.94), rgba(35,156,146,0.88));
  border-color: rgba(122,214,201,0.88);
  transform: translateY(-1px);
}

section[data-testid="stSidebar"] div[data-testid="stButton"] > button:active {
  transform: translateY(0px);
}

/* Linha divisória */
section[data-testid="stSidebar"] hr {
  border: none;
  height: 1px;
  background: rgba(255,255,255,0.13);
  margin: 30px 0 0 0;
}       

            /* =========================
   Expanders de fontes mais discretos
   ========================= */

div[data-testid="stExpander"] details {
  border-radius: 10px !important;
}

div[data-testid="stExpander"] details summary {
  min-height: 34px !important;
  padding: 6px 10px !important;
}

div[data-testid="stExpander"] details summary p {
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  line-height: 1.15 !important;
}

div[data-testid="stExpander"] details summary svg {
  width: 14px !important;
  height: 14px !important;
}

div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] ul {
  margin-top: 6px !important;
  margin-bottom: 6px !important;
}

div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] li {
  font-size: 0.78rem !important;
  line-height: 1.25 !important;
  margin-bottom: 4px !important;
}

/* =========================
   Título/subtítulo da seção de risco
   ========================= */

.wtm-risk-title {
  font-size: 1.35rem;
  font-weight: 850;
  color: #ffffff;
  margin: 0 0 4px 0;
}

.wtm-risk-subtitle {
  font-size: 0.92rem;
  font-weight: 650;
  color: rgba(255,255,255,0.68);
  margin: 0 0 12px 0;
}

.wtm-risk-rule {
  height: 1px;
  background: rgba(255,255,255,0.10);
  margin: 0 0 12px 0;
}
/* =========================
   Força o visual dark mesmo se o usuário escolher tema light
   ========================= */

html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
main {
  background: #0b0f16 !important;
  color: #ffffff !important;
}

.block-container {
  background: #0b0f16 !important;
  color: #ffffff !important;
}

/* Header/top bar do Streamlit */
header[data-testid="stHeader"] {
  background: #0b0f16 !important;
}

/* Textos principais */
h1, h2, h3, h4, h5, h6 {
  color: #ffffff !important;
}

/* Markdown geral, sem destruir cores internas customizadas */
div[data-testid="stMarkdownContainer"] {
  color: #ffffff;
}

/* Labels padrão */
label {
  color: rgba(255,255,255,0.88) !important;
}

/* Parágrafos padrão do markdown */
div[data-testid="stMarkdownContainer"] p {
  color: inherit;
}

/* Caption/textos auxiliares */
div[data-testid="stCaptionContainer"],
.caption,
small {
  color: rgba(255,255,255,0.72) !important;
}

/* Dataframe / tabela */
div[data-testid="stDataFrame"] {
  background: #0f131b !important;
  color: #ffffff !important;
  border-radius: 10px !important;
}

/* Expander */
div[data-testid="stExpander"] details {
  background: #0f131b !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
}

div[data-testid="stExpander"] summary {
  color: #ffffff !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: #292a33 !important;
  color: #ffffff !important;
}

/* Selectbox e botões */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
  background: rgba(255,255,255,0.075) !important;
  color: #ffffff !important;
  border-color: rgba(122,214,201,0.42) !important;
}

/* Links */
a {
  color: #7ad6c9 !important;
}
            
/* =========================
   Tabela de risco customizada dark
   ========================= */

.wtm-risk-table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid rgba(255,255,255,0.13);
  border-radius: 10px;
  background: #0f131b;
}

.wtm-risk-table {
  width: 100%;
  min-width: 1320px;
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 0.88rem;
  color: rgba(255,255,255,0.94);
}

.wtm-risk-table thead th {
  background: #1a1d25;
  color: rgba(255,255,255,0.78);
  font-weight: 800;
  text-align: left;
  padding: 10px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.13);
  border-right: 1px solid rgba(255,255,255,0.09);
  white-space: nowrap;
}

.wtm-risk-table tbody td {
  padding: 10px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.09);
  border-right: 1px solid rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.94);
  font-weight: 400;
  vertical-align: top;
}

.wtm-risk-table tbody tr:hover td {
  background: rgba(255,255,255,0.035);
}

.wtm-risk-table .muted-cell {
  color: rgba(255,255,255,0.52);
}

.wtm-risk-table .basis-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wtm-risk-table th:last-child,
.wtm-risk-table td:last-child {
  border-right: none;
}
            
/* Larguras específicas da tabela de risco */
.wtm-risk-table th:nth-child(1),
.wtm-risk-table td:nth-child(1) {
  width: 210px;
  min-width: 210px;
  white-space: nowrap;
}

.wtm-risk-table th:nth-child(2),
.wtm-risk-table td:nth-child(2) {
  width: 76px;
  text-align: center;
  white-space: nowrap;
}

.wtm-risk-table th:nth-child(3),
.wtm-risk-table td:nth-child(3),
.wtm-risk-table th:nth-child(4),
.wtm-risk-table td:nth-child(4),
.wtm-risk-table th:nth-child(5),
.wtm-risk-table td:nth-child(5),
.wtm-risk-table th:nth-child(6),
.wtm-risk-table td:nth-child(6) {
  width: 135px;
  white-space: nowrap;
}

.wtm-risk-table th:nth-child(7),
.wtm-risk-table td:nth-child(7) {
  width: 135px;
  white-space: nowrap;
}

.wtm-risk-table th:nth-child(8),
.wtm-risk-table td:nth-child(8) {
  width: 115px;
  white-space: nowrap;
}

.wtm-risk-table th:nth-child(9),
.wtm-risk-table td:nth-child(9) {
  width: 145px;
  white-space: nowrap;
}

/* Base do cálculo: pode cortar o final, sem quebrar linha */
.wtm-risk-table th:nth-child(10),
.wtm-risk-table td:nth-child(10) {
  width: 330px;
  max-width: 330px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

# ✅ place precisa existir antes da sidebar (pra setar index do select)
# ✅ também precisa sobreviver ao clique nos botões de idioma

def _qp_get(name: str) -> str:
    value = st.query_params.get(name, "")
    if isinstance(value, list):
        return value[0] if value else ""
    return value or ""


place_from_url = _qp_get("place").strip()

place = (
    st.session_state.get("place")
    or place_from_url
    or ""
).strip()

if place:
    st.session_state["place"] = place

    # só escreve na URL se estiver diferente, pra evitar rerun desnecessário
    if _qp_get("place").strip() != place:
        st.query_params["place"] = place

# ======================
# SIDEBAR DINÂMICA
# Durante loading: só mostra "Check another place" + Back
# Depois do loading: mostra análises salvas + Back
# ======================

sidebar_slot = st.sidebar.empty()


def _sidebar_base_names():
    """
    Usa cache manual se existir.
    Se não existir, busca pela função cacheada.
    """
    raw = st.session_state.get("_kb_names_cache", [])

    if not raw:
        try:
            raw = _cached_kb_names(status="trained")
            if raw:
                st.session_state["_kb_names_cache"] = raw
        except Exception:
            raw = []

    return sorted(
        set([n.split(" - ")[0].strip() for n in raw if n and " - " in n])
    )


def render_analysis_sidebar(show_saved: bool):
    sidebar_slot.empty()

    current_place = (st.session_state.get("place") or place or "").strip()
    key_suffix = "ready" if show_saved else "loading"

    with sidebar_slot.container():
        if show_saved:
            base_names = _sidebar_base_names()

            if base_names:
                st.markdown(
                    f"""
                    <div class="wtm-sidebar-section-title">
                        {tr("browse_saved")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                choice = st.selectbox(
                    tr("browse_saved"),
                    base_names,
                    index=base_names.index(current_place) if current_place in base_names else 0,
                    key=f"sidebar_place_select_{key_suffix}",
                    label_visibility="collapsed",
                )

                if choice and choice != current_place:
                    st.session_state["place"] = choice
                    st.query_params["place"] = choice
                    st.rerun()

        st.markdown(
            f"""
            <div class="wtm-sidebar-spacer"></div>
            <div class="wtm-sidebar-section-title">
                {tr("check_another_place")}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"← {tr('back')}",
            use_container_width=True,
            key=f"sidebar_back_btn_{key_suffix}",
        ):
            st.switch_page("Check_another_place.py")

        st.markdown("---")

render_analysis_sidebar(show_saved=False)

if not place:
    st.warning(tr("no_place_selected"))
    st.stop()

render_language_buttons(
    "analysis_lang_switcher",
    extra_params={"place": place},
)

st.title(place)

main_panel = st.container()

def apply_dark_plot_theme(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.90)"),
        legend=dict(
            font=dict(color="rgba(255,255,255,0.86)", size=12),
            title_font=dict(color="rgba(255,255,255,0.78)", size=12),
        ),
    )

    fig.update_xaxes(
        tickfont=dict(color="rgba(255,255,255,0.76)"),
        title_font=dict(color="rgba(255,255,255,0.82)"),
        gridcolor="rgba(255,255,255,0.14)",
        zerolinecolor="rgba(255,255,255,0.22)",
    )

    fig.update_yaxes(
        tickfont=dict(color="rgba(255,255,255,0.76)"),
        title_font=dict(color="rgba(255,255,255,0.82)"),
        gridcolor="rgba(255,255,255,0.14)",
        zerolinecolor="rgba(255,255,255,0.22)",
    )

    return fig

with main_panel:
    doc_name = place


def _short_domain(url: str) -> str:
    try:
        p = urlparse(url)
        host = p.netloc or url
        return host + "…"
    except Exception:
        return "Source…"


def _fmt_date(x) -> str:
    if isinstance(x, str) and ("http://" in x or "https://" in x):
        return "-"

    try:
        if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and not x.strip()):
            return "-"

        dt = pd.to_datetime(x, errors="coerce")

        if pd.isna(dt):
            return "-"

        # Data sentinela/erro
        if dt.strftime("%d-%m-%Y") == "01-01-1970":
            return "-"

        return dt.strftime("%d-%m-%Y")

    except Exception:
        return "-"


_NUM_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")

def _num_from_any(v):
    """
    Extrai o primeiro número de um valor vindo da KB:
    ex: '36°C', '36,0', ' record: 36 ', etc.
    """
    if v is None:
        return None

    # já numérico
    if isinstance(v, (int, float)):
        if isinstance(v, float) and pd.isna(v):
            return None
        return float(v)

    s = str(v).strip()
    if not s or s.lower() in {"nan", "none", "null", "n/a", "na", "-"}:
        return None

    m = _NUM_RE.search(s)
    if not m:
        return None

    num = m.group(0).replace(",", ".")
    try:
        return float(num)
    except Exception:
        return None


def _as_float(v):
    return _num_from_any(v)


def _is_temp(v) -> bool:
    fv = _num_from_any(v)
    return fv is not None and (-60 <= fv <= 60)


def _first_http_in_row(row: pd.Series):
    for v in row.values:
        if isinstance(v, str) and ("http://" in v or "https://" in v):
            return v.strip()
    return None


def _best_date_in_row(row: pd.Series):
    # pega a primeira data parseável que não seja URL
    for v in row.values:
        if isinstance(v, str) and ("http://" in v or "https://" in v):
            continue
        dt = pd.to_datetime(v, errors="coerce")
        if not pd.isna(dt):
            return dt
    return None


def _extract_hist_metrics(hist_df: pd.DataFrame):
    """
    Regra forte:
    - Max é o MAIOR número plausível de temperatura na linha
    - Min é o MENOR número plausível de temperatura na linha
    - Datas: usa colunas *_date se existirem e forem datas válidas;
             senão usa uma data "best effort" do registro para a que estiver faltando.
    """
    row = hist_df.iloc[0]

    # Source URL
    source_url = None
    for col in ["source_url", "information_source", "source", "url", "link", "Unnamed: 6"]:
        if col in hist_df.columns:
            v = row.get(col)
            if isinstance(v, str) and ("http://" in v or "https://" in v):
                source_url = v.strip()
                break
    if not source_url:
        source_url = _first_http_in_row(row)

    # Datas "caminho feliz"
    max_date = row.get("max_temp_date", None)
    min_date = row.get("min_temp_date", None)

    # Valida datas (se vier URL ou lixo, vira None)
    def valid_date(v):
        if isinstance(v, str) and ("http://" in v or "https://" in v):
            return None
        dt = pd.to_datetime(v, errors="coerce")
        return None if pd.isna(dt) else dt

    max_date_dt = valid_date(max_date)
    min_date_dt = valid_date(min_date)

    # Temperaturas: varre a linha e coleta números plausíveis
    # 1) caminho principal: usa as colunas certas (não varre a linha inteira)
    max_temp = _as_float(row.get("max_temp", None))
    min_temp = _as_float(row.get("min_temp", None))

    # normaliza "N/A" / vazio
    if max_temp is not None and not _is_temp(max_temp):
        max_temp = None
    if min_temp is not None and not _is_temp(min_temp):
        min_temp = None

    # 2) fallback: se faltar UM dos lados, tenta achar um candidato na linha
    #    mas sem deixar 1 único número preencher max e min ao mesmo tempo
    candidates = []
    for v in row.values:
        if isinstance(v, str) and ("http://" in v or "https://" in v):
            continue
        fv = _as_float(v)
        if fv is not None and _is_temp(fv):
            candidates.append(float(fv))

    candidates = sorted(set(candidates))

    if max_temp is None and candidates:
        max_temp = max(candidates)

    if min_temp is None:
        # se só tem 1 candidato e ele já foi usado como max, NÃO replica
        if len(candidates) >= 2:
            min_temp = min(candidates)
        else:
            min_temp = None

    # Fallback de datas: se uma das datas não existe, usa a melhor data do registro
    fallback_dt = _best_date_in_row(row)

    if max_date_dt is None:
        max_date_dt = fallback_dt
    if min_date_dt is None:
        # tenta uma data diferente do max (se tiver mais de uma)
        min_date_dt = fallback_dt

    return max_temp, max_date_dt, min_temp, min_date_dt, source_url


def _kpi_card_html(title: str, temp_val, date_val, date_label: str = "Date") -> str:
    date_txt = _fmt_date(date_val)

    # Se a data é inválida/sentinela, invalida o KPI inteiro
    if date_txt == "-":
        temp_txt = "-"
    else:
        temp_txt = "-"
        if temp_val is not None:
            temp_txt = f"{float(temp_val):.1f}".replace(".", ",") + "°C"


    return f"""
<div style="
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px 8px;
    background: rgba(255,255,255,0.02);
    width: 100%;
    min-height: 128px;
    box-sizing: border-box;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    color: #fff;
    text-align: center;
">
    <div style="
        font-size: 0.82rem;
        color: #e8eaed;
        font-weight: 700;
        margin-bottom: 8px;
    ">
        {title}
    </div>

    <div style="
        font-size: 2.15rem;
        font-weight: 850;
        line-height: 1.05;
        margin-bottom: 10px;
    ">
        {temp_txt}
    </div>

    <div>
        <span style="
            display:inline-block;
            padding: 4px 11px;
            border-radius: 999px;
            background: rgba(46, 204, 113, 0.18);
            border: 1px solid rgba(46, 204, 113, 0.35);
            color: #bff5d2;
            font-size: 0.76rem;
            white-space: nowrap;
        ">
            {date_label}: {date_txt}
        </span>
    </div>
</div>
"""

def short_domain(url: str) -> str:
    try:
        p = urlparse(url)
        host = p.netloc or url
        return host + "…"
    except Exception:
        return "Source…"

def first_source_url(df_):
    if df_ is None or len(df_) == 0:
        return None

    # tenta colunas conhecidas
    for col in ["source_url", "information_source", "Unnamed: 6"]:
        if col in df_.columns:
            s = df_[col].dropna().astype(str)

            # se vier lista "['url1','url2']" ou "url1, url2", pega a primeira URL dentro
            for v in s:
                if "http://" in v or "https://" in v:
                    # pega a primeira ocorrência de http(s) e corta no primeiro separador comum
                    start = v.find("http")
                    cand = v[start:]
                    for sep in ["',", '",', ",", " ", "]", ")"]:
                        if sep in cand:
                            cand = cand.split(sep, 1)[0]
                    return cand.strip().strip("'").strip('"')

    # fallback varrendo células
    for v in df_.astype(str).values.flatten():
        if "http://" in v or "https://" in v:
            start = v.find("http")
            cand = v[start:]
            for sep in ["',", '",', ",", " ", "]", ")"]:
                if sep in cand:
                    cand = cand.split(sep, 1)[0]
            return cand.strip().strip("'").strip('"')

    return None

def _short_host(url: str) -> str:
    try:
        host = (urlparse(url).netloc or "").replace("www.", "").strip()
        return host if host else url
    except Exception:
        return url

def all_source_urls(df_: pd.DataFrame) -> list[str]:
    """Extrai TODAS as URLs de um df (colunas conhecidas + varredura geral)."""
    if df_ is None or len(df_) == 0:
        return []

    urls = []

    # 1) colunas mais prováveis (se existirem)
    likely_cols = ["source_url", "information_source", "source", "url", "link", "Unnamed: 6"]
    for col in likely_cols:
        if col in df_.columns:
            for v in df_[col].dropna().astype(str).tolist():
                urls += _URL_RE.findall(v)

    # 2) fallback: varre TODAS as células
    flat = df_.astype(str).values.flatten().tolist()
    for v in flat:
        urls += _URL_RE.findall(v)

    # dedup preservando ordem
    out = []
    seen = set()
    for u in urls:
        u = u.strip().rstrip(".,;")
        if u and u not in seen:
            out.append(u)
            seen.add(u)
    return out

def render_sources_expander(urls: list[str], title: str = "Sources", align: str = "left"):
    """Mostra um 'objeto' (expander) que abre e lista links um abaixo do outro."""
    urls = [u for u in (urls or []) if isinstance(u, str) and u.strip()]
    if not urls:
        return

    with st.expander(f"ℹ️ {title} ({len(urls)})", expanded=False):
        for u in urls:
            host = _short_host(u)
            st.markdown(f"- [{host}]({u})")

def clamp01_to_100(x):
    try:
        x = float(x)
        if x < 0: x = 0
        if x > 100: x = 100
        return x
    except Exception:
        return 0.0

def radar_fig(title, axes, values):
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=axes + [axes[0]],
            fill="toself",
            hovertemplate="%{theta}: %{r:.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=20),   # 👈 t maior pra caber o título
        height=300,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color="rgba(255,255,255,0.55)", size=10),
                gridcolor="rgba(255,255,255,0.13)",
                linecolor="rgba(255,255,255,0.13)",
            ),
            angularaxis=dict(
                tickfont=dict(color="rgba(255,255,255,0.75)", size=10),
                gridcolor="rgba(255,255,255,0.13)",
                linecolor="rgba(255,255,255,0.13)",
                rotation=90,
            ),
        ),
        showlegend=False,
        annotations=[
            dict(
                text=title,
                x=0.0, y=1.15, xref="paper", yref="paper",  # 👈 sempre acima do chart
                xanchor="left", yanchor="top",
                showarrow=False,
                font=dict(size=13, color="rgba(255,255,255,0.70)")
            )
        ]
    )
    return fig

def duration_days(df_, start_col="date_start", end_col="date_end"):
    if df_ is None or len(df_) == 0:
        return None
    if start_col not in df_.columns:
        return None
    starts = pd.to_datetime(df_[start_col], errors="coerce")
    if end_col in df_.columns:
        ends = pd.to_datetime(df_[end_col], errors="coerce")
        d = (ends - starts).dt.days.dropna()
        if len(d) > 0:
            return float(d.max())
    return None


def _num_from_text_robust(v):
    """
    Extrai números de strings como:
    - "49,000 hectares" -> 49000
    - "1.2" -> 1.2
    - "1,2" -> 1.2
    - "€185 million" -> 185
    """
    if v is None:
        return None

    if isinstance(v, (int, float)):
        if isinstance(v, float) and pd.isna(v):
            return None
        return float(v)

    s = str(v).strip()
    if not s or s.lower() in {"nan", "none", "null", "n/a", "na", "-", "—", "not applicable", "not found"}:
        return None

    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", s)
    if not m:
        return None

    raw = m.group(0)

    # "49,000" deve ser 49000, mas "1,2" deve ser 1.2
    if "," in raw and "." not in raw:
        after = raw.split(",", 1)[1]
        raw = raw.replace(",", "") if len(after) == 3 else raw.replace(",", ".")
    elif "," in raw and "." in raw:
        raw = raw.replace(",", "")

    try:
        return float(raw)
    except Exception:
        return None


def _numeric_series_from_aliases(df_, aliases):
    if df_ is None or len(df_) == 0:
        return pd.Series(dtype="float64")

    found = []
    for col in aliases:
        if col in df_.columns:
            s = df_[col].apply(_num_from_text_robust)
            found.append(s)

    if not found:
        return pd.Series(dtype="float64")

    out = pd.concat(found, ignore_index=True)
    return pd.to_numeric(out, errors="coerce").dropna()


def _max_alias(df_, aliases):
    s = _numeric_series_from_aliases(df_, aliases)
    if len(s) == 0:
        return None
    return float(s.max())


def _safe_div_score(value, denominator):
    if value is None:
        return None
    return clamp01_to_100((float(value) / float(denominator)) * 100)


def _is_missing_like(v) -> bool:
    if v is None:
        return True

    try:
        if pd.isna(v):
            return True
    except Exception:
        pass

    s = str(v).strip()
    if not s:
        return True

    return s.lower() in {
        "nan", "none", "null", "n/a", "na", "-", "—",
        "not applicable", "not found", "no data", "unknown"
    }


def _row_text(row: pd.Series) -> str:
    vals = []
    for v in row.values:
        if not _is_missing_like(v):
            vals.append(str(v))
    return " | ".join(vals)


def _df_text(df_: pd.DataFrame | None) -> str:
    if df_ is None or len(df_) == 0:
        return ""
    return " ".join(_row_text(row) for _, row in df_.iterrows()).lower()


def _is_urlish(v) -> bool:
    s = str(v).lower()
    return "http://" in s or "https://" in s


def _is_unreliable_source_text(text: str) -> bool:
    t = (text or "").lower()
    return any(x in t for x in [
        "fandom.com",
        "hypotheticalhurricanes",
        "hypothetical hurricanes",
        "hypothetical"
    ])


def _filter_valid_event_rows(kind: str, df_: pd.DataFrame | None) -> tuple[pd.DataFrame, int]:
    """
    Mantém somente linhas que parecem ser eventos reais.
    - Remove linhas template/placeholder com N/A.
    - Para Storm, remove fontes Fandom/hypothetical do cálculo.
    """
    if df_ is None or len(df_) == 0:
        return pd.DataFrame(), 0

    d = df_.dropna(how="all").copy()
    if len(d) == 0:
        return pd.DataFrame(), 0

    keep_idx = []
    excluded = 0

    for idx, row in d.iterrows():
        txt = _row_text(row)

        if kind == "Storm" and _is_unreliable_source_text(txt):
            excluded += 1
            continue

        meaningful_non_url = []
        meaningful_numeric = []

        for v in row.values:
            if _is_missing_like(v) or _is_urlish(v):
                continue

            num = _num_from_text_robust(v)

            # número zero sozinho não prova evento; número positivo ajuda
            if num is not None:
                if abs(num) > 0:
                    meaningful_numeric.append(num)
                continue

            meaningful_non_url.append(str(v).strip())

        # Regra: precisa ter texto identificando o evento OU algum número positivo
        # e não pode ser só uma linha vazia/placeholder.
        if meaningful_non_url or meaningful_numeric:
            keep_idx.append(idx)

    return d.loc[keep_idx].copy(), excluded


def _count_events(df_):
    if df_ is None or len(df_) == 0:
        return 0

    d2 = df_.dropna(how="all")
    if len(d2) == 0:
        return 0

    if len(d2) == 1 and d2.isna().all(axis=1).iloc[0]:
        return 0

    return int(len(d2))


def _count_sources(df_: pd.DataFrame | None) -> int:
    return len(all_source_urls(df_))


def _scope_from_df(df_: pd.DataFrame | None, place_text: str) -> str:
    if df_ is None or len(df_) == 0:
        return "N/A"

    txt = _df_text(df_)
    parts = [p.strip().lower() for p in (place_text or "").split(",") if p.strip()]
    country = parts[0] if parts else ""
    city = parts[-1] if parts else ""

    if city and city in txt:
        return "City-specific"
    if country and country in txt:
        return "Country-level"
    return "Regional / unclear"


def _confidence_from_evidence(events: int, source_count: int, excluded: int = 0, evidence: str = "") -> str:
    ev = (evidence or "").lower()

    if "not applicable" in ev:
        return "High"
    if events <= 0:
        return "Low"
    if excluded > 0:
        return "Medium"
    if source_count >= 2:
        return "High"
    return "Medium"


def _fmt_score_value(v):
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    return clamp01_to_100(v)


def _basis_join(parts: list[str]) -> str:
    return "; ".join([p for p in parts if p]) or "No quantitative basis found"


def _risk_row(kind: str, cfg: dict, raw_df: pd.DataFrame | None, place_text: str) -> dict:
    valid_df, excluded = _filter_valid_event_rows(kind, raw_df)
    events = _count_events(valid_df)

    event_severity = None
    long_term_hazard = None
    human_impact = None
    basis = []
    evidence = "Found" if events > 0 else "Not found"

    if kind == "Heatwave":
        days = _max_alias(valid_df, ["consecutive_days", "duration_days", "days"])
        if days is None:
            days = duration_days(valid_df)

        event_severity = _safe_div_score(days, 30)
        if days is not None:
            basis.append(f"event duration: {days:g} days / 30")

        mortality = _max_alias(valid_df, ["mortality", "fatalities", "deaths", "excess_deaths"])
        human_impact = _safe_div_score(mortality, 3000)
        if mortality is not None:
            basis.append(f"reported mortality: {mortality:g} / 3000")

    elif kind == "Flood":
        water = _max_alias(valid_df, ["water_level_m", "water_depth_meters", "water_depth_m", "water_level_meters"])
        area = _max_alias(valid_df, ["area_affected_km2", "affected_area_km2", "flooded_area_km2"])
        rainfall = _max_alias(valid_df, ["rainfall_mm", "precipitation_mm", "rainfall_24h_mm", "precipitation_24h_mm"])
        days = duration_days(valid_df)

        candidates = []
        if water is not None:
            candidates.append((_safe_div_score(water, 3), f"water depth/level: {water:g} m / 3"))
        if area is not None:
            candidates.append((_safe_div_score(area, 500), f"affected area: {area:g} km² / 500"))
        if rainfall is not None:
            candidates.append((_safe_div_score(rainfall, 200), f"rainfall: {rainfall:g} mm / 200"))
        if days is not None:
            candidates.append((_safe_div_score(days, 30), f"event duration: {days:g} days / 30"))

        if candidates:
            event_severity, chosen_basis = max(candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(chosen_basis)

        fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
        displaced = _max_alias(valid_df, ["displaced", "displaced_people", "evacuated"])
        h_candidates = []
        if fatalities is not None:
            h_candidates.append((_safe_div_score(fatalities, 500), f"fatalities: {fatalities:g} / 500"))
        if displaced is not None:
            h_candidates.append((_safe_div_score(displaced, 50000), f"displaced/evacuated: {displaced:g} / 50000"))
        if h_candidates:
            human_impact, h_basis = max(h_candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(h_basis)

    elif kind == "Wildfire":
        burned_ha = _max_alias(valid_df, [
            "burned_area_ha",
            "area_burned_hectares",
            "burned_area_hectares",
            "area_burned_ha"
        ])
        burned_km2 = _max_alias(valid_df, ["burned_area_km2", "area_burned_km2"])
        days = duration_days(valid_df)

        candidates = []
        if burned_ha is not None:
            candidates.append((_safe_div_score(burned_ha, 50000), f"burned area: {burned_ha:g} ha / 50000"))
        if burned_km2 is not None:
            candidates.append((_safe_div_score(burned_km2, 500), f"burned area: {burned_km2:g} km² / 500"))
        if days is not None:
            candidates.append((_safe_div_score(days, 30), f"event duration: {days:g} days / 30"))

        if candidates:
            event_severity, chosen_basis = max(candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(chosen_basis)

        fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
        evacuated = _max_alias(valid_df, ["evacuated", "displaced", "displaced_people"])
        h_candidates = []
        if fatalities is not None:
            h_candidates.append((_safe_div_score(fatalities, 200), f"fatalities: {fatalities:g} / 200"))
        if evacuated is not None:
            h_candidates.append((_safe_div_score(evacuated, 50000), f"evacuated/displaced: {evacuated:g} / 50000"))
        if h_candidates:
            human_impact, h_basis = max(h_candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(h_basis)

    elif kind == "Storm":
        wind = _max_alias(valid_df, [
            "max_wind_kmh",
            "wind_gust_kmh",
            "max_gust_kmh",
            "max_sustained_wind_kmh",
            "maximum_wind_kmh"
        ])

        event_severity = _safe_div_score(wind, 150)
        if wind is not None:
            basis.append(f"wind speed/gust: {wind:g} km/h / 150")
        if excluded > 0:
            basis.append(f"{excluded} unreliable/hypothetical row(s) ignored")

        fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
        human_impact = _safe_div_score(fatalities, 100)
        if fatalities is not None:
            basis.append(f"fatalities: {fatalities:g} / 100")

    elif kind == "WinterStorm":
        snow = _max_alias(valid_df, ["snowfall_cm", "snow_depth_cm", "snow_cm"])
        ice = _max_alias(valid_df, ["ice_accumulation_mm", "ice_mm"])
        wind = _max_alias(valid_df, ["max_wind_kmh", "wind_gust_kmh", "max_gust_kmh"])
        days = duration_days(valid_df)

        candidates = []
        if snow is not None:
            candidates.append((_safe_div_score(snow, 100), f"snowfall/depth: {snow:g} cm / 100"))
        if ice is not None:
            candidates.append((_safe_div_score(ice, 30), f"ice accumulation: {ice:g} mm / 30"))
        if wind is not None:
            candidates.append((_safe_div_score(wind, 120), f"wind: {wind:g} km/h / 120"))
        if days is not None:
            candidates.append((_safe_div_score(days, 7), f"event duration: {days:g} days / 7"))

        if candidates:
            event_severity, chosen_basis = max(candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(chosen_basis)

        fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
        displaced = _max_alias(valid_df, ["displaced", "displaced_people", "evacuated"])
        h_candidates = []
        if fatalities is not None:
            h_candidates.append((_safe_div_score(fatalities, 100), f"fatalities: {fatalities:g} / 100"))
        if displaced is not None:
            h_candidates.append((_safe_div_score(displaced, 50000), f"displaced/evacuated: {displaced:g} / 50000"))
        if h_candidates:
            human_impact, h_basis = max(h_candidates, key=lambda x: x[0] if x[0] is not None else -1)
            basis.append(h_basis)

    elif kind == "Seismo":
        # Terremoto não é risco climático atual. Entra como risco estrutural/histórico.
        magnitude = _max_alias(valid_df, ["magnitude", "mag", "richter_magnitude"])
        long_term_hazard = _safe_div_score(magnitude, 8)
        event_severity = None

        if magnitude is not None:
            evidence = "Historical / long-term"
            basis.append(f"historical magnitude: {magnitude:g} / 8")

        fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
        human_impact = _safe_div_score(fatalities, 50000)
        if fatalities is not None:
            basis.append(f"reported fatalities: {fatalities:g} / 50000")

    elif kind == "Eruption":
        if events == 0:
            evidence = "Not applicable"
            basis.append("no local volcanic event/hazard identified in the selected data")
        else:
            vei = _max_alias(valid_df, ["vei"])
            column_km = _max_alias(valid_df, ["eruption_column_km"])
            volume = _max_alias(valid_df, ["ejected_material_volume_km3"])

            candidates = []
            if vei is not None:
                candidates.append((_safe_div_score(vei, 8), f"VEI: {vei:g} / 8"))
            if column_km is not None:
                candidates.append((_safe_div_score(column_km, 30), f"eruption column: {column_km:g} km / 30"))
            if volume is not None:
                candidates.append((_safe_div_score(volume, 10), f"ejected volume: {volume:g} km³ / 10"))

            if candidates:
                event_severity, chosen_basis = max(candidates, key=lambda x: x[0] if x[0] is not None else -1)
                basis.append(chosen_basis)

            fatalities = _max_alias(valid_df, ["fatalities", "deaths", "mortality"])
            displaced = _max_alias(valid_df, ["displaced_people", "displaced", "evacuated"])
            h_candidates = []
            if fatalities is not None:
                h_candidates.append((_safe_div_score(fatalities, 500), f"fatalities: {fatalities:g} / 500"))
            if displaced is not None:
                h_candidates.append((_safe_div_score(displaced, 50000), f"displaced/evacuated: {displaced:g} / 50000"))
            if h_candidates:
                human_impact, h_basis = max(h_candidates, key=lambda x: x[0] if x[0] is not None else -1)
                basis.append(h_basis)

    event_severity = _fmt_score_value(event_severity)
    long_term_hazard = _fmt_score_value(long_term_hazard)
    human_impact = _fmt_score_value(human_impact)

    score_candidates = [x for x in [event_severity, long_term_hazard] if x is not None]
    overall = max(score_candidates) if score_candidates else None

    source_count = _count_sources(valid_df)
    confidence = _confidence_from_evidence(events, source_count, excluded, evidence)
    scope = _scope_from_df(valid_df, place_text)

    return {
        "Hazard": cfg["label"],
        "Events": events,
        "Event Severity": event_severity,
        "Long-term Hazard": long_term_hazard,
        "Human Impact": human_impact,
        "Overall Estimate": overall,
        "Evidence": evidence,
        "Confidence": confidence,
        "Scope": scope,
        "Basis": _basis_join(basis),
    }


def build_risk_matrix(dfs_dis, place_text: str = ""):
    rows = []
    for h, cfg in HAZARD_CONFIG.items():
        rows.append(_risk_row(h, cfg, dfs_dis.get(h), place_text))
    return pd.DataFrame(rows)


def _score_txt(v):
    if v is None:
        return "N/A"
    try:
        if pd.isna(v):
            return "N/A"
    except Exception:
        pass
    return f"{int(round(float(v)))} / 100"


def _display_risk_df(risk_df: pd.DataFrame) -> pd.DataFrame:
    out = risk_df.copy()

    for col in ["Event Severity", "Long-term Hazard", "Human Impact", "Overall Estimate"]:
        if col in out.columns:
            out[col] = out[col].apply(_score_txt)

    if "Events" in out.columns:
        out["Events"] = pd.to_numeric(out["Events"], errors="coerce").fillna(0).astype(int)

    return out

def _translate_hazard_label(x: str) -> str:
    return {
        "Heatwave": tr("risk_hazard_heatwave"),
        "Flood / Heavy Rain": tr("risk_hazard_flood"),
        "Wildfire": tr("risk_hazard_wildfire"),
        "Storm / Severe Wind": tr("risk_hazard_storm"),
        "Winter Storm / Blizzard": tr("risk_hazard_winter"),
        "Earthquake": tr("risk_hazard_earthquake"),
        "Volcanic Risk": tr("risk_hazard_volcanic"),
    }.get(str(x), str(x))


def _translate_simple_value(x: str) -> str:
    return {
        "Found": tr("risk_found"),
        "Not found": tr("risk_not_found"),
        "Historical / long-term": tr("risk_historical_long_term"),
        "Not applicable": tr("risk_not_applicable"),
        "High": tr("risk_high"),
        "Medium": tr("risk_medium"),
        "Low": tr("risk_low"),
        "Country-level": tr("risk_country_level"),
        "City-specific": tr("risk_city_specific"),
        "Regional / unclear": tr("risk_regional_unclear"),
        "N/A": tr("risk_na"),
    }.get(str(x), str(x))


def _translate_basis_text(x: str) -> str:
    s = str(x)

    replacements = {
        "No quantitative basis found": tr("basis_no_quantitative"),
        "event duration:": tr("basis_event_duration"),
        "reported mortality:": tr("basis_reported_mortality"),
        "burned area:": tr("basis_burned_area"),
        "fatalities:": tr("basis_fatalities"),
        "wind speed/gust:": tr("basis_wind_speed"),
        "unreliable/hypothetical row(s) ignored": tr("basis_unreliable_rows"),
        "historical magnitude:": tr("basis_historical_magnitude"),
        "no local volcanic event/hazard identified in the selected data": tr("basis_no_local_volcanic"),
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    return s


def _translated_display_risk_df(risk_df: pd.DataFrame) -> pd.DataFrame:
    out = _display_risk_df(risk_df)

    if "Hazard" in out.columns:
        out["Hazard"] = out["Hazard"].apply(_translate_hazard_label)

    for col in ["Evidence", "Confidence", "Scope"]:
        if col in out.columns:
            out[col] = out[col].apply(_translate_simple_value)

    for col in ["Event Severity", "Long-term Hazard", "Human Impact", "Overall Estimate"]:
        if col in out.columns:
            out[col] = out[col].replace("N/A", tr("risk_na"))

    if "Basis" in out.columns:
        out["Basis"] = out["Basis"].apply(_translate_basis_text)

    return out.rename(columns={
        "Hazard": tr("risk_col_hazard"),
        "Events": tr("risk_col_events"),
        "Event Severity": tr("risk_col_event_severity"),
        "Long-term Hazard": tr("risk_col_long_term_hazard"),
        "Human Impact": tr("risk_col_human_impact"),
        "Overall Estimate": tr("risk_col_overall_estimate"),
        "Evidence": tr("risk_col_evidence"),
        "Confidence": tr("risk_col_confidence"),
        "Scope": tr("risk_col_scope"),
        "Basis": tr("risk_col_basis"),
    })

def _finalize_risk_table_df(display_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajusta a tabela final para exibição:
    - Eventos = 0  -> "-"
    - N/A / N/D    -> "-"
    """
    out = display_df.copy()

    events_col = tr("risk_col_events")

    # colunas onde N/A / N/D devem virar "-"
    replace_dash_cols = [
        tr("risk_col_events"),
        tr("risk_col_event_severity"),
        tr("risk_col_long_term_hazard"),
        tr("risk_col_human_impact"),
        tr("risk_col_overall_estimate"),
        tr("risk_col_evidence"),
        tr("risk_col_scope"),
    ]

    if events_col in out.columns:
        out[events_col] = out[events_col].apply(
            lambda x: "-" if str(x).strip() in {"0", "0.0"} else x
        )

    for col in replace_dash_cols:
        if col in out.columns:
            out[col] = out[col].replace({
                "N/A": "-",
                "N/D": "-",
                tr("risk_na"): "-",
                "Not found": "-",
                "Não encontrado": "-",
                "Não encontrada": "-",
                tr("risk_not_found"): "-",
            })

    return out

def _is_muted_table_value(v) -> bool:
    s = str(v).strip().lower()

    if s in {"-", "—", "", "n/a", "n/d"}:
        return True

    muted_phrases = [
        "sem base quantitativa encontrada",
        "no quantitative basis found",
        "nenhum evento/risco vulcânico local identificado nos dados selecionados",
        "no local volcanic event/hazard identified in the selected data",
        "não aplicável",
        "not applicable",
    ]

    return any(p in s for p in muted_phrases)


def render_risk_table_html(display_df: pd.DataFrame):
    """
    Renderiza a tabela de risco em HTML para não depender do tema claro do st.dataframe.
    """
    df_show = display_df.reset_index(drop=True).copy()

    header_html = "".join(
        f"<th>{html.escape(str(col))}</th>"
        for col in df_show.columns
    )

    rows_html = []

    basis_col = tr("risk_col_basis")

    for _, row in df_show.iterrows():
        cells = []

        for col in df_show.columns:
            value = row[col]
            text = html.escape(str(value))

            classes = []
            if _is_muted_table_value(value):
                classes.append("muted-cell")

            if col == basis_col:
                classes.append("basis-cell")

            class_attr = f' class="{" ".join(classes)}"' if classes else ""
            cells.append(f"<td{class_attr}>{text}</td>")

        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    table_html = f"""
    <div class="wtm-risk-table-wrap">
      <table class="wtm-risk-table">
        <thead>
          <tr>{header_html}</tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

def _style_risk_table(display_df: pd.DataFrame):
    """
    Estiliza a tabela final:
    - headers em negrito
    - placeholders "-" em cor discreta
    - textos de 'sem dado útil' também em cor discreta
    - sem index
    """
    df_show = display_df.reset_index(drop=True).copy()

    placeholder_values = {"-", "—", ""}

    def is_muted_value(v):
        s = str(v).strip().lower()

        if s in {x.lower() for x in placeholder_values}:
            return True

        muted_phrases = [
            "sem base quantitativa encontrada",
            "no quantitative basis found",
            "nenhum evento/risco vulcânico local identificado nos dados selecionados",
            "no local volcanic event/hazard identified in the selected data",
            "não aplicável",
            "not applicable",
        ]

        return any(p in s for p in muted_phrases)

    styler = df_show.style

    for col in df_show.columns:
        styler = styler.map(
            lambda v: (
                "color: rgba(255,255,255,0.58); font-weight: 400;"
                if is_muted_value(v)
                else "color: rgba(255,255,255,0.95); font-weight: 400;"
            ),
            subset=[col]
        )

    styler = styler.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("color", "rgba(255,255,255,0.78)"),
                    ("font-weight", "700"),
                ],
            }
        ],
        overwrite=False,
    )

    styler = styler.hide(axis="index")

    return styler

with main_panel:
    doc_name = place
    loading = st.empty()     # placeholder do spinner
    content = st.container() # conteúdo final

    # =========================
    # 1) COMPUTA TUDO NO SPINNER
    # =========================
    with loading:
        with st.spinner(tr("loading_place", place=doc_name)):
            df, name = cached_load_df_by_exact_name(doc_name)

            # Pré-carregamentos/variáveis do tab principal
            hist_df = None
            max_temp = max_date = min_temp = min_date = hist_source_url = None
            risk_df = None
            dfs_dis = {}
            src = None
            fig = None
            source_url = None
            df_plot = None

            if df is not None and doc_name == place:
                # Histórico (KPIs) — aqui só calcula; não renderiza UI
                hist_df, _ = cached_load_df_by_exact_name(f"{place} - Historic")
                if hist_df is not None and len(hist_df) > 0:
                    max_temp, max_date, min_temp, min_date, hist_source_url = _extract_hist_metrics(hist_df)

                # Desastres — aqui também só calcula; renderização fica abaixo, depois do loading
                docs = {
                    hazard_key: resolve_doc_by_suffixes(place, cfg["suffixes"])
                    for hazard_key, cfg in HAZARD_CONFIG.items()
                }

                dfs_dis = {}
                for k, exact in docs.items():
                    dfs_dis[k] = cached_load_df_by_exact_name(exact)[0] if exact else None

                risk_df = build_risk_matrix(dfs_dis, place)

                src = (
                    first_source_url(dfs_dis.get("Heatwave"))
                    or first_source_url(dfs_dis.get("Flood"))
                    or first_source_url(dfs_dis.get("Wildfire"))
                    or first_source_url(dfs_dis.get("Storm"))
                    or first_source_url(dfs_dis.get("WinterStorm"))
                    or first_source_url(dfs_dis.get("Seismo"))
                    or first_source_url(dfs_dis.get("Eruption"))
                )

                # Gráfico mensal
                if "Unnamed: 6" in df.columns:
                    unique_sources = df["Unnamed: 6"].dropna().unique()
                    if len(unique_sources) > 0:
                        source_url = unique_sources[0]
                    df = df.drop(columns=["Unnamed: 6"])

                # Date parsing robusto
                if "Year" in df.columns and "Month" in df.columns:
                    y = pd.to_numeric(df["Year"], errors="coerce")
                    m_num = pd.to_numeric(df["Month"], errors="coerce")

                    if m_num.isna().all():
                        m_str = df["Month"].astype(str).str.strip().str.lower()
                        month_map = {
                            "jan": 1, "january": 1, "janeiro": 1,
                            "feb": 2, "february": 2, "fevereiro": 2,
                            "mar": 3, "march": 3, "março": 3, "marco": 3,
                            "apr": 4, "april": 4, "abril": 4,
                            "may": 5, "maio": 5,
                            "jun": 6, "june": 6, "junho": 6,
                            "jul": 7, "july": 7, "julho": 7,
                            "aug": 8, "august": 8, "agosto": 8,
                            "sep": 9, "september": 9, "set": 9, "setembro": 9,
                            "oct": 10, "october": 10, "out": 10, "outubro": 10,
                            "nov": 11, "november": 11, "novembro": 11,
                            "dec": 12, "december": 12, "dez": 12, "dezembro": 12,
                        }
                        m = m_str.map(month_map)
                    else:
                        m = m_num

                    df["Date"] = pd.to_datetime(
                        dict(year=y, month=m, day=1),
                        errors="coerce"
                    )
                    df = df.dropna(subset=["Date"]).sort_values("Date")
                else:
                    df["Date"] = pd.NaT

                max_temp_label = tr("max_temp_label")
                min_temp_label = tr("min_temp_label")

                df_plot = df.rename(columns={
                    "max_temp": max_temp_label,
                    "min_temp": min_temp_label,
                })

                fig = px.line(
                    df_plot,
                    x="Date",
                    y=[max_temp_label, min_temp_label],
                    markers=True,
                    title=None,
                    labels={
                        "value": tr("temperature_label"),
                        "variable": tr("legend_label"),
                        "Date": tr("month_year_label"),
                    },
                )
                fig.update_layout(hovermode="x unified")
                fig.update_xaxes(tickformat="%m-%Y", dtick="M1")

                if "rain" in df.columns:
                    mask_rain = df["rain"].astype(str).str.upper().eq("X")
                    if mask_rain.any():
                        y_rain = df.loc[mask_rain, "max_temp"].astype(float) + 1
                        fig.add_scatter(
                            x=df.loc[mask_rain, "Date"],
                            y=y_rain,
                            mode="text",
                            text=["🌧️"] * mask_rain.sum(),
                            textposition="top center",
                            hovertemplate=f"{tr('rain_hover')}<extra></extra>",
                            showlegend=False,
                        )
                        fig.add_scatter(
                            x=[None],
                            y=[None],
                            mode="text",
                            text=["🌧️"],
                            name=tr("rain_label"),
                            showlegend=True,
                            hoverinfo="skip",
                        )

    # acabou de calcular tudo -> some com o spinner
    loading.empty()

    # Agora que os dados já carregaram, troca a sidebar para a versão completa
    render_analysis_sidebar(show_saved=True)

    # =========================
    # 2) RENDERIZA A UI FINAL
    # =========================
    with content:
        if df is None:
            st.info(tr("not_found", place=doc_name))
            st.stop()

        if doc_name == place:
            if hist_df is not None and len(hist_df) > 0:
                # fontes da primeira seção
                hist_sources = all_source_urls(hist_df)
                if not hist_sources and hist_source_url:
                    hist_sources = [hist_source_url]

                dis_sources = []
                for _k, _d in (dfs_dis or {}).items():
                    dis_sources += all_source_urls(_d)

                seen = set()
                dis_sources = [u for u in dis_sources if not (u in seen or seen.add(u))]
                if not dis_sources and src:
                    dis_sources = [src]


                # Linha 1: KPIs à esquerda, desastres à direita
                kpi_col, risk_col = st.columns([0.85, 4.15], gap="large")

                with kpi_col:
                    components.html(
                        _kpi_card_html(tr("historic_max"), max_temp, max_date, tr("date_label")),
                        height=138,
                    )
                    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
                    components.html(
                        _kpi_card_html(tr("historic_min"), min_temp, min_date, tr("date_label")),
                        height=138,
                    )

                with risk_col:
                    st.markdown(
                        f"""
                        <div class="wtm-risk-title">{tr("natural_disasters")}</div>
                        <div class="wtm-risk-rule"></div>
                        <div class="wtm-risk-subtitle">{tr("risk_chart_title")}</div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if risk_df is not None and len(risk_df) > 0:
                        chart_df = risk_df.copy()
                        chart_df["Overall Estimate"] = pd.to_numeric(
                            chart_df["Overall Estimate"],
                            errors="coerce"
                        )

                        chart_df_plot = (
                            chart_df.dropna(subset=["Overall Estimate"])
                            .sort_values("Overall Estimate", ascending=True)
                        )

                        chart_df_plot["Hazard"] = chart_df_plot["Hazard"].apply(_translate_hazard_label)

                        if len(chart_df_plot) > 0:
                            fig_risk = px.bar(
                                chart_df_plot,
                                x="Overall Estimate",
                                y="Hazard",
                                orientation="h",
                                title=None,
                                labels={
                                    "Overall Estimate": tr("risk_x_label"),
                                    "Hazard": "",
                                },
                                hover_data={
                                    "Events": True,
                                    "Evidence": True,
                                    "Confidence": True,
                                    "Scope": True,
                                    "Overall Estimate": ":.0f",
                                    "Basis": True,
                                },
                            )
                            fig_risk.update_traces(
                                marker_color="#0E598C",
                                marker_line_width=0,
                            )
                            fig_risk.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=8, r=8, t=8, b=42),
                                height=225,
                                showlegend=False,
                            )
                            fig_risk.update_xaxes(range=[0, 100])
                            fig_risk.update_xaxes(title_standoff=18)

                            fig_risk.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="#ffffff"),
                            )
                            fig_risk = apply_dark_plot_theme(fig_risk)
                            st.plotly_chart(fig_risk, use_container_width=True)

                        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

                        src_hist_col, src_dis_col = st.columns([1.25, 2.75], gap="medium")

                        with src_hist_col:
                            render_sources_expander(
                                hist_sources,
                                title=tr("hist_sources"),
                                align="left",
                            )

                        with src_dis_col:
                            render_sources_expander(
                                dis_sources,
                                title=tr("disasters_sources"),
                                align="right",
                            )

                # Linha 2: tabela em largura total
                if risk_df is not None and len(risk_df) > 0:
                    display_df = _translated_display_risk_df(risk_df)
                    display_df = _finalize_risk_table_df(display_df)
                    styled_df = _style_risk_table(display_df)

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <div style="
                            color: rgba(255,255,255,0.88);
                            font-size: 1.04rem;
                            line-height: 1.85;
                            font-weight: 500;
                            margin: 8px 0 14px 0;
                        ">
                            {tr("risk_caption")}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    ordered_cols = [
                        tr("risk_col_hazard"),
                        tr("risk_col_events"),
                        tr("risk_col_event_severity"),
                        tr("risk_col_long_term_hazard"),
                        tr("risk_col_human_impact"),
                        tr("risk_col_overall_estimate"),
                        tr("risk_col_evidence"),
                        tr("risk_col_confidence"),
                        tr("risk_col_scope"),
                        tr("risk_col_basis"),
                    ]

                    styled_df = _style_risk_table(display_df[ordered_cols])

                    render_risk_table_html(display_df[ordered_cols])

                    with st.expander(tr("risk_how_title"), expanded=False):
                        st.markdown(tr("risk_how_text"))

                st.divider()

            # ===== Gráfico mensal =====
            if fig is not None:
                st.markdown(
                    f"""
                    <div class="wtm-risk-title">{tr("monthly_chart_title")}</div>
                    <div class="wtm-risk-rule"></div>
                    """,
                    unsafe_allow_html=True,
                )

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff"),
                )
                fig = apply_dark_plot_theme(fig)
                st.plotly_chart(fig, use_container_width=True)

            # Sources do gráfico mensal
            climate_sources = []
            if df_plot is not None and "Unnamed: 6" in df_plot.columns:
                climate_sources = all_source_urls(df_plot)
            else:
                if source_url:
                    climate_sources = [source_url]
                else:
                    climate_sources = all_source_urls(df)

            render_sources_expander(climate_sources, title=tr("climate_chart_sources"), align="right")

        else:
            st.dataframe(df, use_container_width=True)
