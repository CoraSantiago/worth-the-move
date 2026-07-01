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
        "hist_sources": "Links — Temperature Records",
        "disasters_sources": "Links — Disaster Evidence",
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
        "choose_saved_analysis": "Choose a saved location",
        "risk_chart_title": "Risk estimate by hazard",
        "risk_x_label": "Calculated estimate (0–100)",
        "risk_caption": "Scores are calculated estimates. The table below shows the evidence status, scope and calculation basis used for each hazard.",
        "risk_how_title": "How to read these scores",
        "risk_how_text": """
        - **Events**: real count of valid rows/events found in the source tables. It is not normalized.
        - **Event Severity**: calculated from event-specific metrics such as heatwave duration, rainfall, wind speed or burned area.
        - **Long-term Hazard**: structural/historical exposure. Example: Lisbon earthquake risk belongs here, not as a current climate event.
        - **Human Impact**: calculated from fatalities, mortality, displaced or evacuated people when available.
        - **Overall Estimate**: the maximum between event severity and long-term hazard. It is a comparative product score, not a literal value from the source.
        - **Evidence / Confidence / Scope / Basis**: explains whether the score is supported by city-level data, country-level data, historical evidence, or limited evidence.
        """,

        "risk_col_hazard": "Hazard",
        "risk_col_events": "Events",
        "risk_col_event_severity": "Event Severity",
        "risk_col_long_term_hazard": "Long-term Hazard",
        "risk_col_human_impact": "Human Impact",
        "risk_col_overall_estimate": "Overall Estimate",
        "risk_col_evidence": "Evidence",
        "risk_col_confidence": "Confidence",
        "risk_col_scope": "Scope",
        "risk_col_basis": "Basis",

        "risk_hazard_heatwave": "Heatwave",
        "risk_hazard_flood": "Flood / Heavy Rain",
        "risk_hazard_wildfire": "Wildfire",
        "risk_hazard_storm": "Storm / Severe Wind",
        "risk_hazard_winter": "Winter Storm / Blizzard",
        "risk_hazard_earthquake": "Earthquake",
        "risk_hazard_volcanic": "Volcanic Risk",

        "risk_found": "Found",
        "risk_not_found": "Not found",
        "risk_historical_long_term": "Historical / long-term",
        "risk_not_applicable": "Not applicable",
        "risk_high": "High",
        "risk_medium": "Medium",
        "risk_low": "Low",
        "risk_country_level": "Country-level",
        "risk_city_specific": "City-specific",
        "risk_regional_unclear": "Regional / unclear",
        "risk_na": "N/A",

        "basis_no_quantitative": "No quantitative basis found",
        "basis_event_duration": "event duration:",
        "basis_reported_mortality": "reported mortality:",
        "basis_burned_area": "burned area:",
        "basis_fatalities": "fatalities:",
        "basis_wind_speed": "wind speed/gust:",
        "basis_unreliable_rows": "unreliable/hypothetical row(s) ignored",
        "basis_historical_magnitude": "historical magnitude:",
        "basis_no_local_volcanic": "no local volcanic event/hazard identified in the selected data",

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
        "historic_max": "Máxima Histórica",
        "historic_min": "Mínima Histórica",
        "natural_disasters": "Desastres Naturais",
        "hist_sources": "Links — Recordes de Temperatura",
        "disasters_sources": "Links — Evidências de Desastres",
        "climate_chart_sources": "Fontes do Gráfico Climático",
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
        "choose_saved_analysis": "Escolha um local já analisado",
        "risk_chart_title": "Estimativa de risco por ameaça",
        "risk_x_label": "Estimativa calculada (0–100)",
        "risk_caption": "As pontuações são estimativas calculadas. A tabela abaixo mostra o status da evidência, o escopo e a base de cálculo usada para cada ameaça.",
        "risk_how_title": "Como ler essas pontuações",
        "risk_how_text": """
        - **Eventos**: contagem real de linhas/eventos válidos encontrados nas tabelas de origem. Não é normalizada.
        - **Severidade do evento**: calculada a partir de métricas específicas, como duração de onda de calor, chuva, velocidade do vento ou área queimada.
        - **Risco estrutural**: exposição histórica ou estrutural. Exemplo: risco sísmico entra aqui, não como evento climático atual.
        - **Impacto humano**: calculado a partir de mortes, mortalidade, deslocados ou evacuados quando esses dados existem.
        - **Estimativa geral**: maior valor entre severidade do evento e risco estrutural. É uma pontuação comparativa do produto, não um valor literal da fonte.
        - **Evidência / Confiança / Escopo / Base**: explica se a pontuação vem de dados locais, nacionais, históricos ou de evidência limitada.
        """,

        "risk_col_hazard": "Ameaça",
        "risk_col_events": "Eventos",
        "risk_col_event_severity": "Severidade do evento",
        "risk_col_long_term_hazard": "Risco estrutural",
        "risk_col_human_impact": "Impacto humano",
        "risk_col_overall_estimate": "Estimativa geral",
        "risk_col_evidence": "Evidência",
        "risk_col_confidence": "Confiança",
        "risk_col_scope": "Escopo",
        "risk_col_basis": "Base do cálculo",

        "risk_hazard_heatwave": "Onda de calor",
        "risk_hazard_flood": "Inundação / chuva forte",
        "risk_hazard_wildfire": "Incêndio florestal",
        "risk_hazard_storm": "Tempestade / vento severo",
        "risk_hazard_winter": "Tempestade de inverno / nevasca",
        "risk_hazard_earthquake": "Terremoto",
        "risk_hazard_volcanic": "Risco vulcânico",

        "risk_found": "Encontrado",
        "risk_not_found": "Não encontrado",
        "risk_historical_long_term": "Histórico / estrutural",
        "risk_not_applicable": "Não aplicável",
        "risk_high": "Alta",
        "risk_medium": "Média",
        "risk_low": "Baixa",
        "risk_country_level": "Nível nacional",
        "risk_city_specific": "Específico da cidade",
        "risk_regional_unclear": "Regional / incerto",
        "risk_na": "N/D",

        "basis_no_quantitative": "Sem base quantitativa encontrada",
        "basis_event_duration": "duração do evento:",
        "basis_reported_mortality": "mortalidade reportada:",
        "basis_burned_area": "área queimada:",
        "basis_fatalities": "mortes:",
        "basis_wind_speed": "velocidade/rajada do vento:",
        "basis_unreliable_rows": "linha(s) não confiável(is)/hipotética(s) ignorada(s)",
        "basis_historical_magnitude": "magnitude histórica:",
        "basis_no_local_volcanic": "nenhum evento/risco vulcânico local identificado nos dados selecionados",
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
        "hist_sources": "Links — Recordes de Temperatura",
        "disasters_sources": "Links — Evidências de Desastres",
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
        "choose_saved_analysis": "Escolha um local já analisado",
        "risk_chart_title": "Estimativa de risco por ameaça",
        "risk_x_label": "Estimativa calculada (0–100)",
        "risk_caption": "As pontuações são estimativas calculadas. A tabela abaixo mostra o estado da evidência, o âmbito e a base de cálculo usada para cada ameaça.",
        "risk_how_title": "Como ler estas pontuações",
        "risk_how_text": """
        - **Eventos**: contagem real de linhas/eventos válidos encontrados nas tabelas de origem. Não é normalizada.
        - **Severidade do evento**: calculada a partir de métricas específicas, como duração de onda de calor, chuva, velocidade do vento ou área ardida.
        - **Risco estrutural**: exposição histórica ou estrutural. Exemplo: risco sísmico entra aqui, não como evento climático atual.
        - **Impacto humano**: calculado a partir de mortes, mortalidade, deslocados ou evacuados quando esses dados existem.
        - **Estimativa geral**: maior valor entre severidade do evento e risco estrutural. É uma pontuação comparativa do produto, não um valor literal da fonte.
        - **Evidência / Confiança / Âmbito / Base**: explica se a pontuação vem de dados locais, nacionais, históricos ou de evidência limitada.
        """,

        "risk_col_hazard": "Ameaça",
        "risk_col_events": "Eventos",
        "risk_col_event_severity": "Severidade do evento",
        "risk_col_long_term_hazard": "Risco estrutural",
        "risk_col_human_impact": "Impacto humano",
        "risk_col_overall_estimate": "Estimativa geral",
        "risk_col_evidence": "Evidência",
        "risk_col_confidence": "Confiança",
        "risk_col_scope": "Âmbito",
        "risk_col_basis": "Base do cálculo",

        "risk_hazard_heatwave": "Onda de calor",
        "risk_hazard_flood": "Inundação / chuva forte",
        "risk_hazard_wildfire": "Incêndio florestal",
        "risk_hazard_storm": "Tempestade / vento severo",
        "risk_hazard_winter": "Tempestade de inverno / nevão",
        "risk_hazard_earthquake": "Sismo",
        "risk_hazard_volcanic": "Risco vulcânico",

        "risk_found": "Encontrado",
        "risk_not_found": "Não encontrado",
        "risk_historical_long_term": "Histórico / estrutural",
        "risk_not_applicable": "Não aplicável",
        "risk_high": "Alta",
        "risk_medium": "Média",
        "risk_low": "Baixa",
        "risk_country_level": "Nível nacional",
        "risk_city_specific": "Específico da cidade",
        "risk_regional_unclear": "Regional / incerto",
        "risk_na": "N/D",

        "basis_no_quantitative": "Sem base quantitativa encontrada",
        "basis_event_duration": "duração do evento:",
        "basis_reported_mortality": "mortalidade reportada:",
        "basis_burned_area": "área ardida:",
        "basis_fatalities": "mortes:",
        "basis_wind_speed": "velocidade/rajada do vento:",
        "basis_unreliable_rows": "linha(s) não confiável(is)/hipotética(s) ignorada(s)",
        "basis_historical_magnitude": "magnitude histórica:",
        "basis_no_local_volcanic": "nenhum evento/risco vulcânico local identificado nos dados selecionados",
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
