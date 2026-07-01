import urllib.parse
import streamlit as st

TEXTS = {
    "en": {
        "home_title": "Worth the Move?",
        "home_subtitle": "So… where are you looking at?",
        "browse_saved": "Browse saved analyses",
        "missing_place": "Don’t see your place? Type it below.",
        "country_city": "Country, City",
        "place_placeholder": "Ex: Portugal, Maia",
        "search_data": "Search Data",
        "select_or_type_warning": "Select an analysis or type a place in the format Country, City.",
        "triggering_workflow": "Starting workflow...",
        "analysis_ready": "Your analysis is ready ✅ ({place})",
        "generating_analysis": "Generating analysis for **{place}**… This page will refresh automatically when it’s ready.",
        "taking_longer": "This is taking longer than expected. Please try again in a moment.",

        # Analysis page
        "no_place_selected": "No place selected. Go back to the home page.",
        "check_another_place": "Check another place",
        "back": "Back",
        "tab_climate": "Climate",
        "loading_place": "Loading: {place}...",
        "historic_max": "Historical Max",
        "historic_min": "Historical Min",
        "natural_disasters": "Natural Disasters",
        "hist_sources": "Historic sources",
        "disasters_sources": "Disasters sources",
        "climate_chart_sources": "Climate chart sources",
        "monthly_chart_title": "Maximum & Minimum Temperatures - Last Year",
        "temperature_label": "Temperature (°C)",
        "legend_label": "Legend",
        "month_year_label": "Month-Year",
        "rain_label": "Rain",
        "rain_hover": "Rain this month",
        "sources": "Sources",
        "not_found": "Not found: {place}",
        "date_label": "Date",
        "type_label": "Type",
        "events_col": "Events",
        "physical_col": "Physical",
        "human_mortality_col": "Human (Mortality)",
        "score_label": "Score",
        "max_temp_label": "Max Temp",
        "min_temp_label": "Min Temp",
        "disaster_seismo": "Seismo",
        "disaster_hurricane": "Hurricane",
        "disaster_heatwave": "Heatwave",
        "disaster_flood": "Flood",
        "disaster_wildfire": "Wildfire",
        "disaster_eruption": "Eruption",
    },
    "pt_br": {
        "home_title": "Vale a mudança?",
        "home_subtitle": "Então… você está olhando para onde?",
        "browse_saved": "Ver análises salvas",
        "missing_place": "Não encontrou seu lugar? Digite abaixo.",
        "country_city": "País, Cidade",
        "place_placeholder": "Ex: Portugal, Maia",
        "search_data": "Buscar dados",
        "select_or_type_warning": "Selecione uma análise ou digite um local no formato País, Cidade.",
        "triggering_workflow": "Acionando workflow...",
        "analysis_ready": "Sua análise está pronta ✅ ({place})",
        "generating_analysis": "Gerando análise para **{place}**… Esta página será atualizada automaticamente quando estiver pronta.",
        "taking_longer": "Está levando mais tempo do que o esperado. Tente novamente em alguns instantes.",

        # Página Analysis
        "no_place_selected": "Nenhum local selecionado. Volte para a página inicial.",
        "check_another_place": "Ver outro local",
        "back": "Voltar",
        "tab_climate": "Clima",
        "loading_place": "Carregando: {place}...",
        "historic_max": "Máxima histórica",
        "historic_min": "Mínima histórica",
        "natural_disasters": "Desastres naturais",
        "hist_sources": "Fontes históricas",
        "disasters_sources": "Fontes de desastres",
        "climate_chart_sources": "Fontes do gráfico climático",
        "monthly_chart_title": "Temperaturas máximas e mínimas - Último ano",
        "temperature_label": "Temperatura (°C)",
        "legend_label": "Legenda",
        "month_year_label": "Mês-Ano",
        "rain_label": "Chuva",
        "rain_hover": "Chuva neste mês",
        "sources": "Fontes",
        "not_found": "Não encontrei: {place}",
        "date_label": "Data",
        "type_label": "Tipo",
        "events_col": "Eventos",
        "physical_col": "Físico",
        "human_mortality_col": "Humano (mortalidade)",
        "score_label": "Pontuação",
        "max_temp_label": "Temp. máxima",
        "min_temp_label": "Temp. mínima",
        "disaster_seismo": "Sismo",
        "disaster_hurricane": "Furacão",
        "disaster_heatwave": "Onda de calor",
        "disaster_flood": "Inundação",
        "disaster_wildfire": "Incêndio florestal",
        "disaster_eruption": "Erupção",
    },
    "pt_pt": {
        "home_title": "Vale a pena mudar?",
        "home_subtitle": "Então… está a olhar para onde?",
        "browse_saved": "Ver análises guardadas",
        "missing_place": "Não encontra o seu local? Escreva abaixo.",
        "country_city": "País, Cidade",
        "place_placeholder": "Ex: Portugal, Maia",
        "search_data": "Pesquisar dados",
        "select_or_type_warning": "Selecione uma análise ou escreva um local no formato País, Cidade.",
        "triggering_workflow": "A iniciar workflow...",
        "analysis_ready": "A sua análise está pronta ✅ ({place})",
        "generating_analysis": "A gerar análise para **{place}**… Esta página será atualizada automaticamente quando estiver pronta.",
        "taking_longer": "Isto está a demorar mais do que o esperado. Tente novamente dentro de instantes.",

        # Página Analysis
        "no_place_selected": "Nenhum local selecionado. Volte para a página inicial.",
        "check_another_place": "Ver outro local",
        "back": "Voltar",
        "tab_climate": "Clima",
        "loading_place": "A carregar: {place}...",
        "historic_max": "Máxima histórica",
        "historic_min": "Mínima histórica",
        "natural_disasters": "Desastres naturais",
        "hist_sources": "Fontes históricas",
        "disasters_sources": "Fontes de desastres",
        "climate_chart_sources": "Fontes do gráfico climático",
        "monthly_chart_title": "Temperaturas máximas e mínimas - Último ano",
        "temperature_label": "Temperatura (°C)",
        "legend_label": "Legenda",
        "month_year_label": "Mês-Ano",
        "rain_label": "Chuva",
        "rain_hover": "Chuva neste mês",
        "sources": "Fontes",
        "not_found": "Não encontrei: {place}",
        "date_label": "Data",
        "type_label": "Tipo",
        "events_col": "Eventos",
        "physical_col": "Físico",
        "human_mortality_col": "Humano (mortalidade)",
        "score_label": "Pontuação",
        "max_temp_label": "Temp. máxima",
        "min_temp_label": "Temp. mínima",
        "disaster_seismo": "Sismo",
        "disaster_hurricane": "Furacão",
        "disaster_heatwave": "Onda de calor",
        "disaster_flood": "Inundação",
        "disaster_wildfire": "Incêndio florestal",
        "disaster_eruption": "Erupção",
    },
}


def init_language(default: str = "en") -> str:
    lang_from_url = st.query_params.get("lang")

    if isinstance(lang_from_url, list):
        lang_from_url = lang_from_url[0]

    if lang_from_url in TEXTS:
        st.session_state["lang"] = lang_from_url

    if st.session_state.get("lang") not in TEXTS:
        st.session_state["lang"] = default

    return st.session_state["lang"]


def tr(key: str, **kwargs) -> str:
    lang = init_language()
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))

    if kwargs:
        return text.format(**kwargs)

    return text


def render_language_buttons(
    component_key: str = "lang_switcher",
    extra_params: dict | None = None,
) -> None:
    current = init_language()

    def build_params() -> dict:
        params = {}

        for k, v in dict(st.query_params).items():
            if isinstance(v, list):
                v = v[0] if v else ""

            if v is not None and str(v).strip():
                params[k] = str(v)

        if extra_params:
            for k, v in extra_params.items():
                if v is None or str(v).strip() == "":
                    params.pop(k, None)
                else:
                    params[k] = str(v)

        return params

    def url_for(lang: str) -> str:
        params = build_params()
        params["lang"] = lang
        return "?" + urllib.parse.urlencode(params)

    url_en = url_for("en")
    url_pt_br = url_for("pt_br")
    url_pt_pt = url_for("pt_pt")

    active_en = "active" if current == "en" else ""
    active_pt_br = "active" if current == "pt_br" else ""
    active_pt_pt = "active" if current == "pt_pt" else ""

    st.markdown(
        f"""
        <style>
        .wtm-lang-slot {{
            height: 42px;
        }}

        .wtm-lang-wrap {{
            position: fixed;
            top: 84px;
            left: 50%;
            transform: translateX(-50%);
            width: min(880px, calc(100vw - 48px));

            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 8px;

            margin: 0;
            padding: 0;
            box-sizing: border-box;
            z-index: 999999;
            pointer-events: none;
        }}

        .wtm-lang-wrap a {{
            height: 32px;
            min-width: 68px;
            padding: 0 14px;

            display: inline-flex;
            align-items: center;
            justify-content: center;

            border-radius: 999px;
            border: 1px solid rgba(122, 214, 201, 0.35);

            background: rgba(255, 255, 255, 0.035);
            color: rgba(255, 255, 255, 0.82);

            font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
            font-weight: 700;
            line-height: 1;
            white-space: nowrap;
            text-decoration: none !important;

            box-shadow: none;
            transition: all 0.18s ease;
            pointer-events: auto;
        }}

        .wtm-lang-wrap a:hover {{
            background: rgba(122, 214, 201, 0.14);
            border-color: rgba(122, 214, 201, 0.72);
            color: white;
            text-decoration: none !important;
            transform: translateY(-1px);
        }}

        .wtm-lang-wrap a.active {{
            background: #2c8f86;
            border-color: #7ad6c9;
            color: white;
        }}
        </style>

        <div class="wtm-lang-slot">
            <div class="wtm-lang-wrap">
                <a class="{active_en}" href="{url_en}" target="_self">EN</a>
                <a class="{active_pt_br}" href="{url_pt_br}" target="_self">PT-BR</a>
                <a class="{active_pt_pt}" href="{url_pt_pt}" target="_self">PT-PT</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )