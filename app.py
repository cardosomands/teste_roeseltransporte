import streamlit as st
import pandas as pd
import requests
import base64
import json
import uuid
import io
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Roesel Transportes", page_icon="🚛", layout="wide", initial_sidebar_state="collapsed")

# ── DARK MODE CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
/* Fundo geral */
.stApp { background-color: #0D1117; color: #E6EDF3; }
[data-testid="stSidebar"] { background: #161B22; border-right: 1px solid #30363D; }

/* Métricas */
[data-testid="stMetric"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] { color: #E05252 !important; font-size: 1.5rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8B949E !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.05em; }

/* Inputs */
.stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
    background: #21262D !important; color: #E6EDF3 !important;
    border: 1px solid #30363D !important; border-radius: 8px !important;
}
.stSelectbox > div > div { background: #21262D !important; border: 1px solid #30363D !important; }
[data-testid="stSelectbox"] > div > div { background: #21262D !important; }

/* Botões */
.stButton > button {
    background: linear-gradient(135deg, #8B1A1A, #C0392B) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

/* Botão secundário */
button[kind="secondary"] {
    background: #21262D !important; color: #F85149 !important;
    border: 1px solid #F85149 !important;
}

/* Tabelas */
[data-testid="stDataFrame"] { border: 1px solid #30363D; border-radius: 12px; overflow: hidden; }
.dataframe { background: #161B22 !important; }

/* Expander */
.streamlit-expanderHeader {
    background: #161B22 !important; border: 1px solid #30363D !important;
    border-radius: 8px !important; color: #E6EDF3 !important;
}
.streamlit-expanderContent { background: #161B22 !important; border: 1px solid #30363D !important; }

/* Divider */
hr { border-color: #30363D !important; }

/* Radio e checkbox */
.stRadio label, .stCheckbox label { color: #E6EDF3 !important; }

/* Info/success/error */
.stAlert { border-radius: 8px !important; }

/* Form */
[data-testid="stForm"] { background: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; }

/* File uploader */
[data-testid="stFileUploader"] { background: #161B22; border: 1px solid #30363D; border-radius: 8px; }

/* Título principal */
h1 { color: #E6EDF3 !important; border-bottom: 2px solid #1F6FEB; padding-bottom: 8px; }
h2, h3 { color: #C9D1D9 !important; }

/* Caption */
.stCaption { color: #8B949E !important; }

/* Esconder sidebar */
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D1117; }
::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }

/* Login card */
.login-container {
    display: flex; justify-content: center; align-items: center;
    min-height: 90vh; padding: 20px;
}
.login-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 20px;
    padding: 48px 40px;
    width: 100%;
    max-width: 420px;
    text-align: center;
    box-shadow: 0 24px 80px rgba(0,0,0,0.6);
}
.login-title {
    font-size: 22px; font-weight: 800; color: #E6EDF3;
    letter-spacing: 0.08em; text-transform: uppercase; margin: 16px 0 4px;
}
.login-sub { font-size: 13px; color: #8B949E; margin-bottom: 32px; }
.login-label {
    text-align: left; font-size: 12px; color: #8B949E;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin-bottom: 4px; font-weight: 600;
}

/* Nav bar */
.nav-bar {
    display: flex; align-items: center; gap: 0;
    background: #161B22; border-bottom: 1px solid #30363D;
    padding: 0 16px; margin: -1rem -1rem 1rem -1rem;
    position: sticky; top: 0; z-index: 999;
}
.nav-brand { padding: 10px 16px 10px 0; border-right: 1px solid #30363D; font-weight: 800; font-size: 14px; color: #E05252; letter-spacing: 0.08em; }
.nav-menu { display: flex; flex: 1; gap: 0; padding: 0 8px; overflow-x: auto; }
.nav-user { padding: 6px 14px; border-radius: 20px; background: #21262D; color: #C9D1D9; font-size: 12px; font-weight: 600; border: 1px solid #30363D; white-space: nowrap; }

/* Card */
.card {
    background: #161B22; border: 1px solid #30363D;
    border-radius: 12px; padding: 20px;
    margin-bottom: 12px;
}

/* Status badge */
.badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 700; letter-spacing: 0.05em;
}

/* Download button */
.stDownloadButton > button {
    background: #21262D !important; color: #3FB950 !important;
    border: 1px solid #3FB950 !important; border-radius: 8px !important;
}

/* Número input sem arrows */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
</style>
""", unsafe_allow_html=True)

# ── SUPABASE ───────────────────────────────────────────────────────
SUPABASE_URL = "https://lmcefcmjatnixrsggyvz.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ANTHROPIC_KEY = st.secrets.get("ANTHROPIC_KEY", "")

HDR = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
       "Content-Type": "application/json", "Prefer": "return=representation"}

def sb_get(t, p=""):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/{t}?{p}", headers=HDR, timeout=10)
        return r.json() if r.ok else []
    except: return []

def sb_post(t, d, upsert=False):
    h = {**HDR, "Prefer": "resolution=merge-duplicates,return=representation" if upsert else "return=representation"}
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/{t}", json=d, headers=h, timeout=10)
        return r.ok
    except: return False

def sb_patch(t, f, d):
    try:
        r = requests.patch(f"{SUPABASE_URL}/rest/v1/{t}?{f}", json=d, headers=HDR, timeout=10)
        return r.ok
    except: return False

def sb_delete(t, f):
    try:
        r = requests.delete(f"{SUPABASE_URL}/rest/v1/{t}?{f}", headers={**HDR, "Prefer": ""}, timeout=10)
        return r.ok
    except: return False

# ── LEITURA IA (CORRIGIDA) ─────────────────────────────────────────
def ler_contrato_ia(img_bytes, media_type="image/jpeg"):
    if not ANTHROPIC_KEY:
        return None, "⚠️ Chave ANTHROPIC_KEY não configurada nos Secrets do Streamlit."
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    prompt = """Analise este contrato de transporte e retorne APENAS um JSON puro, sem markdown, sem explicação, sem blocos de código.
Formato obrigatório:
{"cliente":"AUTOPORT","motorista":"NOME EM MAIUSCULAS","placa":"ABC1234","frota":"","contrato":"numero","data":"DD/MM/AAAA","fat_bruto":0.0,"chapa":0.0,"destino":"Cidade/UF","qtd_veiculos":0,"dt_pagamento":"DD/MM/AAAA"}

Retorne SOMENTE o JSON, nada mais."""
    is_pdf = media_type == "application/pdf"
    hdrs = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    if is_pdf:
        hdrs["anthropic-beta"] = "pdfs-2024-09-25"
    bloco = {
        "type": "document" if is_pdf else "image",
        "source": {"type": "base64", "media_type": media_type, "data": b64}
    }
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=hdrs,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": [bloco, {"type": "text", "text": prompt}]}]
            },
            timeout=60
        )
        if not r.ok:
            resp = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
            msg = resp.get("error", {}).get("message", r.text[:200])
            return None, f"Erro API ({r.status_code}): {msg}"
        data = r.json()
        if not data.get("content"):
            return None, "Resposta vazia da API"
        texto = data["content"][0].get("text", "")
        # limpa markdown caso exista
        clean = texto.replace("```json", "").replace("```", "").strip()
        s = clean.find("{")
        e = clean.rfind("}") + 1
        if s >= 0 and e > s:
            return json.loads(clean[s:e]), None
        return None, f"JSON não encontrado na resposta: {clean[:200]}"
    except requests.exceptions.Timeout:
        return None, "Timeout: o arquivo pode ser muito grande ou a rede está lenta."
    except Exception as ex:
        return None, str(ex)

# ── CONSTANTES ─────────────────────────────────────────────────────
MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
META = 127000
SEM = ["FLAVIO","MARIO","ORANGE CARVALHO","WEMERSON CARLOS"]
MOTORISTAS = ["ALEX","DAIVDSON","ELEXSANDRO","GEOVANE","FLAVIO","HEBERT","JOSÉ EDUARDO","LUIZ OTAVIO","MARIO","REINALDO ADRIANO","ROBINSON TAVARES","WAGNER","WEMERSON CARLOS","ORANGE CARVALHO"]
CLIENTES = ["SADA","AUTOPORT","DACUNHA","BRAZUL","VIX","TRANSAUTO","TRANSZERO","OUTRO"]
STATUS = ["ABERTO","ADIANTADO","PENDENTE","FECHADO"]
STATUS_P = ["QUALIFICADO","EM ANÁLISE","APROVADO","PAGO","NÃO APROVADO"]
PERFIS = {
    "🏢 Escritório": {"senha": "roesel2026", "perm": "total"},
    "👩‍💼 Claudiane": {"senha": "claudiane123", "perm": "view"},
    "👥 Equipe": {"senha": "equipe2026", "perm": "equipe"}
}
STATUS_COR = {"ABERTO":"#E05252","ADIANTADO":"#F0883E","PENDENTE":"#BC8CFF","FECHADO":"#3FB950","FOLHA PAGA":"#56D364"}
PLOT = dict(paper_bgcolor="#0D1117", plot_bgcolor="#161B22",
            font=dict(color="#C9D1D9", family="Arial"),
            xaxis=dict(gridcolor="#21262D", color="#8B949E"),
            yaxis=dict(gridcolor="#21262D", color="#8B949E"),
            margin=dict(l=0, r=100, t=20, b=0))

def R(v):
    try: return f"R$ {float(v or 0):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def com(m, f):
    f = float(f or 0)
    return (0, f*0.10) if m in SEM else (f*0.05, f*0.05)

def fd(d):
    try: return datetime.strptime(str(d)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return ""

def badge(status):
    cor = STATUS_COR.get(status, "#8B949E")
    return f'<span style="background:{cor}22;color:{cor};border:1px solid {cor};padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700">{status}</span>'

# ── EXPORTAÇÃO EXCEL ───────────────────────────────────────────────
def gerar_excel(df, titulo="Relatório"):
    """Gera um arquivo Excel formatado com os dados dos contratos."""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = titulo[:31]

    # Cores
    azul_esc = "1F3A6B"
    azul_med = "2E6DA4"
    cinza_cl = "F2F2F2"
    branco = "FFFFFF"
    verde = "1A7A4A"

    thin = Side(style="thin", color="CCCCCC")
    borda = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Cabeçalho
    ws.merge_cells("A1:I1")
    ws["A1"] = f"Carlos Roesel Transportes — {titulo}"
    ws["A1"].font = Font(bold=True, color=branco, size=14, name="Arial")
    ws["A1"].fill = PatternFill("solid", fgColor=azul_esc)
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws["A2"].font = Font(italic=True, color="666666", size=10, name="Arial")
    ws["A2"].alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 18

    # Colunas
    colunas = ["MOTORISTA","CLIENTE","CONTRATO","DATA","FAT. BRUTO (R$)","CHAPA (R$)","ADIANTAMENTO (R$)","FOLHA (R$)","DESTINO","STATUS"]
    for i, col in enumerate(colunas, 1):
        c = ws.cell(row=3, column=i, value=col)
        c.font = Font(bold=True, color=branco, name="Arial", size=10)
        c.fill = PatternFill("solid", fgColor=azul_med)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = borda
    ws.row_dimensions[3].height = 22

    # Dados
    df2 = df.copy()
    if "data" in df2.columns:
        df2["data"] = pd.to_datetime(df2["data"], errors="coerce").dt.strftime("%d/%m/%Y")

    for ri, (_, row) in enumerate(df2.iterrows(), 4):
        fill_cor = cinza_cl if ri % 2 == 0 else branco
        a_val, f_val = com(row.get("motorista",""), row.get("fat_bruto", 0))
        linha = [
            row.get("motorista",""),
            row.get("cliente",""),
            row.get("contrato",""),
            row.get("data",""),
            float(row.get("fat_bruto", 0)),
            float(row.get("chapa", 0)),
            a_val if row.get("motorista","") not in SEM else 0,
            f_val,
            row.get("destino",""),
            row.get("status",""),
        ]
        for ci, val in enumerate(linha, 1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font = Font(name="Arial", size=10)
            c.fill = PatternFill("solid", fgColor=fill_cor)
            c.border = borda
            if ci in (5,6,7,8):
                c.number_format = '#,##0.00'
                c.alignment = Alignment(horizontal="right")
            elif ci == 4:
                c.alignment = Alignment(horizontal="center")
            else:
                c.alignment = Alignment(horizontal="left")
        ws.row_dimensions[ri].height = 18

    # Totais
    nrows = len(df2) + 4
    ws.cell(row=nrows, column=4, value="TOTAL").font = Font(bold=True, name="Arial")
    for ci, col in [(5,"fat_bruto"),(6,"chapa")]:
        v = float(df2[col].sum()) if col in df2.columns else 0
        c = ws.cell(row=nrows, column=ci, value=v)
        c.font = Font(bold=True, color=verde, name="Arial")
        c.number_format = '#,##0.00'
        c.alignment = Alignment(horizontal="right")
        c.fill = PatternFill("solid", fgColor="E8F5E9")
        c.border = borda

    # Larguras
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 16
    ws.column_dimensions["F"].width = 14
    ws.column_dimensions["G"].width = 18
    ws.column_dimensions["H"].width = 14
    ws.column_dimensions["I"].width = 20
    ws.column_dimensions["J"].width = 12

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

# ── LOGIN ──────────────────────────────────────────────────────────
if "ok" not in st.session_state:
    st.session_state.ok = False

if not st.session_state.ok:
    st.markdown("""
    <div style='display:flex;justify-content:center;align-items:center;min-height:85vh'>
      <div style='background:#161B22;border:1px solid #30363D;border-radius:20px;padding:52px 44px 40px;width:440px;text-align:center;box-shadow:0 32px 80px rgba(0,0,0,0.7)'>
        <div style='font-size:56px;margin-bottom:12px'>🚛</div>
        <div style='font-size:22px;font-weight:800;color:#E6EDF3;letter-spacing:0.1em;text-transform:uppercase'>Carlos Roesel</div>
        <div style='font-size:13px;color:#8B949E;margin-bottom:8px'>TRANSPORTES</div>
        <div style='font-size:11px;color:#30363D;margin-bottom:32px'>CNPJ 66.330.549/0001-52</div>
        <div style='height:1px;background:#30363D;margin-bottom:28px'></div>
        <div style='font-size:11px;color:#8B949E;text-align:left;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.05em'>Perfil de Acesso</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        p = st.selectbox("Perfil", list(PERFIS.keys()), label_visibility="collapsed")
        s = st.text_input("Senha", type="password", placeholder="Digite sua senha…", label_visibility="collapsed")
        if st.button("Entrar →", use_container_width=True):
            if s == PERFIS[p]["senha"]:
                st.session_state.ok = True
                st.session_state.perfil = p
                st.session_state.perm = PERFIS[p]["perm"]
                st.rerun()
            else:
                st.error("Senha incorreta. Tente novamente.")
    st.stop()

perm = st.session_state.perm

# ── DADOS ──────────────────────────────────────────────────────────
@st.cache_data(ttl=15)
def get_df():
    d = sb_get("contratos", "order=data.desc")
    if not d or not isinstance(d, list): return pd.DataFrame()
    df = pd.DataFrame(d)
    if df.empty: return df
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    for c in ["fat_bruto","chapa"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)
    df["adiant"] = df.apply(lambda r: com(r["motorista"], r["fat_bruto"])[0], axis=1)
    df["folha"]  = df.apply(lambda r: com(r["motorista"], r["fat_bruto"])[1], axis=1)
    return df

@st.cache_data(ttl=15)
def get_premios():
    d = sb_get("premios")
    return {p["motorista"]: p for p in d} if d and isinstance(d, list) else {}

df_all   = get_df()
prem_map = get_premios()

# ── MENU HORIZONTAL ────────────────────────────────────────────────
if "aba" not in st.session_state:
    st.session_state.aba = "📊 Dashboard"

perfil_nome = st.session_state.perfil.split(" ", 1)[-1] if " " in st.session_state.perfil else st.session_state.perfil

ABAS = ["📊 Dashboard","➕ Novo Contrato","📋 Contratos","👤 Por Motorista","💳 Comissões","🏆 Prêmios"]
nav_cols = st.columns([2, 1, 1, 1, 1, 1, 1, 0.5, 1.2, 0.6])
with nav_cols[0]:
    st.markdown("<div style='padding:12px 0;font-size:15px;font-weight:800;color:#E05252;letter-spacing:0.08em'>🚛 ROESEL</div>", unsafe_allow_html=True)
for i, a in enumerate(ABAS, 1):
    with nav_cols[i]:
        ativo = st.session_state.aba == a
        if st.button(a.split(" ",1)[-1], key=f"nav_{i}",
            use_container_width=True,
            type="primary" if ativo else "secondary"):
            st.session_state.aba = a
            st.rerun()
with nav_cols[8]:
    st.markdown(f'<div style="padding:8px 0;text-align:right"><span style="background:#21262D;border:1px solid #30363D;border-radius:20px;padding:4px 12px;font-size:12px;color:#C9D1D9">{perfil_nome}</span></div>', unsafe_allow_html=True)
with nav_cols[9]:
    if st.button("🚪", help="Sair", use_container_width=True):
        st.session_state.ok = False
        st.rerun()

st.markdown('<hr style="margin:8px 0;border-color:#30363D">', unsafe_allow_html=True)
aba = st.session_state.aba

# ── FILTRO DE PERÍODO ──────────────────────────────────────────────
def sel_periodo(key_suffix=""):
    anos_list = [0] + sorted(df_all["data"].dt.year.dropna().unique().astype(int).tolist(), reverse=True) if not df_all.empty else [0, 2026]
    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        ano = st.selectbox("📅 Ano", anos_list,
            index=1 if len(anos_list) > 1 else 0,
            format_func=lambda x: "Todos os anos" if x == 0 else str(x),
            key=f"ano_{key_suffix}")
    with c2:
        mes = st.selectbox("🗓️ Mês", [0] + list(range(1, 13)),
            index=datetime.now().month,
            format_func=lambda x: "Todos" if x == 0 else MESES[x - 1],
            key=f"mes_{key_suffix}")
    periodo = f"{MESES[mes-1]}/{ano}" if mes and ano else ("Todos" if not mes and not ano else MESES[mes-1] if mes else str(ano))
    df = df_all.copy()
    if not df_all.empty:
        if ano: df = df[df["data"].dt.year == ano]
        if mes: df = df[df["data"].dt.month == mes]
    return df, periodo, ano, mes

# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════
if aba == "📊 Dashboard":
    st.markdown("# 📊 Dashboard")
    df, periodo, ano, mes = sel_periodo("dash")
    st.markdown(f"<p style='color:#8B949E;margin-top:-12px'>{periodo} · {len(df)} contratos</p>", unsafe_allow_html=True)

    if df.empty:
        st.markdown(f"""<div class='card' style='text-align:center;padding:60px'>
            <div style='font-size:40px'>📭</div>
            <div style='color:#8B949E;margin-top:8px'>Nenhum contrato em {periodo}</div>
        </div>""", unsafe_allow_html=True)
    else:
        fat = df["fat_bruto"].sum()
        pend = len(df[df["status"].isin(["ABERTO","PENDENTE"])])
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("💰 Faturamento", R(fat))
        c2.metric("📄 Contratos", len(df))
        c3.metric("⚠️ Pendentes", pend)
        c4.metric("⏩ Adiantamentos", R(df["adiant"].sum()))
        c5.metric("📋 Folha", R(df["folha"].sum()))
        c6.metric("🔧 Chapas", R(df["chapa"].sum()))

        meta_pct = min(fat / META * 100, 100)
        cor_meta = "#3FB950" if meta_pct >= 100 else "#F0883E"
        st.markdown(f"""
        <div class='card'>
            <div style='display:flex;justify-content:space-between;margin-bottom:8px'>
                <span style='color:#C9D1D9;font-weight:700;font-size:13px'>🏆 Progresso da Meta Mensal</span>
                <span style='color:{cor_meta};font-weight:700;font-size:13px'>{R(fat)} / {R(META)} ({meta_pct:.1f}%)</span>
            </div>
            <div style='background:#21262D;border-radius:4px;height:8px'>
                <div style='background:linear-gradient(90deg,#1F6FEB,{cor_meta});width:{meta_pct}%;height:8px;border-radius:4px;transition:width 0.5s'></div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("#### 📈 Faturamento por Motorista")
            fm = df.groupby("motorista")["fat_bruto"].sum().sort_values().reset_index()
            fm["cor"] = fm["fat_bruto"].apply(lambda x: "#3FB950" if x >= META else "#E05252")
            fig = go.Figure(go.Bar(
                x=fm["fat_bruto"], y=fm["motorista"], orientation="h",
                marker_color=fm["cor"],
                text=[R(v) for v in fm["fat_bruto"]], textposition="outside",
                textfont=dict(color="#C9D1D9", size=11)
            ))
            fig.add_vline(x=META, line_dash="dash", line_color="#F0883E",
                annotation_text="Meta 🏆", annotation_font_color="#F0883E")
            fig.update_layout(height=420, **PLOT)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 🥧 Status dos Contratos")
            sc = df["status"].value_counts().reset_index()
            fig2 = px.pie(sc, values="count", names="status",
                color="status", color_discrete_map=STATUS_COR, hole=0.5)
            fig2.update_layout(height=420, paper_bgcolor="#0D1117",
                font=dict(color="#C9D1D9"), legend=dict(font=dict(color="#C9D1D9")),
                margin=dict(l=0, r=0, t=20, b=0))
            fig2.update_traces(textfont_color="#E6EDF3")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### 🏆 Ranking de Motoristas")
        rk = df.groupby("motorista")["fat_bruto"].sum().sort_values(ascending=False).reset_index()
        for i, row in rk.iterrows():
            pct = min(row["fat_bruto"] / META * 100, 100)
            el = row["fat_bruto"] >= META
            cor = "#F0883E" if el else "#388BFD"
            st.markdown(f"""
            <div class='card' style='display:flex;align-items:center;gap:16px;padding:12px 16px;margin:4px 0'>
                <div style='font-size:18px;width:30px;text-align:center'>{"🏆" if el else f"#{i+1}"}</div>
                <div style='flex:1'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:6px'>
                        <span style='color:#E6EDF3;font-weight:700;font-size:13px'>{row["motorista"]}</span>
                        <span style='color:{cor};font-weight:700;font-size:13px'>{R(row["fat_bruto"])}</span>
                    </div>
                    <div style='background:#21262D;border-radius:3px;height:5px'>
                        <div style='background:{cor};width:{pct}%;height:5px;border-radius:3px'></div>
                    </div>
                </div>
                <div style='font-size:11px;color:{"#3FB950" if el else "#8B949E"};font-weight:700;white-space:nowrap'>
                    {"✅ Elegível" if el else f"Falta {R(META - row['fat_bruto'])}"}
                </div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# NOVO CONTRATO
# ══════════════════════════════════════════════════════════════════
elif aba == "➕ Novo Contrato":
    if perm not in ["total","equipe"]:
        st.warning("Sem permissão para cadastrar contratos.")
        st.stop()
    st.markdown("# ➕ Novo Contrato")

    with st.expander("📷 Importar por Foto ou PDF com IA", expanded=False):
        if not ANTHROPIC_KEY:
            st.warning("⚠️ Configure a chave `ANTHROPIC_KEY` nos Secrets do Streamlit para usar esta função.")
        else:
            st.markdown("<p style='color:#8B949E;font-size:13px'>Envie uma foto ou PDF do contrato e a IA irá preencher os campos automaticamente.</p>", unsafe_allow_html=True)
        upl = st.file_uploader("Selecione a foto ou PDF do contrato",
            type=["jpg","jpeg","png","webp","pdf"],
            help="Formatos aceitos: JPG, PNG, WEBP, PDF")
        if upl:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                if upl.type != "application/pdf":
                    st.image(upl, use_container_width=True)
                else:
                    st.markdown(f"""<div class='card' style='text-align:center;padding:24px'>
                        <div style='font-size:36px'>📄</div>
                        <div style='color:#388BFD;font-weight:700;margin-top:8px'>{upl.name}</div>
                        <div style='color:#8B949E;font-size:12px'>PDF pronto para análise</div>
                    </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🤖 Analisar com IA", use_container_width=True, disabled=not ANTHROPIC_KEY):
                    with st.spinner("Analisando contrato… Pode levar alguns segundos."):
                        arquivo = upl.read()
                        if len(arquivo) > 5 * 1024 * 1024:
                            st.error("Arquivo muito grande (máx. 5 MB). Por favor, comprima a imagem.")
                        else:
                            dados, erro = ler_contrato_ia(arquivo, upl.type)
                    if erro:
                        st.error(f"Erro: {erro}")
                        st.info("Dica: verifique se a ANTHROPIC_KEY está correta nos Secrets do Streamlit.")
                    elif dados:
                        st.session_state["ia"] = dados
                        st.success("✅ Contrato lido com sucesso! Campos preenchidos abaixo.")
                        st.rerun()

    ia = st.session_state.get("ia", {})
    if ia:
        st.info("📋 Campos preenchidos pela IA — revise antes de salvar!")

    with st.form("fnovo", clear_on_submit=True):
        c1,c2,c3 = st.columns(3)
        mi = MOTORISTAS.index(ia.get("motorista","")) if ia.get("motorista","") in MOTORISTAS else 0
        ci = CLIENTES.index(ia.get("cliente","")) if ia.get("cliente","") in CLIENTES else 0
        mot   = c1.selectbox("Motorista *", MOTORISTAS, index=mi)
        cli   = c2.selectbox("Cliente *", CLIENTES, index=ci)
        placa = c3.text_input("Placa *", ia.get("placa","")).upper()

        c4,c5,c6 = st.columns(3)
        cont  = c4.text_input("Nº Contrato *", ia.get("contrato",""))
        frota = c5.text_input("Frota", ia.get("frota",""))
        dia   = datetime.now()
        if ia.get("data"):
            try: dia = datetime.strptime(ia["data"], "%d/%m/%Y")
            except: pass
        data_v = c6.date_input("Data *", dia)

        c7,c8,c9 = st.columns(3)
        fat_v   = c7.number_input("Fat. Bruto (R$) *", float(ia.get("fat_bruto", 0)), step=100.0, format="%.2f")
        chapa_v = c8.number_input("Chapa (R$)", float(ia.get("chapa", 0)), step=50.0, format="%.2f")
        qtd     = c9.number_input("Qtd Veículos", int(ia.get("qtd_veiculos", 0)), step=1)

        c10,c11 = st.columns(2)
        dest = c10.text_input("Destino", ia.get("destino","")).upper()
        sts  = c11.selectbox("Status", STATUS)

        c12,c13 = st.columns(2)
        dt_pag = c12.date_input("Dt. Pagamento", value=None)
        adpago = c13.checkbox("Adiantamento Pago?")
        obs = st.text_area("Observação", "", height=80)

        if fat_v > 0:
            a, f = com(mot, fat_v)
            st.markdown(f"""<div class='card' style='border-left:3px solid #388BFD;border-radius:0 8px 8px 0;padding:10px 14px;font-size:12px;color:#C9D1D9'>
                💳 {"Sem adiantamento · " if mot in SEM else f"Adiantamento: <b style='color:#F0883E'>{R(a)}</b> · "}Folha: <b style='color:#BC8CFF'>{R(f)}</b>
            </div>""", unsafe_allow_html=True)

        if st.form_submit_button("✅ Salvar Contrato", use_container_width=True):
            if not cont or not fat_v:
                st.error("Preencha os campos obrigatórios: Nº Contrato e Faturamento.")
            else:
                novo = {"id": str(uuid.uuid4()), "motorista": mot, "cliente": cli,
                        "placa": placa, "frota": frota, "contrato": cont, "data": str(data_v),
                        "fat_bruto": fat_v, "chapa": chapa_v, "destino": dest,
                        "qtd_veiculos": int(qtd), "adiantamento_pago": adpago,
                        "dt_pagamento": str(dt_pag) if dt_pag else None,
                        "status": sts, "obs": obs}
                if sb_post("contratos", novo):
                    st.success(f"✅ Contrato {cont} salvo com sucesso!")
                    st.cache_data.clear()
                    st.session_state.pop("ia", None)
                    st.rerun()
                else:
                    st.error("❌ Erro ao salvar no banco. Verifique a conexão com o Supabase.")

# ══════════════════════════════════════════════════════════════════
# CONTRATOS
# ══════════════════════════════════════════════════════════════════
elif aba == "📋 Contratos":
    st.markdown("# 📋 Contratos")
    df, periodo, ano, mes = sel_periodo("cont")
    st.markdown(f"<p style='color:#8B949E;margin-top:-12px'>{periodo}</p>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    busca = c1.text_input("🔍 Buscar", "", placeholder="Motorista, contrato, destino…")
    fs = c2.selectbox("Status", ["Todos"] + STATUS)
    fc = c3.selectbox("Cliente", ["Todos"] + CLIENTES)

    dv = df.copy()
    if not dv.empty:
        if busca:
            b = busca.upper()
            dv = dv[dv.apply(lambda r:
                b in str(r.get("motorista","")).upper() or
                b in str(r.get("contrato","")).upper() or
                b in str(r.get("destino","")).upper(), axis=1)]
        if fs != "Todos": dv = dv[dv["status"] == fs]
        if fc != "Todos": dv = dv[dv.get("cliente","") == fc]

    # Sumário
    st.markdown(f"""<div style='display:flex;gap:24px;margin-bottom:12px;flex-wrap:wrap'>
        <span style='color:#8B949E;font-size:13px'><b style='color:#E6EDF3'>{len(dv)}</b> contratos encontrados</span>
        <span style='color:#8B949E;font-size:13px'>Faturamento: <b style='color:#3FB950'>{R(dv["fat_bruto"].sum() if not dv.empty else 0)}</b></span>
        <span style='color:#8B949E;font-size:13px'>Adiantamentos: <b style='color:#F0883E'>{R(dv["adiant"].sum() if not dv.empty else 0)}</b></span>
        <span style='color:#8B949E;font-size:13px'>Folha: <b style='color:#BC8CFF'>{R(dv["folha"].sum() if not dv.empty else 0)}</b></span>
    </div>""", unsafe_allow_html=True)

    if not dv.empty:
        # Tabela organizada
        cols = [c for c in ["motorista","cliente","contrato","data","fat_bruto","chapa","destino","status","adiantamento_pago"] if c in dv.columns]
        ds = dv[cols].copy()
        ds["data"] = ds["data"].dt.strftime("%d/%m/%Y")
        ds["fat_bruto"] = ds["fat_bruto"].apply(R)
        ds["chapa"] = ds["chapa"].apply(R)
        ds["adiantamento_pago"] = ds["adiantamento_pago"].apply(lambda x: "✅" if x else "❌")
        ds.columns = ["MOTORISTA","CLIENTE","CONTRATO","DATA","FAT. BRUTO","CHAPA","DESTINO","STATUS","ADIANT."][:len(cols)]

        st.dataframe(ds, use_container_width=True, hide_index=True,
            column_config={
                "FAT. BRUTO": st.column_config.TextColumn(width="medium"),
                "MOTORISTA": st.column_config.TextColumn(width="medium"),
                "STATUS": st.column_config.TextColumn(width="small"),
                "ADIANT.": st.column_config.TextColumn(width="small"),
            })

        # Exportação
        col_exp1, col_exp2 = st.columns(2)
        with col_exp1:
            csv = dv.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button("📥 Exportar CSV", csv,
                f"contratos_{periodo.replace('/','_')}.csv", "text/csv",
                use_container_width=True)
        with col_exp2:
            try:
                excel_buf = gerar_excel(dv, f"Contratos {periodo}")
                st.download_button("📊 Exportar Excel (.xlsx)", excel_buf,
                    f"contratos_{periodo.replace('/','_')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except Exception as ex:
                st.caption(f"Excel indisponível: {ex}")

        # Editar/Excluir
        if perm == "total":
            st.markdown("---")
            st.markdown("#### ✏️ Editar / Excluir Contrato")
            labels = [f"{r['motorista']} — {r['contrato']} — {fd(str(r['data'])[:10])}" for _, r in dv.iterrows()]
            sel = st.selectbox("Selecione o contrato", labels)
            row = dv.iloc[labels.index(sel)]
            with st.expander("✏️ Editar este contrato"):
                with st.form("fedit"):
                    ec1,ec2 = st.columns(2)
                    es = ec1.selectbox("Status", STATUS,
                        index=STATUS.index(row.get("status","ABERTO")) if row.get("status") in STATUS else 0)
                    ea = ec2.checkbox("Adiantamento Pago?", value=bool(row.get("adiantamento_pago")))
                    eo = st.text_area("Obs", value=row.get("obs","") or "")
                    if st.form_submit_button("💾 Salvar alterações"):
                        if sb_patch("contratos", f"id=eq.{row['id']}", {"status": es, "adiantamento_pago": ea, "obs": eo}):
                            st.success("✅ Alterações salvas!")
                            st.cache_data.clear()
                            st.rerun()
            if st.button(f"🗑️ Excluir contrato {row['contrato']}", type="secondary"):
                if sb_delete("contratos", f"id=eq.{row['id']}"):
                    st.success("Contrato excluído.")
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.info("Nenhum contrato encontrado com os filtros selecionados.")

# ══════════════════════════════════════════════════════════════════
# POR MOTORISTA
# ══════════════════════════════════════════════════════════════════
elif aba == "👤 Por Motorista":
    st.markdown("# 👤 Por Motorista")
    df, periodo, ano, mes = sel_periodo("mot")
    if df.empty:
        st.info("Nenhum dado no período selecionado.")
    else:
        mot = st.selectbox("Selecione o motorista", sorted(df["motorista"].dropna().unique().tolist()))
        dm  = df[df["motorista"] == mot]
        fat = dm["fat_bruto"].sum()
        a, f = com(mot, fat)
        pct  = min(fat / META * 100, 100)
        cor  = "#3FB950" if fat >= META else "#E05252"

        st.markdown(f"""<div class='card'>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'>
                <div>
                    <div style='font-size:20px;font-weight:800;color:#E6EDF3'>{mot}</div>
                    <div style='font-size:12px;color:#8B949E'>{"Sem adiantamento · 10% folha" if mot in SEM else "Com adiantamento · 5%+5%"}</div>
                </div>
                <div style='font-size:24px;font-weight:800;color:{cor}'>{R(fat)}</div>
            </div>
            <div style='background:#21262D;border-radius:4px;height:8px;margin-bottom:8px'>
                <div style='background:{cor};width:{pct}%;height:8px;border-radius:4px'></div>
            </div>
            <div style='font-size:11px;color:#8B949E'>{"🏆 Elegível para prêmio!" if fat >= META else f"Falta {R(META-fat)} para a meta"}</div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Viagens", len(dm))
        c2.metric("Adiantamento", R(a) if mot not in SEM else "N/A")
        c3.metric("Folha", R(f))
        c4.metric("Chapas", R(dm["chapa"].sum()))

        st.markdown("---")
        if not dm.empty:
            cols = [c for c in ["contrato","cliente","data","fat_bruto","chapa","destino","status"] if c in dm.columns]
            ds = dm[cols].copy()
            ds["data"] = ds["data"].dt.strftime("%d/%m/%Y")
            ds["fat_bruto"] = ds["fat_bruto"].apply(R)
            ds["chapa"] = ds["chapa"].apply(R)
            ds.columns = [c.upper().replace("_"," ") for c in ds.columns]
            st.dataframe(ds, use_container_width=True, hide_index=True)

            try:
                excel_buf = gerar_excel(dm, f"{mot} {periodo}")
                st.download_button("📊 Exportar Excel", excel_buf,
                    f"{mot.replace(' ','_')}_{periodo.replace('/','_')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except: pass

# ══════════════════════════════════════════════════════════════════
# COMISSÕES
# ══════════════════════════════════════════════════════════════════
elif aba == "💳 Comissões":
    st.markdown("# 💳 Comissões")
    df, periodo, ano, mes = sel_periodo("com")
    st.markdown(f"<p style='color:#8B949E;margin-top:-12px'>{periodo}</p>", unsafe_allow_html=True)
    if df.empty:
        st.info("Nenhum dado no período.")
    else:
        for mot in MOTORISTAS:
            dm = df[df["motorista"] == mot]
            if dm.empty: continue
            fat = dm["fat_bruto"].sum()
            a, f = com(mot, fat)
            pct = min(fat / META * 100, 100)
            cor = "#3FB950" if fat >= META else "#E05252"
            st.markdown(f"""
            <div class='card'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>
                    <div>
                        <span style='font-weight:700;color:#E6EDF3'>{mot}</span>
                        <span style='font-size:11px;color:#8B949E;margin-left:8px'>{"10% folha" if mot in SEM else "5%+5%"} · {len(dm)} viagens</span>
                    </div>
                    <div style='text-align:right'>
                        <span style='color:{cor};font-weight:700'>{R(fat)}</span>
                        {"&nbsp;&nbsp;<span style='background:#F0883E22;color:#F0883E;border:1px solid #F0883E;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700'>🏆 ELEGÍVEL</span>" if fat >= META else ""}
                    </div>
                </div>
                <div style='display:flex;gap:20px;font-size:12px;color:#8B949E;flex-wrap:wrap'>
                    {"<span>Adiant: <b style='color:#F0883E'>N/A</b></span>" if mot in SEM else f"<span>Adiant: <b style='color:#F0883E'>{R(a)}</b></span>"}
                    <span>Folha: <b style='color:#BC8CFF'>{R(f)}</b></span>
                    <span>Chapas: <b style='color:#C9D1D9'>{R(dm["chapa"].sum())}</b></span>
                    <span>Total: <b style='color:#3FB950'>{R(a+f)}</b></span>
                </div>
                <div style='background:#21262D;border-radius:3px;height:4px;margin-top:10px'>
                    <div style='background:{cor};width:{pct}%;height:4px;border-radius:3px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # Exportação Excel das comissões
        st.markdown("---")
        rows_exp = []
        for mot in MOTORISTAS:
            dm = df[df["motorista"] == mot]
            if dm.empty: continue
            fat = dm["fat_bruto"].sum()
            a, f = com(mot, fat)
            rows_exp.append({
                "motorista": mot, "tipo": "10% folha" if mot in SEM else "5%+5%",
                "viagens": len(dm), "fat_bruto": fat, "adiantamento": 0 if mot in SEM else a,
                "folha": f, "chapas": dm["chapa"].sum(), "total_comissao": a+f
            })
        df_com = pd.DataFrame(rows_exp)
        try:
            excel_buf = gerar_excel(df_com.rename(columns={
                "motorista":"motorista","tipo":"status","viagens":"contrato",
                "fat_bruto":"fat_bruto","adiantamento":"adiant","folha":"folha",
                "chapas":"chapa","total_comissao":"destino"
            }), f"Comissões {periodo}")
            st.download_button("📊 Exportar Relatório de Comissões (.xlsx)", excel_buf,
                f"comissoes_{periodo.replace('/','_')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except: pass

# ══════════════════════════════════════════════════════════════════
# PRÊMIOS
# ══════════════════════════════════════════════════════════════════
elif aba == "🏆 Prêmios":
    st.markdown("# 🏆 Prêmios")
    df, periodo, ano, mes = sel_periodo("prem")
    st.markdown(f"<p style='color:#8B949E;margin-top:-12px'>Meta: {R(META)} · {periodo}</p>", unsafe_allow_html=True)
    if df.empty:
        st.info("Nenhum dado no período.")
    else:
        for mot in MOTORISTAS:
            dm = df[df["motorista"] == mot]
            if dm.empty: continue
            fat  = dm["fat_bruto"].sum()
            el   = fat >= META
            prem = prem_map.get(mot, {})
            with st.expander(f"{'🏆' if el else '⏳'} {mot} — {R(fat)}", expanded=el):
                c1,c2,c3 = st.columns(3)
                c1.metric("Faturamento", R(fat))
                c2.metric("Meta", R(META))
                c3.metric("Elegível?", "✅ SIM" if el else f"Falta {R(META - fat)}")
                if prem.get("status"):
                    cor_p = {"QUALIFICADO":"#388BFD","EM ANÁLISE":"#F0883E","APROVADO":"#3FB950","PAGO":"#56D364","NÃO APROVADO":"#F85149"}.get(prem["status"],"#8B949E")
                    st.markdown(f"""<div class='card' style='border-left:3px solid {cor_p};border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0'>
                        <span style='color:{cor_p};font-weight:700'>{prem["status"]}</span>
                        {f" · <span style='color:#3FB950;font-weight:700'>{R(prem.get('valor',0))}</span>" if prem.get("valor") else ""}
                        {f"<div style='color:#8B949E;font-size:12px;margin-top:4px'>{prem['obs']}</div>" if prem.get("obs") else ""}
                    </div>""", unsafe_allow_html=True)
                if perm == "total" and el:
                    with st.form(f"fp_{mot}"):
                        pc1,pc2 = st.columns(2)
                        ps = pc1.selectbox("Status do Prêmio", STATUS_P,
                            index=STATUS_P.index(prem.get("status","QUALIFICADO")) if prem.get("status") in STATUS_P else 0)
                        pv = pc2.number_input("Valor (R$)", value=float(prem.get("valor") or 0), format="%.2f")
                        po = st.text_input("Observação", value=prem.get("obs","") or "")
                        if st.form_submit_button("💾 Salvar Prêmio"):
                            if sb_post("premios", {"motorista": mot, "status": ps, "valor": pv, "obs": po}, upsert=True):
                                st.success("✅ Prêmio salvo!")
                                st.cache_data.clear()
                                st.rerun()
