import re
import os
from datetime import datetime, date
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

def load_logo_image():
    if os.path.exists("assets/logo.png"):
        try:
            img = Image.open("assets/logo.png")
            return img
        except Exception:
            return None
    return None

logo_img = load_logo_image()

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Dashboard de Performance de Vídeo - Meta Ads",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling - Manual 2026 Visual Identity (80% Black, 15% White, 5% Accents)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Montserrat', -apple-system, sans-serif !important;
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 96% !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
    }

    p, span, label, div {
        color: #e4e4e7;
    }

    .metric-card {
        background-color: #121215;
        border: 1px solid #27272a;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #a1a1aa !important;
        font-weight: 600 !important;
    }

    /* Status Color-Scale Tags (Kept intact with dark theme high contrast) */
    .evaluation-tag-excellent {
        background-color: rgba(34, 197, 94, 0.18);
        color: #4ade80;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.95rem;
        border: 1px solid #22c55e;
    }
    .evaluation-tag-good {
        background-color: rgba(234, 179, 8, 0.18);
        color: #fde047;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.95rem;
        border: 1px solid #eab308;
    }
    .evaluation-tag-better {
        background-color: rgba(239, 68, 68, 0.18);
        color: #fca5a5;
        font-weight: 700;
        padding: 6px 14px;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.95rem;
        border: 1px solid #ef4444;
    }

    .insight-card {
        background-color: #121215;
        border: 1px solid #27272a;
        border-left-width: 5px !important;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .insight-card p, .insight-card div, .insight-card span, .insight-card strong, .insight-card li {
        color: #FFFFFF !important;
    }
    .insight-card a {
        font-weight: 700;
        text-decoration: underline;
        color: #28FFFF !important;
    }

    .quadrant-box {
        background-color: #121215;
        border-radius: 8px;
        padding: 14px 18px;
        border: 1px solid #27272a;
        color: #FFFFFF;
        font-size: 0.9rem;
    }
    .quadrant-box strong, .quadrant-box em {
        color: #FFFFFF !important;
    }

    /* Streamlit Sidebar Dark Theme */
    [data-testid="stSidebar"] {
        background-color: #09090b !important;
        border-right: 1px solid #27272a;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        color: #a1a1aa !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    button[aria-selected="true"] {
        color: #C8FF28 !important;
        border-bottom-color: #C8FF28 !important;
    }

    /* Expander Dark Styling */
    [data-testid="stExpander"] {
        background-color: #121215 !important;
        border: 1px solid #27272a !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Month map for Portuguese date parsing
MONTH_MAP = {
    'jan': 1, 'janeiro': 1,
    'fev': 2, 'fevereiro': 2,
    'mar': 3, 'março': 3, 'marco': 3,
    'abr': 4, 'abril': 4,
    'mai': 5, 'maio': 5,
    'jun': 6, 'junho': 6,
    'jul': 7, 'julho': 7,
    'ago': 8, 'agosto': 8,
    'set': 9, 'setembro': 9,
    'out': 10, 'outubro': 10,
    'nov': 11, 'novembro': 11,
    'dez': 12, 'dezembro': 12
}

def clean_currency(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    s = re.sub(r'[^\d,.-]', '', s)
    if not s:
        return 0.0
    if '.' in s and ',' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

def clean_numeric(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = re.sub(r'[^\d.-]', '', str(val).replace(',', '.'))
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_pt_date(date_str):
    if pd.isna(date_str) or not str(date_str).strip():
        return date.today()
    s = str(date_str).strip().lower()
    
    try:
        dt = pd.to_datetime(s, dayfirst=True)
        if not pd.isna(dt):
            return dt.date()
    except Exception:
        pass
        
    match = re.search(r'(\d{1,2})\s*(?:de|\/|-)?\s*([a-zçáàâãéêíóôõú]+)\.?\s*(?:de|\/|-)?\s*(\d{4})', s)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).replace('.', '')
        year = int(match.group(3))
        month = MONTH_MAP.get(month_str, 1)
        try:
            return date(year, month, day)
        except ValueError:
            return date.today()
            
    return date.today()

@st.cache_data
def process_dataframe(df_raw, reference_date):
    df = df_raw.copy()
    
    # Check column names for copy / description
    if 'Copy' in df.columns and 'Descript' not in df.columns:
        df['Descript'] = df['Copy']
    elif 'Descript' in df.columns and 'Copy' not in df.columns:
        df['Copy'] = df['Descript']
    elif 'Copy' not in df.columns and 'Descript' not in df.columns:
        df['Descript'] = ""
        df['Copy'] = ""

    expected_cols = [
        'AdName', 'Thumb', 'URL', 'ThruPlay', 'Avg Watch Time', 
        '3s Video Views', '75%', 'Saves', 'Shares', 'Comments', 
        'Descript', 'Copy', 'Start', 'End', 'Impressões', 'Alcance', 'R$'
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0 if col in ['ThruPlay', 'Avg Watch Time', '3s Video Views', '75%', 'Saves', 'Shares', 'Comments', 'Impressões', 'Alcance'] else ""
    
    # Clean Numeric Columns
    df['Spend_R$'] = df['R$'].apply(clean_currency)
    df['Impressões_num'] = df['Impressões'].apply(clean_numeric)
    df['Alcance_num'] = df['Alcance'].apply(clean_numeric)
    df['Views_3s'] = df['3s Video Views'].apply(clean_numeric)
    df['Views_75'] = df['75%'].apply(clean_numeric)
    df['ThruPlay_num'] = df['ThruPlay'].apply(clean_numeric)
    df['Avg_Watch_Time_num'] = df['Avg Watch Time'].apply(clean_numeric)
    df['Saves_num'] = df['Saves'].apply(clean_numeric)
    df['Shares_num'] = df['Shares'].apply(clean_numeric)
    df['Comments_num'] = df['Comments'].apply(clean_numeric)
    
    # Requirement 1: Date & Runtime Analysis
    df['Start_Date'] = df['Start'].apply(parse_pt_date)
    df['End_Date'] = df['End'].apply(parse_pt_date)
    
    def calc_pacing(row):
        start = row['Start_Date']
        end = row['End_Date']
        planned = (end - start).days
        if planned <= 0:
            planned = 1
            
        days_elapsed = (reference_date - start).days
        days_elapsed_capped = max(0, min(days_elapsed, planned))
        progress_pct = (days_elapsed_capped / planned) * 100.0
        
        if progress_pct < 25 or days_elapsed < 3:
            pacing = "Recém-Iniciado"
        elif 25 <= progress_pct <= 85:
            pacing = "Em Veiculação"
        else:
            pacing = "Reta Final / Concluído"
            
        return pd.Series([planned, days_elapsed_capped, progress_pct, pacing])
        
    df[['Planned_Duration_Days', 'Days_Elapsed', 'Campaign_Progress_Pct', 'Pacing_Status']] = df.apply(calc_pacing, axis=1)
    
    # Requirement 2: Core Creative & Efficiency Metrics
    # CPM = (Spend / Impressões) * 1000
    df['CPM'] = np.where(df['Impressões_num'] > 0, (df['Spend_R$'] / df['Impressões_num']) * 1000.0, 0.0)
    
    # Retention Rate (%) = (75% views / 3s Video Views) * 100
    df['Retention_Rate_Pct'] = np.where(df['Views_3s'] > 0, (df['Views_75'] / df['Views_3s']) * 100.0, 0.0)
    
    # Creative Engagement Score = (Saves * 10) + (Shares * 10) + (Comments * 5) + (Retention Rate * 2)
    df['Creative_Engagement_Score'] = (
        (df['Saves_num'] * 10) + 
        (df['Shares_num'] * 10) + 
        (df['Comments_num'] * 5) + 
        (df['Retention_Rate_Pct'] * 2)
    )
    
    # Cost per Engaged Action = Spend / (Saves + Shares + Comments + 75% views)
    total_actions = df['Saves_num'] + df['Shares_num'] + df['Comments_num'] + df['Views_75']
    df['Cost_per_Engaged_Action'] = np.where(total_actions > 0, df['Spend_R$'] / total_actions, np.nan)
    
    return df

def render_clickable_plotly(fig, height=520):
    """
    Renders Plotly figure with interactive click redirect (window.open to URL in new tab)
    and transparent background.
    """
    html_content = fig.to_html(
        include_plotlyjs='cdn',
        full_html=True,
        config={
            'responsive': True,
            'displayModeBar': True,
            'displaylogo': False
        }
    )
    
    # Inject JavaScript handler to trigger window.open on click
    click_script = """
    <style>
        body, html { margin: 0; padding: 0; background: transparent !important; }
        .plotly-graph-div { cursor: pointer !important; }
    </style>
    <script>
    function attachClick() {
        var plotEl = document.getElementsByClassName('plotly-graph-div')[0];
        if (plotEl && plotEl.on) {
            plotEl.on('plotly_click', function(data) {
                if (data && data.points && data.points.length > 0) {
                    var pt = data.points[0];
                    var url = null;
                    if (pt.customdata) {
                        if (Array.isArray(pt.customdata)) {
                            url = pt.customdata[0];
                        } else {
                            url = pt.customdata;
                        }
                    }
                    if (url && typeof url === 'string' && url.indexOf('http') === 0) {
                        window.open(url, '_blank');
                    }
                }
            });
        } else {
            setTimeout(attachClick, 250);
        }
    }
    document.addEventListener("DOMContentLoaded", attachClick);
    setTimeout(attachClick, 500);
    </script>
    </body>
    """
    
    html_content = html_content.replace("</body>", click_script)
    components.html(html_content, height=height, scrolling=False)

# Header Title & Intro Reframed
st.markdown("<h1 style='margin:0; font-size: 2.2rem;'>Dashboard de Performance de Vídeo - Meta Ads</h1>", unsafe_allow_html=True)

st.markdown("**Central de Controle do Diretor de Criação:** Avaliação estratégica de performance, retenção de ganchos e recomendações de iteração criativa.")
st.write("")

# Sidebar Controls
st.sidebar.header("📁 Dados & Controles")

uploaded_file = st.sidebar.file_uploader("Upload do CSV do Meta Ads", type=["csv"])
reference_date = st.sidebar.date_input("Data de Referência da Análise (Hoje)", value=date(2026, 7, 24))

df_raw = None
if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV personalizado carregado com sucesso!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o arquivo CSV: {e}")

if df_raw is None:
    if os.path.exists("sample_data.csv"):
        df_raw = pd.read_csv("sample_data.csv")
        st.sidebar.info("💡 Exibindo conjunto de dados de exemplo (`Facens_Quinzenal`). Faça upload do seu CSV a qualquer momento!")
    else:
        st.warning("Por favor, faça upload de um arquivo CSV com os dados de performance de vídeo do Meta Ads.")
        st.stop()

# Process Data
df = process_dataframe(df_raw, reference_date)

# Sidebar Filters
st.sidebar.subheader("🔍 Filtrar Anúncios")
selected_pacing = st.sidebar.multiselect(
    "Filtrar por Status de Veiculação",
    options=["Recém-Iniciado", "Em Veiculação", "Reta Final / Concluído"],
    default=["Recém-Iniciado", "Em Veiculação", "Reta Final / Concluído"]
)

search_term = st.sidebar.text_input("Buscar por Nome do Anúncio ou Palavra-chave do Copy", "")

filtered_df = df[df['Pacing_Status'].isin(selected_pacing)].copy()
if search_term:
    filtered_df = filtered_df[
        filtered_df['AdName'].str.contains(search_term, case=False, na=False) |
        filtered_df['Descript'].str.contains(search_term, case=False, na=False) |
        filtered_df['Copy'].str.contains(search_term, case=False, na=False)
    ]

# ==========================================
# BIG NUMBERS SECTION & SCORE EVALUATION
# ==========================================
total_spend = filtered_df['Spend_R$'].sum()
total_impressions = filtered_df['Impressões_num'].sum()
avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
avg_retention = filtered_df['Retention_Rate_Pct'].mean()
avg_score = filtered_df['Creative_Engagement_Score'].mean()

# Determine Evaluation Tag
if avg_score >= 30:
    eval_tag_html = '<span class="evaluation-tag-excellent">🟢 Status Criativo Geral: Excelente</span>'
elif avg_score >= 15:
    eval_tag_html = '<span class="evaluation-tag-good">🟡 Status Criativo Geral: Bom</span>'
else:
    eval_tag_html = '<span class="evaluation-tag-better">🔴 Status Criativo Geral: Pode Melhorar</span>'

col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

with col_kpi1:
    st.metric("Investimento Total (R$)", f"R$ {total_spend:,.2f}")
with col_kpi2:
    st.metric("CPM Médio", f"R$ {avg_cpm:.2f}")
with col_kpi3:
    st.metric("Retenção Média (75%/3s)", f"{avg_retention:.1f}%")
with col_kpi4:
    st.metric("Pontuação Criativa Média", f"{avg_score:.1f}")
with col_kpi5:
    st.metric("Anúncios Ativos Analisados", f"{len(filtered_df)}")

# Callout / Explanation for Creative Score & Evaluation Tag
col_score_tag, col_score_exp = st.columns([3.5, 2])
with col_score_tag:
    st.markdown("#### Avaliação Benchmark Criativa")
    st.markdown(eval_tag_html, unsafe_allow_html=True)
    st.caption("Níveis de Benchmark: **🟢 Excelente** (≥ 30) | **🟡 Bom** (15 - 29.9) | **🔴 Pode Melhorar** (< 15)")
with col_score_exp:
    with st.expander("📐 Como a Pontuação Criativa é calculada", expanded=False):
        st.markdown(
            "`Pontuação Criativa = (Salvamentos × 10) + (Compartilhamentos × 10) + (Comentários × 5) + (Taxa de Retenção % × 2)`\n\n"
            "*Esta fórmula dá grande peso a ações de alta intenção do usuário (Salvamentos e Compartilhamentos) e recompensa vídeos que mantêm o tempo de visualização acima de 75%.*"
        )

st.divider()

# Main Application Tabs
tab1, tab2, tab3 = st.tabs([
    "Visão Geral & Direção Criativa Estratégica", 
    "Funil de Retenção & Matriz de Performance", 
    "Dados Brutos & Exportação"
])

# ==========================================
# TAB 1: Overview & Creative Director Insights
# ==========================================
with tab1:
    st.subheader("🎯 Diagnósticos do Diretor de Criação & Orientações Práticas")
    st.markdown("Análise baseada em dados avaliando ângulos de copy, estruturas de mensagem e ganchos visuais para direcionar o próximo lote criativo.")
    
    # Generate Creative Director Insights for Each Ad
    for idx, row in filtered_df.iterrows():
        ad_name = row['AdName']
        url = row['URL']
        copy_text = str(row['Descript']) if row['Descript'] else str(row['Copy'])
        pacing = row['Pacing_Status']
        progress = row['Campaign_Progress_Pct']
        score = row['Creative_Engagement_Score']
        cpm = row['CPM']
        retention = row['Retention_Rate_Pct']
        cpa = row['Cost_per_Engaged_Action']
        saves = row['Saves_num']
        shares = row['Shares_num']
        comments = row['Comments_num']
        spend = row['Spend_R$']
        
        # Analyze Copy Attributes
        has_question = "?" in copy_text or "🤔" in copy_text or "E aí" in copy_text
        has_discount = "desconto" in copy_text.lower() or "bolsa" in copy_text.lower() or "100%" in copy_text
        has_testimonial = "alunos" in copy_text.lower() or "voz dos nossos" in copy_text.lower() or "experiência" in copy_text.lower()
        has_urgency = "inscreva-se" in copy_text.lower() or "garanta" in copy_text.lower() or "prova dia" in copy_text.lower()
        
        # Format AdName as HTML hyperlink
        ad_link = f"<a href='{url}' target='_blank'>{ad_name}</a>" if url and str(url).startswith("http") else f"<strong>{ad_name}</strong>"
        
        # Build Strategic Creative Insights based on copy style + metric combination
        if pacing == "Recém-Iniciado":
            insight_html = (
                f"<div class='insight-card' style='border-left-color: #28FFFF;'>"
                f"<strong>Anúncio:</strong> {ad_link} &nbsp;|&nbsp; <strong>Status:</strong> 🔵 {pacing} ({progress:.0f}% de progresso)<br/>"
                f"<strong>Trecho do Copy:</strong> <em>\"{copy_text[:120]}...\"</em><br/>"
                f"⚠️ <strong>Aviso de Veiculação Inicial:</strong> Este anúncio está em fase inicial de teste (Investido R$ {spend:.2f}). "
                f"Aguarde pelo menos 5 a 7 dias de aprendizado de público antes de fazer alterações estruturais. "
                f"<strong>Estratégia para o Próximo Lote:</strong> Mantenha este gancho ativo enquanto prepara variações de capa/miniatura."
                f"</div>"
            )
        elif score >= 25 or (saves + shares > 1):
            if has_testimonial:
                reason = "O ângulo de prova social e depoimento de alunos ressoou fortemente, gerando alto volume de compartilhamentos e salvamentos."
                next_step = "Produzir 2 cortes estilo UGC com depoimentos autênticos de alunos falando diretamente para a câmera nos primeiros 2 segundos."
            elif has_question:
                reason = "A pergunta de curiosidade na abertura prendeu a atenção na rolagem e impulsionou alto engajamento."
                next_step = "Replicar este modelo de gancho baseado em pergunta com 3 variações distintas de título para diferentes personas."
            else:
                reason = "Alto engajamento impulsionado pela clareza da proposta de valor e oferta."
                next_step = "Testar a combinação deste copy de alto valor com vinhetas animadas e destaques em texto no início."

            insight_html = (
                f"<div class='insight-card' style='border-left-color: #C8FF28;'>"
                f"<strong>Anúncio:</strong> {ad_link} &nbsp;|&nbsp; <strong>Pontuação Criativa:</strong> 🔥 {score:.1f} (Retenção: {retention:.1f}%, Salvamentos: {saves:.0f}, Compartilhamentos: {shares:.0f})<br/>"
                f"<strong>Trecho do Copy:</strong> <em>\"{copy_text[:130]}...\"</em><br/>"
                f"💡 <strong>Diagnóstico do Diretor de Criação:</strong> {reason}<br/>"
                f"🚀 <strong>Briefing Prático para o Próximo Lote:</strong> {next_step}"
                f"</div>"
            )
        elif retention < 10.0 or cpm > 15.0:
            if has_urgency:
                diagnosis = "A chamada para ação (CTA) e a urgência do prazo são fortes no copy, mas a introdução do vídeo não retém a atenção nos primeiros 3 segundos (Retenção < 10%)."
                fix = "Destaque o benefício principal (Bolsa/Desconto) em texto chamativo no 1º frame e insira cortes visuais mais rápidos."
            else:
                diagnosis = "CPM alto / baixa retenção indica desconexão da mensagem com o público ou ritmo lento no vídeo."
                fix = "Reduza o texto inicial para menos de 5 palavras, aumente a velocidade de transição das cenas e teste o estilo nativo do Reels."

            insight_html = (
                f"<div class='insight-card' style='border-left-color: #FF6969;'>"
                f"<strong>Anúncio:</strong> {ad_link} &nbsp;|&nbsp; <strong>Pontuação Criativa:</strong> 🚨 {score:.1f} (CPM: R$ {cpm:.2f}, Retenção: {retention:.1f}%)<br/>"
                f"<strong>Trecho do Copy:</strong> <em>\"{copy_text[:130]}...\"</em><br/>"
                f"🚨 <strong>Diagnóstico do Diretor de Criação:</strong> {diagnosis}<br/>"
                f"🛠️ <strong>Briefing Prático para o Próximo Lote:</strong> {fix}"
                f"</div>"
            )
        else:
            insight_html = (
                f"<div class='insight-card' style='border-left-color: #FF9623;'>"
                f"<strong>Anúncio:</strong> {ad_link} &nbsp;|&nbsp; <strong>Pontuação Criativa:</strong> ⚖️ {score:.1f} (Retenção: {retention:.1f}%, CPM: R$ {cpm:.2f})<br/>"
                f"<strong>Trecho do Copy:</strong> <em>\"{copy_text[:130]}...\"</em><br/>"
                f"📊 <strong>Diagnóstico do Diretor de Criação:</strong> Engajamento moderado. A mensagem é clara, mas falta um elemento emocional marcante ou um gancho direto."
                f"<br/>💡 <strong>Briefing Prático para o Próximo Lote:</strong> Testar a inclusão de uma pergunta visual marcante na capa do vídeo e um destaque de benefício mais direto."
                f"</div>"
            )

        st.markdown(insight_html, unsafe_allow_html=True)

    st.markdown("---")
    
    # Ranking Tables
    col_top, col_under = st.columns(2)
    
    with col_top:
        st.markdown("### 🟢 Anúncios Criativos de Maior Performance")
        st.caption("Classificados por maior Pontuação Criativa e menor Custo por Ação Engajada.")
        
        top_ads = filtered_df.sort_values(
            by=['Creative_Engagement_Score', 'Cost_per_Engaged_Action'], 
            ascending=[False, True]
        ).copy()
        
        display_top = top_ads[[
            'AdName', 'Creative_Engagement_Score', 'Cost_per_Engaged_Action', 
            'Retention_Rate_Pct', 'Pacing_Status', 'URL'
        ]].head(5)
        
        display_top.columns = ['Nome do Anúncio', 'Pontuação Criativa', 'Custo / Ação (R$)', 'Retenção %', 'Status', 'URL']
        
        st.data_editor(
            display_top,
            column_config={
                "URL": st.column_config.LinkColumn("Link do Post", display_text="🔗 Ver Post"),
                "Pontuação Criativa": st.column_config.NumberColumn(format="%.1f"),
                "Custo / Ação (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Retenção %": st.column_config.NumberColumn(format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True,
            key="top_ads_table"
        )

    with col_under:
        st.markdown("### 🔴 Anúncios Criativos Abaixo do Esperado")
        st.caption("Classificados por menor Pontuação Criativa e maior CPM.")
        
        under_ads = filtered_df.sort_values(
            by=['Creative_Engagement_Score', 'CPM'], 
            ascending=[True, False]
        ).copy()
        
        display_under = under_ads[[
            'AdName', 'Creative_Engagement_Score', 'CPM', 
            'Retention_Rate_Pct', 'Pacing_Status', 'URL'
        ]].head(5)
        
        display_under.columns = ['Nome do Anúncio', 'Pontuação Criativa', 'CPM (R$)', 'Retenção %', 'Status', 'URL']
        
        st.data_editor(
            display_under,
            column_config={
                "URL": st.column_config.LinkColumn("Link do Post", display_text="🔗 Ver Post"),
                "Pontuação Criativa": st.column_config.NumberColumn(format="%.1f"),
                "CPM (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
                "Retenção %": st.column_config.NumberColumn(format="%.1f%%"),
            },
            hide_index=True,
            use_container_width=True,
            key="under_ads_table"
        )


# ==========================================
# TAB 2: Full-Width Clickable Visualizations & Matrix
# ==========================================
with tab2:
    st.subheader("📊 Análise Visual de Performance (Largura Total)")
    st.info("💡 **Ao clicar em qualquer bolha ou barra nestes gráficos, o post do Meta Ads será aberto diretamente em uma nova aba!**")
    
    # ------------------------------------------------------------------
    # 🎯 1. Efficiency vs. Quality Matrix (Clickable Bubbles)
    # ------------------------------------------------------------------
    st.markdown("### 🎯 1. Matriz de Eficiência vs. Qualidade")
    st.caption("Eixo X = CPM (Eficiência de Custo) | Eixo Y = Pontuação Criativa (Qualidade) | Tamanho da Bolha = Investimento (R$) | **Clique na bolha para abrir o link do post**")
    
    # Quadrant explanatory breakdown
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        st.markdown("""
        <div class="quadrant-box" style="border-top: 4px solid #C8FF28;">
            <strong>🌟 Q1: Alta Qualidade & Baixo CPM</strong><br/>
            <em>Quadrante Superior Esquerdo</em><br/>
            <strong>Ação:</strong> Anúncios Campeões! Escalar orçamento imediatamente e criar variações.
        </div>
        """, unsafe_allow_html=True)
    with col_q2:
        st.markdown("""
        <div class="quadrant-box" style="border-top: 4px solid #28FFFF;">
            <strong>💎 Q2: Alta Qualidade & Alto CPM</strong><br/>
            <em>Quadrante Superior Direito</em><br/>
            <strong>Ação:</strong> Alto Engajamento. Testar públicos mais amplos para reduzir o CPM.
        </div>
        """, unsafe_allow_html=True)
    with col_q3:
        st.markdown("""
        <div class="quadrant-box" style="border-top: 4px solid #FF9623;">
            <strong>⚡ Q3: Baixa Qualidade & Baixo CPM</strong><br/>
            <em>Quadrante Inferior Esquerdo</em><br/>
            <strong>Ação:</strong> Alcance Barato. Aprimorar a taxa de retenção inicial e ganchos do copy.
        </div>
        """, unsafe_allow_html=True)
    with col_q4:
        st.markdown("""
        <div class="quadrant-box" style="border-top: 4px solid #FF6969;">
            <strong>🚨 Q4: Baixa Qualidade & Alto CPM</strong><br/>
            <em>Quadrante Inferior Direito</em><br/>
            <strong>Ação:</strong> Fadiga Criativa / Baixa Relevância. Pausar ou reformular o conceito.
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # Median / Benchmark lines for Quadrants
    median_cpm = filtered_df['CPM'].median() if len(filtered_df) > 0 else 10.0
    median_score = filtered_df['Creative_Engagement_Score'].median() if len(filtered_df) > 0 else 20.0
    
    fig_scatter = px.scatter(
        filtered_df,
        x='CPM',
        y='Creative_Engagement_Score',
        size='Spend_R$',
        color='Pacing_Status',
        custom_data=['URL', 'AdName', 'Spend_R$', 'Retention_Rate_Pct', 'Cost_per_Engaged_Action'],
        labels={
            'CPM': 'CPM (R$ - Menor é Mais Barato)',
            'Creative_Engagement_Score': 'Pontuação Criativa (Maior é Melhor)',
            'Spend_R$': 'Investimento (R$)',
            'Pacing_Status': 'Status de Veiculação'
        },
        color_discrete_map={
            "Recém-Iniciado": "#28FFFF",
            "Em Veiculação": "#C8FF28",
            "Reta Final / Concluído": "#FF9623"
        },
        title="Matriz Criativa dos Anúncios: Clique em qualquer bolha para abrir o post"
    )
    
    # Custom Hover template for scatter plot
    fig_scatter.update_traces(
        hovertemplate="<b>%{customdata[1]}</b><br/>" +
                      "CPM: R$ %{x:.2f}<br/>" +
                      "Pontuação Criativa: %{y:.1f}<br/>" +
                      "Investimento: R$ %{customdata[2]:,.2f}<br/>" +
                      "Retenção (75%/3s): %{customdata[3]:.1f}%<br/>" +
                      "🔗 <i>Clique na bolha para abrir o post</i><extra></extra>"
    )
    
    # Add Reference Quadrant Lines (Dashed)
    fig_scatter.add_vline(x=median_cpm, line_dash="dash", line_color="#B464FF", annotation_text=f"CPM Mediano (R$ {median_cpm:.2f})", annotation_position="top left", annotation_font_color="#FFFFFF")
    fig_scatter.add_hline(y=median_score, line_dash="dash", line_color="#B464FF", annotation_text=f"Pontuação Mediana ({median_score:.1f})", annotation_position="bottom right", annotation_font_color="#FFFFFF")

    # Full Width & Transparent Background
    fig_scatter.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Montserrat, sans-serif'),
        title=dict(font=dict(color='#FFFFFF', size=16)),
        height=540,
        margin=dict(l=30, r=30, t=50, b=30),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255, 255, 255, 0.12)',
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(color='#FFFFFF'),
            title=dict(font=dict(color='#FFFFFF'))
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255, 255, 255, 0.12)',
            zerolinecolor='rgba(255, 255, 255, 0.2)',
            tickfont=dict(color='#FFFFFF'),
            title=dict(font=dict(color='#FFFFFF'))
        ),
        legend=dict(font=dict(color='#FFFFFF'))
    )
    
    render_clickable_plotly(fig_scatter, height=560)

    st.markdown("---")

    # ------------------------------------------------------------------
    # 🔻 2. Full-Width Video Retention Funnel Drop-off (Clickable Bars & No X Axis Caption)
    # ------------------------------------------------------------------
    col_ret_header, col_ret_sort1, col_ret_sort2 = st.columns([2.5, 1.2, 1])
    with col_ret_header:
        st.markdown("### 🔻 2. Funil de Retenção e Queda nos Vídeos")
        st.caption("Gráfico de barras agrupadas comparando Visualizações de 3s vs. ThruPlay vs. Visualizações de 75%. **Passe o mouse para ver o nome do anúncio e clique para abrir o link!**")
    with col_ret_sort1:
        sort_metric = st.selectbox(
            "Ordenar gráfico por:",
            options=[
                "Investimento (R$)",
                "Visualizações de 3s",
                "Visualizações ThruPlay",
                "Visualizações de 75%",
                "Taxa de Retenção (%)",
                "Pontuação Criativa",
                "Nome do Anúncio"
            ],
            index=0,
            key="funnel_sort_metric"
        )
    with col_ret_sort2:
        sort_order = st.selectbox(
            "Ordem:",
            options=["Decrescente", "Crescente"],
            index=0,
            key="funnel_sort_order"
        )

    sort_metric_map = {
        "Investimento (R$)": "Spend_R$",
        "Visualizações de 3s": "Views_3s",
        "Visualizações ThruPlay": "ThruPlay_num",
        "Visualizações de 75%": "Views_75",
        "Taxa de Retenção (%)": "Retention_Rate_Pct",
        "Pontuação Criativa": "Creative_Engagement_Score",
        "Nome do Anúncio": "AdName"
    }

    selected_col = sort_metric_map.get(sort_metric, "Spend_R$")
    ascending_flag = (sort_order == "Crescente")

    top_retention_df = filtered_df.sort_values(by=selected_col, ascending=ascending_flag).copy()
    
    fig_funnel = go.Figure()
    
    # 3s Video Views
    fig_funnel.add_trace(go.Bar(
        x=top_retention_df['AdName'],
        y=top_retention_df['Views_3s'],
        name='Visualizações de 3s (Gancho)',
        marker_color='#28FFFF',
        customdata=top_retention_df[['URL', 'AdName', 'Retention_Rate_Pct', 'Spend_R$']].values,
        hovertemplate="<b>Anúncio:</b> %{customdata[1]}<br/>" +
                      "<b>Métrica:</b> Visualizações de 3s<br/>" +
                      "<b>Volume:</b> %{y:,}<br/>" +
                      "<b>Retenção:</b> %{customdata[2]:.1f}%<br/>" +
                      "🔗 <i>Clique na barra para abrir o link</i><extra></extra>"
    ))
    
    # ThruPlay Views
    fig_funnel.add_trace(go.Bar(
        x=top_retention_df['AdName'],
        y=top_retention_df['ThruPlay_num'],
        name='Visualizações ThruPlay',
        marker_color='#19A5FA',
        customdata=top_retention_df[['URL', 'AdName', 'Retention_Rate_Pct', 'Spend_R$']].values,
        hovertemplate="<b>Anúncio:</b> %{customdata[1]}<br/>" +
                      "<b>Métrica:</b> Visualizações ThruPlay<br/>" +
                      "<b>Volume:</b> %{y:,}<br/>" +
                      "<b>Retenção:</b> %{customdata[2]:.1f}%<br/>" +
                      "🔗 <i>Clique na barra para abrir o link</i><extra></extra>"
    ))
    
    # 75% Video Views
    fig_funnel.add_trace(go.Bar(
        x=top_retention_df['AdName'],
        y=top_retention_df['Views_75'],
        name='Visualizações de 75% (Retenção)',
        marker_color='#C8FF28',
        customdata=top_retention_df[['URL', 'AdName', 'Retention_Rate_Pct', 'Spend_R$']].values,
        hovertemplate="<b>Anúncio:</b> %{customdata[1]}<br/>" +
                      "<b>Métrica:</b> Visualizações de 75%<br/>" +
                      "<b>Volume:</b> %{y:,}<br/>" +
                      "<b>Retenção:</b> %{customdata[2]:.1f}%<br/>" +
                      "🔗 <i>Clique na barra para abrir o link</i><extra></extra>"
    ))
    
    fig_funnel.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFFFFF', family='Montserrat, sans-serif'),
        height=540,
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color='#FFFFFF')
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(
            title=None,
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="Volume de Visualizações", font=dict(color='#FFFFFF')),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.12)',
            tickfont=dict(color='#FFFFFF')
        )
    )
    
    render_clickable_plotly(fig_funnel, height=560)

    st.markdown("---")
    
    # Detailed Video Retention Table
    st.markdown("### 🎥 Tabela Detalhada de Retenção e Engajamento de Vídeo")
    
    retention_table = filtered_df[[
        'AdName', 'Pacing_Status', 'Spend_R$', 'Impressões_num', 
        'Views_3s', 'ThruPlay_num', 'Views_75', 'Retention_Rate_Pct',
        'Avg_Watch_Time_num', 'Saves_num', 'Shares_num', 'Comments_num', 'URL'
    ]].copy()
    
    retention_table.columns = [
        'Nome do Anúncio', 'Status', 'Investimento (R$)', 'Impressões', 
        'Visualizações 3s', 'ThruPlay', 'Visualizações 75%', 'Retenção %', 
        'Tempo Médio (s)', 'Salvamentos', 'Compartilhamentos', 'Comentários', 'URL'
    ]
    
    st.data_editor(
        retention_table,
        column_config={
            "URL": st.column_config.LinkColumn("Link do Post", display_text="🔗 Ver Post"),
            "Investimento (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Impressões": st.column_config.NumberColumn(format="%d"),
            "Visualizações 3s": st.column_config.NumberColumn(format="%d"),
            "ThruPlay": st.column_config.NumberColumn(format="%d"),
            "Visualizações 75%": st.column_config.NumberColumn(format="%d"),
            "Retenção %": st.column_config.NumberColumn(format="%.1f%%"),
            "Tempo Médio (s)": st.column_config.NumberColumn(format="%.1fs"),
        },
        hide_index=True,
        use_container_width=True,
        key="detailed_retention_table"
    )


# ==========================================
# TAB 3: Raw Data & Export
# ==========================================
with tab3:
    st.subheader("📋 Dados Brutos & Métricas Calculadas")
    st.caption("Inspecione todos os atributos importados e calculados ou baixe o CSV processado.")
    
    all_cols = filtered_df.columns.tolist()
    selected_cols = st.multiselect(
        "Selecionar Colunas para Exibir",
        options=all_cols,
        default=[
            'AdName', 'Copy', 'Pacing_Status', 'Spend_R$', 'CPM', 
            'Retention_Rate_Pct', 'Creative_Engagement_Score', 
            'Cost_per_Engaged_Action', 'Start_Date', 'End_Date', 
            'Campaign_Progress_Pct', 'URL'
        ]
    )
    
    st.data_editor(
        filtered_df[selected_cols],
        column_config={
            "URL": st.column_config.LinkColumn("URL", display_text="🔗 Abrir Link"),
            "Thumb": st.column_config.ImageColumn("Pré-visualização da Capa")
        },
        hide_index=True,
        use_container_width=True,
        key="raw_data_editor"
    )
    
    st.markdown("---")
    
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar CSV de Análise Processada",
        data=csv_bytes,
        file_name="meta_ads_analise_criativa.csv",
        mime="text/csv"
    )
