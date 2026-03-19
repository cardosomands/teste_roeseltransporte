import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import uuid

st.set_page_config(page_title="Roesel Transportes", page_icon="🚛", layout="wide")

st.markdown("""<style>
.main{background:#F8FAFD}
[data-testid="stMetricValue"]{font-size:1.4rem;font-weight:700}
</style>""", unsafe_allow_html=True)

SUPABASE_URL = "https://lmcefcmjatnixrsggyvz.supabase.co"
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=representation"}

def sb_get(t,p=""):
    try:
        r=requests.get(f"{SUPABASE_URL}/rest/v1/{t}?{p}",headers=HEADERS,timeout=10)
        return r.json() if r.ok else []
    except: return []

def sb_post(t,d,upsert=False):
    h={**HEADERS,"Prefer":"resolution=merge-duplicates,return=representation" if upsert else "return=representation"}
    try:
        r=requests.post(f"{SUPABASE_URL}/rest/v1/{t}",json=d,headers=h,timeout=10)
        return r.ok
    except: return False

def sb_patch(t,f,d):
    try:
        r=requests.patch(f"{SUPABASE_URL}/rest/v1/{t}?{f}",json=d,headers=HEADERS,timeout=10)
        return r.ok
    except: return False

def sb_delete(t,f):
    try:
        r=requests.delete(f"{SUPABASE_URL}/rest/v1/{t}?{f}",headers={**HEADERS,"Prefer":""},timeout=10)
        return r.ok
    except: return False

MESES=["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
META=127000
SEM_ADIANT=["FLAVIO","MARIO","ORANGE CARVALHO","WEMERSON CARLOS"]
MOTORISTAS=["ALEX","DAIVDSON","ELEXSANDRO","GEOVANE","FLAVIO","HEBERT","JOSÉ EDUARDO","LUIZ OTAVIO","MARIO","REINALDO ADRIANO","ROBINSON TAVARES","WAGNER","WEMERSON CARLOS","ORANGE CARVALHO"]
CLIENTES=["SADA","AUTOPORT","DACUNHA","BRAZUL","VIX","TRANSAUTO","TRANSZERO","OUTRO"]
STATUS_OPTS=["ABERTO","ADIANTADO","PENDENTE","FECHADO"]
STATUS_PREM=["QUALIFICADO","EM ANÁLISE","APROVADO","PAGO","NÃO APROVADO"]
PERFIS={"🏢 Escritório":{"senha":"roesel2026","perm":"total"},"👩‍💼 Claudiane":{"senha":"claudiane123","perm":"view"},"👥 Equipe":{"senha":"equipe2026","perm":"equipe"}}

def R(v):
    try: return f"R$ {float(v or 0):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def com(m,f):
    f=float(f or 0)
    return (0,f*.10) if m in SEM_ADIANT else (f*.05,f*.05)

def fd(d):
    try: return datetime.strptime(str(d)[:10],"%Y-%m-%d").strftime("%d/%m/%Y")
    except: return ""

if "ok" not in st.session_state: st.session_state.ok=False

if not st.session_state.ok:
    _,col,_=st.columns([1,1.2,1])
    with col:
        st.markdown("<div style='text-align:center;padding:40px 0 10px'><div style='font-size:60px'>🚛</div><h2 style='color:#1B3A6B'>Carlos Roesel Transportes</h2><p style='color:#9AA5BB'>CNPJ 66.330.549/0001-52</p></div>",unsafe_allow_html=True)
        p=st.selectbox("Perfil",list(PERFIS.keys()))
        s=st.text_input("Senha",type="password")
        if st.button("Entrar →",use_container_width=True):
            if s==PERFIS[p]["senha"]:
                st.session_state.ok=True; st.session_state.perfil=p; st.session_state.perm=PERFIS[p]["perm"]; st.rerun()
            else: st.error("Senha incorreta")
    st.stop()

perm=st.session_state.perm

@st.cache_data(ttl=15)
def get_df():
    d=sb_get("contratos","order=data.desc")
    if not d or not isinstance(d,list): return pd.DataFrame()
    df=pd.DataFrame(d)
    if df.empty: return df
    df["data"]=pd.to_datetime(df["data"],errors="coerce")
    for c in ["fat_bruto","chapa"]: df[c]=pd.to_numeric(df.get(c,0),errors="coerce").fillna(0)
    df["adiant"]=df.apply(lambda r:com(r["motorista"],r["fat_bruto"])[0],axis=1)
    df["folha"]=df.apply(lambda r:com(r["motorista"],r["fat_bruto"])[1],axis=1)
    return df

@st.cache_data(ttl=15)
def get_premios():
    d=sb_get("premios")
    return {p["motorista"]:p for p in d} if d and isinstance(d,list) else {}

df_all=get_df()
prem_map=get_premios()

with st.sidebar:
    st.markdown("### 🚛 Roesel Transportes")
    st.caption(f"{st.session_state.perfil}")
    st.divider()
    st.markdown("### 📅 Período")
    anos=[0]+sorted(df_all["data"].dt.year.dropna().unique().astype(int).tolist(),reverse=True) if not df_all.empty else [0,2026]
    ano=st.selectbox("Ano",anos,index=1 if len(anos)>1 else 0,format_func=lambda x:"Todos" if x==0 else str(x))
    mes=st.selectbox("Mês",[0]+list(range(1,13)),index=datetime.now().month,format_func=lambda x:"Todos" if x==0 else MESES[x-1])
    st.divider()
    aba=st.radio("Menu",["📊 Dashboard","➕ Novo Contrato","📋 Contratos","👤 Por Motorista","💳 Comissões","🏆 Prêmios"])
    st.divider()
    if st.button("🚪 Sair",use_container_width=True): st.session_state.ok=False; st.rerun()

df=df_all.copy()
if not df.empty:
    if ano: df=df[df["data"].dt.year==ano]
    if mes: df=df[df["data"].dt.month==mes]
periodo=f"{MESES[mes-1]}/{ano}" if mes and ano else "Todos os períodos"

if aba=="📊 Dashboard":
    st.title(f"📊 Dashboard — {periodo}")
    if df.empty:
        st.info(f"Nenhum contrato em {periodo}.")
    else:
        fat=df["fat_bruto"].sum(); n=len(df); pend=len(df[df["status"].isin(["ABERTO","PENDENTE"])])
        c1,c2,c3,c4,c5,c6=st.columns(6)
        c1.metric("💰 Faturamento",R(fat)); c2.metric("📄 Contratos",n); c3.metric("⚠️ Pendentes",pend)
        c4.metric("⏩ Adiantamentos",R(df["adiant"].sum())); c5.metric("📋 Folha",R(df["folha"].sum())); c6.metric("🔧 Chapas",R(df["chapa"].sum()))
        st.divider()
        col1,col2=st.columns([3,2])
        with col1:
            st.markdown("#### 📈 Faturamento por Motorista")
            fm=df.groupby("motorista")["fat_bruto"].sum().sort_values().reset_index()
            fm["cor"]=fm["fat_bruto"].apply(lambda x:"#FFD700" if x>=META else "#2E6DA4")
            fig=go.Figure(go.Bar(x=fm["fat_bruto"],y=fm["motorista"],orientation="h",marker_color=fm["cor"],text=[R(v) for v in fm["fat_bruto"]],textposition="outside"))
            fig.add_vline(x=META,line_dash="dash",line_color="#F59E0B",annotation_text="Meta")
            fig.update_layout(height=420,margin=dict(l=0,r=100,t=10,b=0),plot_bgcolor="white",paper_bgcolor="white")
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            st.markdown("#### 🥧 Status")
            sc=df["status"].value_counts().reset_index()
            cores={"ABERTO":"#3B82F6","ADIANTADO":"#F97316","PENDENTE":"#A855F7","FECHADO":"#059669"}
            fig2=px.pie(sc,values="count",names="status",color="status",color_discrete_map=cores,hole=0.4)
            fig2.update_layout(height=420,margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig2,use_container_width=True)
        st.divider()
        st.markdown("#### 🏆 Ranking")
        rk=df.groupby("motorista")["fat_bruto"].sum().sort_values(ascending=False).reset_index()
        rk["Faturamento"]=rk["fat_bruto"].apply(R)
        rk["Elegível?"]=rk["fat_bruto"].apply(lambda x:"🏆 SIM" if x>=META else f"Falta {R(META-x)}")
        st.dataframe(rk[["motorista","Faturamento","Elegível?"]].rename(columns={"motorista":"Motorista"}),use_container_width=True,hide_index=True)

elif aba=="➕ Novo Contrato":
    if perm not in ["total","equipe"]: st.warning("Sem permissão."); st.stop()
    st.title("➕ Novo Contrato")
    with st.form("form_novo",clear_on_submit=True):
        c1,c2,c3=st.columns(3)
        mot=c1.selectbox("Motorista *",MOTORISTAS); cli=c2.selectbox("Cliente *",CLIENTES); placa=c3.text_input("Placa *","").upper()
        c4,c5,c6=st.columns(3)
        cont=c4.text_input("Nº Contrato *",""); frota=c5.text_input("Frota",""); data_v=c6.date_input("Data *",datetime.now())
        c7,c8,c9=st.columns(3)
        fat=c7.number_input("Fat. Bruto (R$) *",0.0,step=100.0,format="%.2f"); chapa=c8.number_input("Chapa (R$)",0.0,step=50.0,format="%.2f"); qtd=c9.number_input("Qtd Veículos",0,step=1)
        c10,c11=st.columns(2)
        dest=c10.text_input("Destino","").upper(); status=c11.selectbox("Status",STATUS_OPTS)
        c12,c13=st.columns(2)
        dt_pag=c12.date_input("Dt. Pagamento",value=None); adpago=c13.checkbox("Adiantamento Pago?")
        obs=st.text_area("Observação","",height=80)
        if fat>0:
            a,f=com(mot,fat)
            st.info(f"💳 {'Sem adiantamento · ' if mot in SEM_ADIANT else f'Adiantamento: {R(a)} · '}Folha: {R(f)}")
        if st.form_submit_button("✅ Salvar Contrato",use_container_width=True):
            if not cont or not fat: st.error("Preencha os campos obrigatórios!")
            else:
                novo={"id":str(uuid.uuid4()),"motorista":mot,"cliente":cli,"placa":placa,"frota":frota,"contrato":cont,"data":str(data_v),"fat_bruto":fat,"chapa":chapa,"destino":dest,"qtd_veiculos":int(qtd),"adiantamento_pago":adpago,"dt_pagamento":str(dt_pag) if dt_pag else None,"status":status,"obs":obs}
                if sb_post("contratos",novo): st.success(f"✅ Contrato {cont} salvo!"); st.cache_data.clear(); st.rerun()
                else: st.error("Erro ao salvar!")

elif aba=="📋 Contratos":
    st.title(f"📋 Contratos — {periodo}")
    c1,c2,c3=st.columns(3)
    busca=c1.text_input("🔍 Buscar",""); fs=c2.selectbox("Status",["Todos"]+STATUS_OPTS); fc=c3.selectbox("Cliente",["Todos"]+CLIENTES)
    dv=df.copy()
    if not dv.empty:
        if busca:
            b=busca.upper(); dv=dv[dv.apply(lambda r:b in str(r.get("motorista","")).upper() or b in str(r.get("contrato","")).upper() or b in str(r.get("destino","")).upper(),axis=1)]
        if fs!="Todos": dv=dv[dv["status"]==fs]
        if fc!="Todos": dv=dv[dv.get("cliente","")==fc]
    st.markdown(f"**{len(dv)} contratos** · **{R(dv['fat_bruto'].sum() if not dv.empty else 0)}**")
    if not dv.empty:
        cols=[c for c in ["motorista","cliente","contrato","data","fat_bruto","chapa","destino","status","adiantamento_pago"] if c in dv.columns]
        ds=dv[cols].copy(); ds["data"]=ds["data"].dt.strftime("%d/%m/%Y"); ds["fat_bruto"]=ds["fat_bruto"].apply(R); ds["chapa"]=ds["chapa"].apply(R)
        ds["adiantamento_pago"]=ds["adiantamento_pago"].apply(lambda x:"✅" if x else "❌")
        ds.columns=["MOTORISTA","CLIENTE","CONTRATO","DATA","FAT. BRUTO","CHAPA","DESTINO","STATUS","ADIANT."][:len(cols)]
        st.dataframe(ds,use_container_width=True,hide_index=True)
        csv=dv.to_csv(index=False,sep=";",encoding="utf-8-sig")
        st.download_button(f"📥 Exportar CSV",csv,f"contratos_{periodo.replace('/','_')}.csv","text/csv")
        if perm=="total":
            st.divider(); st.markdown("#### ✏️ Editar / Excluir")
            labels=[f"{r['motorista']} — {r['contrato']} — {fd(str(r['data'])[:10])}" for _,r in dv.iterrows()]
            sel=st.selectbox("Selecione",labels); row=dv.iloc[labels.index(sel)]
            with st.expander("✏️ Editar"):
                with st.form("edit"):
                    ec1,ec2=st.columns(2)
                    es=ec1.selectbox("Status",STATUS_OPTS,index=STATUS_OPTS.index(row.get("status","ABERTO")) if row.get("status") in STATUS_OPTS else 0)
                    ea=ec2.checkbox("Adiantamento Pago?",value=bool(row.get("adiantamento_pago")))
                    eo=st.text_area("Obs",value=row.get("obs","") or "")
                    if st.form_submit_button("💾 Salvar"):
                        if sb_patch("contratos",f"id=eq.{row['id']}",{"status":es,"adiantamento_pago":ea,"obs":eo}):
                            st.success("Salvo!"); st.cache_data.clear(); st.rerun()
            if st.button(f"🗑️ Excluir {row['contrato']}",type="secondary"):
                if sb_delete("contratos",f"id=eq.{row['id']}"):
                    st.success("Excluído!"); st.cache_data.clear(); st.rerun()
    else: st.info("Nenhum contrato encontrado.")

elif aba=="👤 Por Motorista":
    st.title(f"👤 Por Motorista — {periodo}")
    if df.empty: st.info("Nenhum dado.")
    else:
        mot=st.selectbox("Motorista",sorted(df["motorista"].dropna().unique().tolist()))
        dm=df[df["motorista"]==mot]; fat=dm["fat_bruto"].sum(); a,f=com(mot,fat)
        c1,c2,c3,c4,c5=st.columns(5)
        c1.metric("Viagens",len(dm)); c2.metric("Faturamento",R(fat)); c3.metric("Adiantamento",R(a) if mot not in SEM_ADIANT else "N/A"); c4.metric("Folha",R(f)); c5.metric("Prêmio","🏆 Elegível!" if fat>=META else f"Falta {R(META-fat)}")
        st.divider()
        if not dm.empty:
            cols=[c for c in ["contrato","cliente","data","fat_bruto","chapa","destino","status"] if c in dm.columns]
            ds=dm[cols].copy(); ds["data"]=ds["data"].dt.strftime("%d/%m/%Y"); ds["fat_bruto"]=ds["fat_bruto"].apply(R); ds["chapa"]=ds["chapa"].apply(R)
            ds.columns=[c.upper().replace("_"," ") for c in ds.columns]
            st.dataframe(ds,use_container_width=True,hide_index=True)

elif aba=="💳 Comissões":
    st.title(f"💳 Comissões — {periodo}")
    if df.empty: st.info("Nenhum dado.")
    else:
        rows=[]
        for mot in MOTORISTAS:
            dm=df[df["motorista"]==mot]
            if dm.empty: continue
            fat=dm["fat_bruto"].sum(); a,f=com(mot,fat)
            rows.append({"Motorista":mot,"Tipo":"10% folha" if mot in SEM_ADIANT else "5%+5%","Viagens":len(dm),"Faturamento":R(fat),"Adiantamento":"N/A" if mot in SEM_ADIANT else R(a),"Folha":R(f),"Chapas":R(dm["chapa"].sum()),"Total":R(a+f)})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

elif aba=="🏆 Prêmios":
    st.title(f"🏆 Prêmios — {periodo}")
    st.caption(f"Meta: {R(META)}")
    if df.empty: st.info("Nenhum dado.")
    else:
        for mot in MOTORISTAS:
            dm=df[df["motorista"]==mot]
            if dm.empty: continue
            fat=dm["fat_bruto"].sum(); el=fat>=META; prem=prem_map.get(mot,{})
            with st.expander(f"{'🏆' if el else '⏳'} {mot} — {R(fat)}",expanded=el):
                c1,c2,c3=st.columns(3)
                c1.metric("Faturamento",R(fat)); c2.metric("Meta",R(META)); c3.metric("Elegível?","✅ SIM" if el else f"Falta {R(META-fat)}")
                if prem.get("status"): st.info(f"Status: **{prem['status']}** | Valor: **{R(prem.get('valor',0))}**")
                if perm=="total" and el:
                    with st.form(f"p_{mot}"):
                        pc1,pc2=st.columns(2)
                        ps=pc1.selectbox("Status",STATUS_PREM,index=STATUS_PREM.index(prem.get("status","QUALIFICADO")) if prem.get("status") in STATUS_PREM else 0)
                        pv=pc2.number_input("Valor (R$)",value=float(prem.get("valor") or 0),format="%.2f")
                        po=st.text_input("Observação",value=prem.get("obs","") or "")
                        if st.form_submit_button("💾 Salvar"):
                            if sb_post("premios",{"motorista":mot,"status":ps,"valor":pv,"obs":po},upsert=True):
                                st.success("✅ Salvo!"); st.cache_data.clear(); st.rerun()
