import streamlit as st
import time
import urllib.parse
import streamlit.components.v1 as components

from noxus_workflow import trigger_workflow
from noxus_kb import load_df_by_base_name, kb_list_documents

st.set_page_config(
    page_title="Worth the Move?",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ✅ CSS COMPLETO logo no início (pra não dar “flash” e não quebrar layout)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.block-container { max-width: 880px; padding-top: 3rem; }

/* some com nav/sidebar/header/footer */
div[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
header, footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

.stApp {
  background: radial-gradient(circle at 50% 0%, #0c1f28 0%, #08141c 40%, #050c14 100%);
}

.hero { text-align: center; margin-top: 2rem; margin-bottom: 1.5rem; }
.hero h1 {
  font-family: 'DM Serif Display', serif;
  font-size: 4.5rem;
  font-weight: 400;
  letter-spacing: -1px;
  margin: 0;
  color: #7ad6c9;
}
.hero p { margin-top: 1rem; font-size: 1.2rem; opacity: 0.8; }

div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div[role="combobox"] {
  border-radius: 12px;
  min-height: 56px;
  font-size: 1.05rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(122,214,201,0.25);
  transition: all 0.2s ease;
}
div[data-testid="stTextInput"] input:focus {
  border: 1px solid #7ad6c9;
  box-shadow: 0 0 0 1px #7ad6c9;
}

div[data-testid="stMarkdownContainer"] p { margin-bottom: 2px; }

div[data-testid="stButton"] button {
  border-radius: 14px;
  height: 52px;
  min-width: 150px;
  padding: 0 28px;
  font-size: 1.05rem;
  font-weight: 500;
  background: linear-gradient(135deg, #1e6f68, #2c8f86);
  color: white;
  border: none;
  transition: all 0.25s ease;
  display: block;
  margin: 0 auto;
}
div[data-testid="stButton"] button:hover {
  background: linear-gradient(135deg, #239c92, #35b3a8);
  transform: translateY(-1px);
}
div[data-testid="stButton"] button:active {
  transform: translateY(0px);
  opacity: 0.9;
}

div[data-testid="stAlert"] { border-radius: 10px; }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

.center-row {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-top: 10px;
}

hr {
  border: 0;
  height: 1px;
  background: rgba(255,255,255,0.10);
  margin: 18px 0 22px 0;
}

.card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(122,214,201,0.20);
  border-radius: 16px;
  padding: 16px 16px 6px 16px;
  margin-top: 8px;
}

/* deixa o expander mais limpo e sem "sobras" internas */
div[data-testid="stExpander"] details {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid rgba(122,214,201,0.20) !important;
  border-radius: 16px !important;
}

div[data-testid="stExpander"] summary {
  font-weight: 600;
}   

div[data-testid="stButton"] button:disabled {
  opacity: 0.45 !important;
  cursor: not-allowed !important;
  transform: none !important;
}      

/* ===== FORCE DARK SELECTBOX (BaseWeb) ===== */

/* Caixa fechada (o input/select em si) */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.06) !important;
  color: #ffffff !important;
  border: 1px solid rgba(122,214,201,0.25) !important;
  border-radius: 12px !important;
}

/* Texto / placeholder / ícones internos */
div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
  color: #ffffff !important;
}

/* Menu (dropdown) quando abre */
ul[data-testid="stSelectboxVirtualDropdown"] {
  background: #08141c !important;
  border: 1px solid rgba(122,214,201,0.25) !important;
}

/* Cada item do dropdown */
ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"] {
  background: #08141c !important;
  color: #ffffff !important;
}

/* Hover do item */
ul[data-testid="stSelectboxVirtualDropdown"] li[role="option"]:hover {
  background: rgba(122,214,201,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HERO
# ======================
st.markdown(
    """
    <div class="hero">
      <h1>Worth the Move?</h1>
      <p>So… where are you looking at?</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr/>", unsafe_allow_html=True)

# ======================
# STATE
# ======================
if "selected_analysis" not in st.session_state:
    st.session_state.selected_analysis = ""
if "typed_place" not in st.session_state:
    st.session_state.typed_place = ""
if "search_locked" not in st.session_state:
    st.session_state.search_locked = False

import time

if "pending" not in st.session_state:
    st.session_state.pending = False
    st.session_state.search_locked = False
if "pending_place" not in st.session_state:
    st.session_state.pending_place = ""
if "pending_started" not in st.session_state:
    st.session_state.pending_started = 0.0
if "pending_run_id" not in st.session_state:
    st.session_state.pending_run_id = ""
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

# >>> NOVO
if "pending_snapshot" not in st.session_state:
    st.session_state.pending_snapshot = set()
# ======================
# 1) SELECT: ANÁLISES DISPONÍVEIS
# ======================
docs = kb_list_documents(status="trained")

raw_names = [
    (d.get("name") or "").strip()
    for d in docs
    if (d.get("name") or "").strip()
]

# pega só a parte antes de " - "
def pretty_base(name: str) -> str:
    # remove extensão comum
    for ext in (".json", ".csv", ".png"):
        if name.lower().endswith(ext):
            name = name[: -len(ext)]
            break
    # volta "__" / "_" para ", " (só no display)
    name = name.replace("__", ", ").replace("_", " ")
    name = " ".join(name.split())
    return name.strip()

base_names = [pretty_base(name.split(" - ")[0].strip()) for name in raw_names]

# remove duplicados e ordena
names = ["— Selecione —"] + sorted(set(base_names))

def go_to_analysis():
    place = (st.session_state.get("selected_analysis") or "").strip()
    if not place:
        return
    st.session_state["place"] = place
    st.switch_page("pages/Analysis.py")

def on_pick_saved():
    place = (st.session_state.get("selected_analysis") or "").strip()
    if not place or place == "— Selecione —":
        return
    st.session_state["go_analysis"] = True
    st.session_state["place"] = place

chosen = st.selectbox(
    "Browse saved analyses",
    options=names,
    index=0,
    key="selected_analysis",
    on_change=on_pick_saved,
)

typed = (st.session_state.get("typed_place") or "").strip()
if "\n" in typed or len(typed) > 80:
    typed = ""

active_place = typed or (chosen or "").strip()

if st.session_state.get("go_analysis"):
    st.session_state["go_analysis"] = False
    st.switch_page("pages/Analysis.py")
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)


# ======================
# 2) INPUT: NOVO LOCAL
# ======================
# ======================
# 2) INPUT: NOVO LOCAL (OCULTO ATÉ CLICAR)
# ======================
# --- lê o valor enviado pelo HTML (se existir)
qp = st.query_params

if "typed_place" in qp:
    st.session_state["typed_place"] = qp["typed_place"]
else:
    st.session_state["typed_place"] = ""

buscar_dados = (qp.get("do_search") == "1")
# ======================
# 2) INPUT: NOVO LOCAL (OCULTO ATÉ CLICAR)
# ======================

with st.expander("Don’t see your place? Type it below.", expanded=False):
    st.markdown("**Country, City**")

    components.html(
      """
      <div style="display:flex; flex-direction:column; gap:12px;">
        <input
          id="typed_place_html"
          type="text"
          placeholder="Ex: Portugal, Maia"
          autocomplete="off"
          autocapitalize="off"
          autocorrect="off"
          spellcheck="false"
          style="
            width: 100%;
            border-radius: 12px;
            min-height: 56px;
            font-size: 1.05rem;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(122,214,201,0.25);
            padding: 0 14px;
            color: white;
            outline: none;
            box-sizing: border-box;
          "
        />
      </div>

      <script>
        const inp = document.getElementById("typed_place_html");
        const KEY = "wtm_typed_place";

        const prev = window.localStorage.getItem(KEY);
        if (prev && !inp.value) inp.value = prev;

        function setQueryParam(val) {
          try {
            const p = window.parent; // <<<<<< AQUI é a diferença
            const url = new URL(p.location.href);

            if (val) url.searchParams.set("typed_place", val);
            else url.searchParams.delete("typed_place");

            p.history.replaceState({}, "", url.toString());
          } catch (e) {
            // fallback: não quebra se o browser bloquear
            console.log("Could not set parent query param", e);
          }
        }

        // seta a URL externa ao carregar
        setQueryParam((inp.value || "").trim());

        inp.addEventListener("input", () => {
          const val = (inp.value || "").trim();
          window.localStorage.setItem(KEY, val);
          setQueryParam(val);
        });
      </script>
      """,
      height=90,
  )

    # botão REAL do streamlit (vai funcionar sempre)
    buscar_dados = st.button(
    "Search Data",
    key="search_data_btn",
    use_container_width=True,
    disabled=bool(st.session_state.get("pending") or st.session_state.get("search_locked")),
)

# pega o valor salvo no localStorage via um "fallback" manual:
# (como Python não lê localStorage, você pede o valor do session_state se existir)
typed = (st.session_state.get("typed_place") or "").strip()
active_place = typed or (chosen or "").strip()
# ======================
# ACTIONS
# ======================

# 1) Clique: só trava e rerun (NÃO chama API aqui)
if buscar_dados:
    if st.session_state.get("search_locked") or st.session_state.get("pending"):
        st.stop()
    st.session_state.search_locked = True
    st.rerun()

# 2) Segunda passada: já travado, agora chama API 1x e entra em pending
if st.session_state.get("search_locked") and not st.session_state.get("pending"):
    if not active_place:
        st.session_state.search_locked = False
        st.warning("Selecione uma análise ou digite um local no formato País, Cidade.")
        st.stop()

    # snapshot do que já existe treinado AGORA
    try:
        docs0 = kb_list_documents(status="trained")
        raw0 = [(d.get("name") or "").strip() for d in docs0 if (d.get("name") or "").strip()]
        st.session_state.pending_snapshot = set(raw0)
    except Exception:
        st.session_state.pending_snapshot = set()

    with st.spinner("Acionando workflow..."):
        run_id = trigger_workflow(active_place)

    st.session_state.pending = True
    st.session_state.pending_place = active_place
    st.session_state.pending_started = time.time()
    st.session_state.pending_run_id = run_id or ""

    # mantém locked enquanto pending estiver ativo
    st.rerun()

if st.session_state.get("search_locked") and not st.session_state.get("pending"):
    if not active_place:
        st.session_state.search_locked = False
        st.warning("Selecione uma análise ou digite um local no formato País, Cidade.")
        st.stop()

    # snapshot
    try:
        docs0 = kb_list_documents(status="trained")
        raw0 = [(d.get("name") or "").strip() for d in docs0 if (d.get("name") or "").strip()]
        st.session_state.pending_snapshot = set(raw0)
    except Exception:
        st.session_state.pending_snapshot = set()

    with st.spinner("Acionando workflow..."):
        run_id = trigger_workflow(active_place)

    st.session_state.pending = True
    st.session_state.pending_place = active_place
    st.session_state.pending_started = time.time()
    st.session_state.pending_run_id = run_id or ""

    # mantém locked enquanto pending estiver ativo
    time.sleep(0.2)
    st.rerun()
# ======================
# AUTO-REFRESH: esperar aparecer na KB e carregar automaticamente
# ======================
if st.session_state.analysis_ready:
    base_pending = st.session_state.pending_place.split(" - ")[0].strip()

    st.success(f"Your analysis is ready ✅ ({base_pending})")

    # Aqui você decide:
    # A) Ir direto pra página
    st.session_state.analysis_ready = False
    st.session_state.pending = False
    st.session_state.search_locked = False
    st.session_state["place"] = base_pending
    st.switch_page("pages/Analysis.py")

    # ou B) só recarregar a home
    # st.session_state.analysis_ready = False
    # st.session_state.pending = False
    # st.rerun()
    
if st.session_state.pending:
    pending_place = (st.session_state.pending_place or "").strip()
    base_pending = pending_place.split(" - ")[0].strip()

    REFRESH_EVERY_SECONDS = 3
    TIMEOUT_SECONDS = 180  # sugiro 3 min

    elapsed = time.time() - float(st.session_state.pending_started or 0.0)

    # ✅ área dedicada (não “some” e não fica silencioso)
    box = st.container()
    with box:
        st.info(f"Generating analysis for **{base_pending}**… This page will refresh automatically when it’s ready.")
        if st.session_state.pending_run_id:
            st.caption(f"run_id: {st.session_state.pending_run_id}")

        prog = min(0.95, elapsed / TIMEOUT_SECONDS)  # não chega em 100% até concluir
        st.progress(prog)

        cancel = False
        force = False

    if cancel:
        st.session_state.pending = False
        st.session_state.search_locked = False   # <<< adiciona
        st.session_state.pending_place = ""
        st.session_state.pending_started = 0.0
        st.session_state.pending_run_id = ""
        st.rerun()

    if elapsed > TIMEOUT_SECONDS:
        st.warning("This is taking longer than expected. Please try again in a moment.")
        st.session_state.pending = False
        st.session_state.search_locked = False
        st.session_state.pending_place = ""
        st.session_state.pending_started = 0.0
        st.session_state.pending_run_id = ""
        st.stop()

    # ✅ checa se apareceu na KB (status trained)
    ready = False
    try:
        docs_now = kb_list_documents(status="trained")
        raw_now = [(d.get("name") or "").strip() for d in docs_now if (d.get("name") or "").strip()]

        # documentos novos desde o clique
        new_docs = set(raw_now) - set(st.session_state.pending_snapshot or set())

        # pega base dos novos documentos
        new_bases = {n.split(" - ")[0].strip() for n in new_docs}

        ready = base_pending in new_bases

    except Exception:
        ready = False

    if ready:
      st.session_state.analysis_ready = True
      st.rerun()

        # (B) ou mandar direto pra página de Analysis:
        # st.session_state["place"] = base_pending
        # st.switch_page("pages/Analysis.py")

    # auto refresh
    if force:
        st.rerun()

    time.sleep(REFRESH_EVERY_SECONDS)
    st.rerun()


