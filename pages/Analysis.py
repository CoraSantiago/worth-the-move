import streamlit as st
import pandas as pd
import plotly.express as px
from urllib.parse import urlparse
import streamlit.components.v1 as components
import plotly.graph_objects as go
import re
from urllib.parse import urlparse
import streamlit as st
from noxus_kb import kb_list_documents, load_df_by_exact_name

_URL_RE = re.compile(r"https?://[^\s\]\)\"'>]+", re.IGNORECASE)

@st.cache_data(ttl=300)  # 5 min: reduz MUITO as chamadas
def _cached_kb_names(status="trained"):
    docs = kb_list_documents(status=status)
    return [((d.get("name") or "").strip()) for d in docs if (d.get("name") or "").strip()]

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






st.markdown("""
<style>
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
            
/* ✅ Força font-size no CONTROLE do select (fechado), sem mexer no menu */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div{
  font-size: 9px !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div *{
  font-size: inherit !important;
}
            
/* ✅ só o DROPDOWN (lista) do selectbox, sem mexer no resto */
ul[data-testid="stSelectboxVirtualDropdown"] *{
  font-size: 9px !important;
  line-height: 1.15 !important;
}

/* (opcional) reduz também a altura da linha pra caber mais itens */
ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"]{
  min-height: 32px !important;   /* antes era ~40 */
}
</style>
""", unsafe_allow_html=True)

# ✅ place precisa existir antes da sidebar (pra setar index do select)
place = (st.session_state.get("place") or "").strip()

# ✅ lista de docs precisa existir antes do selectbox
try:
    raw_names = _cached_kb_names(status="trained")
except Exception:
    raw_names = st.session_state.get("_kb_names_cache", [])

if raw_names:
    st.session_state["_kb_names_cache"] = raw_names

# ✅ nomes “base” (antes do " - ")
base_names = sorted(set([n.split(" - ")[0].strip() for n in raw_names if n and " - " in n]))

with st.sidebar:
    if base_names:
        choice = st.selectbox(
            "Browse saved analyses",
            base_names,
            index=base_names.index(place) if place in base_names else 0,
            key="sidebar_place_select",
        )
        if choice != place:
            st.session_state["place"] = choice
            st.rerun()

    st.markdown("### Check another place")

    # Botão voltar (volta pra tua Home / Check_another_place)
    if st.button("⬅    Back", use_container_width=True):
        st.switch_page("Check_another_place.py")  # ajuste o nome/path se necessário

    st.markdown("---")

    # (Opcional) seletor rápido pra trocar o place sem voltar
    # usa a mesma lista que você já usa na Home
    try:
        raw_names = _cached_kb_names(status="trained")
    except Exception:
        raw_names = st.session_state.get("_kb_names_cache", [])

    if raw_names:
        st.session_state["_kb_names_cache"] = raw_names

    base_names = sorted(set([n.split(" - ")[0].strip() for n in raw_names]))

place = (st.session_state.get("place") or "").strip()

if not place:
    st.warning("Nenhum local selecionado. Volte para a página inicial.")
    st.stop()

st.title(place)

tabs = st.tabs(["Climate"])

with tabs[0]:
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
        return "—"
    try:
        if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and not x.strip()):
            return "—"
        dt = pd.to_datetime(x, errors="coerce")
        if pd.isna(dt):
            return "—"
        return dt.strftime("%d-%m-%Y")
    except Exception:
        return "—"


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


def _kpi_card_html(title: str, temp_val, date_val) -> str:
    temp_txt = "—"
    if temp_val is not None:
        temp_txt = f"{int(temp_val) if float(temp_val).is_integer() else round(temp_val, 1)}°C"

    date_txt = _fmt_date(date_val)

    return f"""
    <div style="
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 12px 8px;
        background: rgba(255,255,255,0.02);
        width: 210px;                      /* 👈 menor */
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        color: #fff;
        text-align: center;                /* 👈 centraliza tudo */
    ">
        <div style="
            font-size: 0.85rem;
            color: #e8eaed;
            font-weight: 600;
            margin-bottom: 8px;
        ">
            {title}
        </div>

        <div style="
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 10px;
        ">
            {temp_txt}
        </div>

        <div>
            <span style="
                display:inline-block;
                padding: 4px 12px;
                border-radius: 999px;
                background: rgba(46, 204, 113, 0.18);
                border: 1px solid rgba(46, 204, 113, 0.35);
                color: #bff5d2;
                font-size: 0.8rem;
            ">
                Date: {date_txt}
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

def get_metrics_for_type(kind: str, dfs: dict):
    eq = st_ = hw = 0
    flood = wildfire = eruption = 0
    human = econ = infra = 0
    src = None

    if kind == "Seismo":
        d = dfs.get("Seismo")
        src = first_source_url(d)
        if d is not None and "magnitude" in d.columns:
            mag = pd.to_numeric(d["magnitude"], errors="coerce").dropna()
            if len(mag) > 0:
                eq = clamp01_to_100((float(mag.max()) / 8.0) * 100)

    elif kind == "Heatwave":
        d = dfs.get("Heatwave")
        src = first_source_url(d)

        days = None
        if d is not None and "consecutive_days" in d.columns:
            cd = pd.to_numeric(d["consecutive_days"], errors="coerce").dropna()
            if len(cd) > 0:
                days = float(cd.max())
        if days is None:
            days = duration_days(d)
        if days is not None:
            hw = clamp01_to_100((days / 30.0) * 100)

        if d is not None and "mortality" in d.columns:
            m = pd.to_numeric(d["mortality"], errors="coerce").dropna()
            if len(m) > 0:
                human = clamp01_to_100((float(m.max()) / 3000.0) * 100)

    elif kind == "Wildfire":
        d = dfs.get("Wildfire")
        src = first_source_url(d)

        # Hazard: área queimada / duração
        wf_h = 0.0
        if d is not None and "burned_area_ha" in d.columns:
            ba = pd.to_numeric(d["burned_area_ha"], errors="coerce").dropna()
            if len(ba) > 0:
                wf_h = clamp01_to_100((float(ba.max()) / 50_000.0) * 100)  # 50k ha ~ topo
        if wf_h == 0.0 and d is not None and "burned_area_km2" in d.columns:
            ba2 = pd.to_numeric(d["burned_area_km2"], errors="coerce").dropna()
            if len(ba2) > 0:
                wf_h = clamp01_to_100((float(ba2.max()) / 500.0) * 100)  # 500 km² ~ topo
        if wf_h == 0.0:
            days = duration_days(d)
            if days is not None:
                wf_h = clamp01_to_100((float(days) / 30.0) * 100)

        # Eu colocaria wildfire como "Heatwave" (hw) no radar Physical hazard
        wildfire = max(wildfire, wf_h)

        # Impact: evacuações / casas destruídas / fatalities / loss
        if d is not None and "evacuated" in d.columns:
            evac = pd.to_numeric(d["evacuated"], errors="coerce").dropna()
            if len(evac) > 0:
                human = max(human, clamp01_to_100((float(evac.max()) / 50_000.0) * 100))

        if d is not None and "homes_destroyed" in d.columns:
            homes = pd.to_numeric(d["homes_destroyed"], errors="coerce").dropna()
            if len(homes) > 0:
                infra = max(infra, clamp01_to_100((float(homes.max()) / 5_000.0) * 100))

        if d is not None and "fatalities" in d.columns:
            fat = pd.to_numeric(d["fatalities"], errors="coerce").dropna()
            if len(fat) > 0:
                human = max(human, clamp01_to_100((float(fat.max()) / 200.0) * 100))

        if d is not None and "economic_loss" in d.columns:
            loss = pd.to_numeric(d["economic_loss"], errors="coerce").dropna()
            if len(loss) > 0:
                econ = max(econ, clamp01_to_100((float(loss.max()) / 500_000_000.0) * 100))
                

    elif kind == "Flood":
        d = dfs.get("Flood")
        src = first_source_url(d)

        # Hazard: severidade por altura/nível d'água ou área inundada ou dias
        flood_h = 0.0
        if d is not None and "water_level_m" in d.columns:
            wl = pd.to_numeric(d["water_level_m"], errors="coerce").dropna()
            if len(wl) > 0:
                flood_h = clamp01_to_100((float(wl.max()) / 3.0) * 100)  # 3m ~ topo
        if flood_h == 0.0 and d is not None and "area_affected_km2" in d.columns:
            aa = pd.to_numeric(d["area_affected_km2"], errors="coerce").dropna()
            if len(aa) > 0:
                flood_h = clamp01_to_100((float(aa.max()) / 500.0) * 100)  # 500km² ~ topo
        if flood_h == 0.0:
            days = duration_days(d)  # usa date_start/date_end se existir
            if days is not None:
                flood_h = clamp01_to_100((float(days) / 30.0) * 100)

        # Coloca no slot "Storm" (st_) do radar Physical hazard
        flood = max(flood, flood_h)

        # Impact: fatalities / displaced / economic_loss (se tiver)
        if d is not None and "fatalities" in d.columns:
            fat = pd.to_numeric(d["fatalities"], errors="coerce").dropna()
            if len(fat) > 0:
                human = max(human, clamp01_to_100((float(fat.max()) / 500.0) * 100))

        if d is not None and "displaced" in d.columns:
            disp = pd.to_numeric(d["displaced"], errors="coerce").dropna()
            if len(disp) > 0:
                human = max(human, clamp01_to_100((float(disp.max()) / 50_000.0) * 100))

        if d is not None and "economic_loss" in d.columns:
            loss = pd.to_numeric(d["economic_loss"], errors="coerce").dropna()
            if len(loss) > 0:
                econ = max(econ, clamp01_to_100((float(loss.max()) / 500_000_000.0) * 100))

    elif kind == "Eruption":
        d = dfs.get("Eruption")
        src = first_source_url(d)

        # -------- Physical hazard (0–100)
        # Prioridade: VEI > coluna eruptiva > volume expelido
        er_h = 0.0

        if d is not None and "vei" in d.columns:
            vei = pd.to_numeric(d["vei"], errors="coerce").dropna()
            if len(vei) > 0:
                er_h = max(er_h, clamp01_to_100((float(vei.max()) / 8.0) * 100))  # VEI 0–8

        if d is not None and "eruption_column_km" in d.columns:
            col = pd.to_numeric(d["eruption_column_km"], errors="coerce").dropna()
            if len(col) > 0:
                er_h = max(er_h, clamp01_to_100((float(col.max()) / 30.0) * 100))  # 30 km ~ topo

        if d is not None and "ejected_material_volume_km3" in d.columns:
            vol = pd.to_numeric(d["ejected_material_volume_km3"], errors="coerce").dropna()
            if len(vol) > 0:
                er_h = max(er_h, clamp01_to_100((float(vol.max()) / 10.0) * 100))  # heurístico

        # Eu jogo eruption no "Earthquake" (eq) do teu radar de hazard
        eruption = max(eruption, er_h)

        # -------- Impact (0–100)
        if d is not None and "fatalities" in d.columns:
            fat = pd.to_numeric(d["fatalities"], errors="coerce").dropna()
            if len(fat) > 0:
                human = max(human, clamp01_to_100((float(fat.max()) / 500.0) * 100))

        if d is not None and "displaced_people" in d.columns:
            disp = pd.to_numeric(d["displaced_people"], errors="coerce").dropna()
            if len(disp) > 0:
                human = max(human, clamp01_to_100((float(disp.max()) / 50_000.0) * 100))

        if d is not None and "economic_loss" in d.columns:
            loss = pd.to_numeric(d["economic_loss"], errors="coerce").dropna()
            if len(loss) > 0:
                econ = max(econ, clamp01_to_100((float(loss.max()) / 500_000_000.0) * 100))
                

    elif kind == "Hurricane":
        d = dfs.get("Hurricane")
        src = first_source_url(d)

        if d is not None and "max_wind_kmh" in d.columns:
            w = pd.to_numeric(d["max_wind_kmh"], errors="coerce").dropna()
            if len(w) > 0:
                v = float(w.max())
                v_max = 250.0  # referência Cat 5 (~252 km/h)
                st_ = clamp01_to_100((v**3 / v_max**3) * 100)

        if d is not None and "fatalities" in d.columns:
            fat = pd.to_numeric(d["fatalities"], errors="coerce").dropna()
            if len(fat) > 0:
                human = clamp01_to_100((float(fat.max()) / 100.0) * 100)

    hazard_scores = [eq, st_, hw, flood, wildfire, eruption]
    impact_scores = [human, econ, infra]
    return hazard_scores, impact_scores, src

def _count_events(df_):
    if df_ is None or len(df_) == 0:
        return 0
    # conta linhas não totalmente vazias
    d2 = df_.dropna(how="all")
    # se vier 1 linha toda NaN, vira 0
    if len(d2) == 1 and d2.isna().all(axis=1).iloc[0]:
        return 0
    return int(len(d2))

def build_risk_matrix(dfs_dis):
    hazards = ["Seismo", "Hurricane", "Heatwave", "Flood", "Wildfire", "Eruption"]

    rows = []
    for h in hazards:
        hazard_scores, impact_scores, _ = get_metrics_for_type(h, dfs_dis)

        physical_map = {
            "Seismo": hazard_scores[0],
            "Hurricane": hazard_scores[1],
            "Heatwave": hazard_scores[2],
            "Flood": hazard_scores[3],
            "Wildfire": hazard_scores[4],
            "Eruption": hazard_scores[5],
        }

        df_h = dfs_dis.get(h)
        rows.append({
            "Tipo": h,
            "Events": _count_events(df_h),          # ✅ NOVO
            "Physical": physical_map[h],
            "Human (Mortality)": impact_scores[0],
        })

    return pd.DataFrame(rows)

with tabs[0]:
    doc_name = place
    loading = st.empty()     # placeholder do spinner
    content = st.container() # conteúdo final

    # =========================
    # 1) COMPUTA TUDO NO SPINNER
    # =========================
    with loading:
        with st.spinner(f"Carregando: {doc_name}..."):
            df, name = load_df_by_exact_name(doc_name)

            # Pré-carregamentos/variáveis do tab principal
            hist_df = None
            max_temp = max_date = min_temp = min_date = hist_source_url = None
            risk_df = None
            src = None
            fig = None
            source_url = None

            if df is not None and doc_name == place:
                # Histórico (KPIs)
                hist_df, _ = load_df_by_exact_name(f"{place} - Historic")
                if hist_df is not None and len(hist_df) > 0:
                    max_temp, max_date, min_temp, min_date, hist_source_url = _extract_hist_metrics(hist_df)

                # Desastres (tabela + radares)
                docs = {
                    "Seismo": resolve_doc_exact(place, "Seismo"),
                    "Heatwave":  resolve_doc_exact(place, "Heatwave"),
                    "Flood":   resolve_doc_exact(place, "Flood"),
                    "Hurricane":   resolve_doc_exact(place, "Hurricane"),
                    "Wildfire":   resolve_doc_exact(place, "Wildfire"),
                    "Eruption":   resolve_doc_exact(place, "Eruption"),

                }

                dfs_dis = {}
                for k, exact in docs.items():
                    dfs_dis[k] = load_df_by_exact_name(exact)[0] if exact else None

                # ✅ Constrói matriz final (Events + Physical + Mortality)
                risk_df = build_risk_matrix(dfs_dis)

                # ✅ Fonte principal
                src = (
                    first_source_url(dfs_dis.get("Seismo"))
                    or first_source_url(dfs_dis.get("Heatwave"))
                    or first_source_url(dfs_dis.get("Hurricane"))
                    or first_source_url(dfs_dis.get("Flood"))
                    or first_source_url(dfs_dis.get("Wildfire"))
                    or first_source_url(dfs_dis.get("Eruption"))
                )

                # Gráfico mensal (prepara a figura aqui também)
                if "Unnamed: 6" in df.columns:
                    unique_sources = df["Unnamed: 6"].dropna().unique()
                    if len(unique_sources) > 0:
                        source_url = unique_sources[0]
                    df = df.drop(columns=["Unnamed: 6"])

                # --- Date parsing robusto (não quebra se vier lixo) ---
                if "Year" in df.columns and "Month" in df.columns:
                    y = pd.to_numeric(df["Year"], errors="coerce")

                    # tenta mês numérico primeiro
                    m_num = pd.to_numeric(df["Month"], errors="coerce")

                    # se não for numérico, tenta mapear nomes/abreviações comuns
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

                    # monta a data sem explodir
                    df["Date"] = pd.to_datetime(
                        dict(year=y, month=m, day=1),
                        errors="coerce"
                    )

                    # remove linhas inválidas (que viraram NaT)
                    df = df.dropna(subset=["Date"]).sort_values("Date")
                else:
                    df["Date"] = pd.NaT

                df_plot = df.rename(columns={"max_temp": "Max Temp", "min_temp": "Min Temp"})

                fig = px.line(
                    df_plot,
                    x="Date",
                    y=["Max Temp", "Min Temp"],
                    markers=True,
                    title="Maximum & Minimum Temperatures - Last Year",
                    labels={"value": "Temperature (°C)", "variable": "Legend", "Date": "Month-Year"},
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
                            hovertemplate="Rain this month<extra></extra>",
                            showlegend=False,
                        )
                        fig.add_scatter(
                            x=[None],
                            y=[None],
                            mode="text",
                            text=["🌧️"],
                            name="Rain",
                            showlegend=True,
                            hoverinfo="skip",
                        )

    # acabou de calcular tudo -> some com o spinner
    loading.empty()

    # =========================
    # 2) SÓ AGORA RENDERIZA A UI
    # =========================
    with content:
        if df is None:
            st.info(f"Não encontrei: {doc_name}")
            st.stop()

        if doc_name == place:
            # ===== KPIs do Histórico =====
            if hist_df is not None and len(hist_df) > 0:
                left, right = st.columns([0.55, 2.45])

                # --- prepara sources ANTES (pra usar na linha de baixo)
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

                with left:
                    st.markdown("<div style='max-width:230px'></div>", unsafe_allow_html=True)
                    components.html(_kpi_card_html("Historical Max", max_temp, max_date), height=140)
                    st.write("")
                    components.html(_kpi_card_html("Historical Min", min_temp, min_date), height=140)

                    # ❌ REMOVE daqui:
                    # render_sources_expander(hist_sources, title="Historic sources", align="left")

                with right:
                    st.markdown("""
                        <div style="
                            display:flex;
                            align-items:flex-end;
                            justify-content:space-between;
                            margin: 2px 0 8px 0;
                        ">
                        <div style="font-size:1.35rem; font-weight:700; color:#ffffff;">
                            Natural Disasters <span style="font-weight:500; color:rgba(255,255,255,0.55);"></span>
                        </div>
                        </div>
                        <div style="height:1px; background:rgba(255,255,255,0.10); margin: 0 0 10px 0;"></div>
                    """, unsafe_allow_html=True)

                    if risk_df is not None and len(risk_df) > 0:
                        plot_df = risk_df.copy()
                        max_ev = max(1, plot_df["Events"].max())
                        plot_df["Events"] = (plot_df["Events"] / max_ev)

                        fig_heat = px.imshow(
                            plot_df.set_index("Tipo"),
                            aspect="auto",
                            text_auto=".0f"
                        )
                        fig_heat.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(l=10, r=10, t=30, b=10),
                            height=260,
                            coloraxis_colorbar=dict(title="Score"),
                        )
                        fig_heat.update_xaxes(side="top")
                        st.plotly_chart(fig_heat, use_container_width=True)

                    # ❌ REMOVE daqui:
                    # render_sources_expander(dis_sources, title="Disasters sources", align="right")

                # ✅ LINHA NOVA: SOURCES ALINHADAS NO MESMO Y
                left_s, right_s = st.columns([0.55, 2.45])

                with left_s:
                    render_sources_expander(hist_sources, title="Hist sources", align="left")

                with right_s:
                    render_sources_expander(dis_sources, title="Disasters sources", align="right")

                st.divider()

            # ===== Gráfico mensal =====
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)

            # Sources do gráfico mensal
            climate_sources = []
            if "Unnamed: 6" in df_plot.columns:
                climate_sources = all_source_urls(df_plot)
            else:
                # você já guardou um source_url antes de dropar a coluna
                if source_url:
                    climate_sources = [source_url]
                else:
                    climate_sources = all_source_urls(df)

            render_sources_expander(climate_sources, title="Climate chart sources", align="right")

        else:
            st.dataframe(df, use_container_width=True)
