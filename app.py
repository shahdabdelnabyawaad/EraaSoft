import base64
import os

import pandas as pd
import plotly.express as px
import streamlit as st

os.chdir(os.path.dirname(os.path.abspath(__file__)))
NAVY, TEAL, AMBER, RED, GREEN = "#1F2A6B", "#1B8AA6", "#F2A93B", "#E5484D", "#2FB67C"
PAL = [TEAL, NAVY, "#3BC1D6", AMBER, RED, "#6C7AE0", GREEN]
CFG = {"displayModeBar": False}
PAGES = [("Overview", "📊"), ("Stores", "🏬"),
         ("Categories", "🧴"), ("Inventory", "📦"),
         ("People & Customers", "👥"), ("Branch Explorer", "🔎")]

DESC = {
    "Overview": "All 8 KPIs, monthly trend, branches and categories at a glance.",
    "Stores": "Which branches are really profitable once discounting is counted? Includes the discount simulator.",
    "Categories": "Which categories drive revenue and margin, and which just drive discounting?",
    "Inventory": "How much inventory is at risk of expiring unsold, and where?",
    "People & Customers": "Pharmacist workload, prescriptions, payment channels and loyalty segments.",
    "Branch Explorer": "Pick one branch and see its manager, KPIs and trends.",
}
st.set_page_config(page_title="Pharmacy Performance Dashboard", page_icon="💊", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html,body,[class*="st-"],.stApp{{font-family:'Poppins','Segoe UI',sans-serif}}
.stApp{{background:linear-gradient(180deg,#e9f0f9 0%,#f7f9fd 100%)}}
header[data-testid=stHeader]{{background:transparent;height:0}}
[data-testid=stToolbar],#MainMenu,footer,section[data-testid=stSidebar],[data-testid=stSidebarCollapsedControl]{{display:none!important}}
.block-container,[data-testid=stMainBlockContainer]{{padding-top:1.2rem!important;padding-bottom:2rem;max-width:1400px}}
.st-key-hdr{{background:linear-gradient(120deg,{NAVY} 0%,#17307f 55%,{TEAL} 140%);border-radius:22px;
padding:14px 26px;box-shadow:0 10px 30px rgba(31,42,107,.28);align-items:center}}
.st-key-hdr button{{height:46px;border-radius:14px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);color:#fff;transition:all .2s}}
.st-key-hdr button:hover{{background:rgba(255,255,255,.28);transform:translateY(-2px);color:#fff;border-color:#fff}}
.st-key-hdr button[data-testid=stBaseButton-primary]{{background:#3BC1D6;color:{NAVY};border-color:#3BC1D6;box-shadow:0 0 18px rgba(59,193,214,.6)}}
.st-key-hdr button *{{color:inherit!important}}
.ttl{{color:#fff;font-size:24px;font-weight:700;line-height:1.15}}
.sub{{color:#a9d8e2;font-size:13px;margin-top:2px}}
.st-key-flt{{background:#fff;border-radius:16px;padding:10px 18px;margin:14px 0 6px;box-shadow:0 4px 14px rgba(31,42,107,.07);border:1px solid #e6ecf5}}
.kpi{{position:relative;overflow:hidden;height:118px;display:flex;align-items:center;gap:14px;background:#fff;
border-radius:18px;padding:0 18px 0 22px;border:1px solid #e6ecf5;box-shadow:0 6px 18px rgba(31,42,107,.08);
transition:transform .2s,box-shadow .2s}}
.kpi:hover{{transform:translateY(-4px);box-shadow:0 14px 28px rgba(31,42,107,.16)}}
.kpi:before{{content:'';position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--c)}}
.kpi .ic{{flex:0 0 52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px}}
.kpi .tx{{min-width:0}}
.kpi .l{{font-size:12px;color:#6b7690;font-weight:500}}
.kpi .v{{font-size:23px;font-weight:700;color:{NAVY};white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.kpi .s{{font-size:11.5px;color:#8a94b8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.insight{{background:linear-gradient(90deg,{NAVY},#26327f);color:#fff;border-radius:14px;padding:14px 20px;margin:12px 0 16px;
border-left:6px solid #3BC1D6;font-size:14px;box-shadow:0 6px 16px rgba(31,42,107,.18)}}
.sec{{color:{NAVY};font-size:20px;font-weight:600;margin:18px 0 4px}}
[data-testid=stVerticalBlockBorderWrapper]{{background:#fff;border-radius:18px;border:1px solid #e6ecf5!important;
box-shadow:0 6px 18px rgba(31,42,107,.07)}}
</style>""", unsafe_allow_html=True)


from urllib.parse import quote

_P = {
    "home": "<path d='M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z'/>",
    "n_0": "<rect x='3' y='3' width='7' height='9' rx='1.5'/><rect x='14' y='3' width='7' height='5' rx='1.5'/><rect x='14' y='12' width='7' height='9' rx='1.5'/><rect x='3' y='16' width='7' height='5' rx='1.5'/>",
    "n_1": "<path d='M3 9l1.5-5h15L21 9'/><path d='M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0'/><path d='M5 12v8h14v-8'/><path d='M10 20v-5h4v5'/>",
    "n_2": "<rect x='3' y='3' width='7' height='7' rx='1.5'/><rect x='14' y='3' width='7' height='7' rx='1.5'/><rect x='3' y='14' width='7' height='7' rx='1.5'/><circle cx='17.5' cy='17.5' r='3.5'/>",
    "n_3": "<path d='M21 8 12 3 3 8v8l9 5 9-5z'/><path d='M3 8l9 5 9-5'/><path d='M12 13v8'/>",
    "n_4": "<circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6'/><circle cx='17' cy='9' r='2.7'/><path d='M17 14c3 0 4.5 1.9 4.5 5'/>",
    "n_5": "<path d='M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z'/><circle cx='12' cy='10' r='2.5'/>",
}
_css = (".st-key-hdr [data-testid=stButton]{display:flex;justify-content:center}"
        ".st-key-hdr button{width:54px!important;min-width:54px!important;height:54px!important;border-radius:16px!important;"
        "padding:0!important;display:flex;align-items:center;justify-content:center;font-size:0!important}"
        ".st-key-hdr button p{display:none}"
        ".st-key-hdr button::after{content:'';display:block;width:28px;height:28px;background:#fff;"
        "-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:center;mask-position:center;"
        "-webkit-mask-size:contain;mask-size:contain}"
        ".st-key-hdr button[data-testid=stBaseButton-primary]::after{background:" + NAVY + "}")
for _k, _inner in _P.items():
    _svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.8' "
            "stroke-linecap='round' stroke-linejoin='round'>" + _inner + "</svg>")
    _key = "n_home" if _k == "home" else _k
    _u = 'url("data:image/svg+xml;utf8,' + quote(_svg) + '")'
    _css += f".st-key-{_key} button::after{{-webkit-mask-image:{_u};mask-image:{_u}}}"
st.markdown("<style>" + _css + "</style>", unsafe_allow_html=True)


def kpi(col, icon, label, value, sub="", color=TEAL):
    col.markdown(f"<div class='kpi' style='--c:{color}'><div class='ic' style='background:{color}22'>{icon}</div>"
                 f"<div class='tx'><div class='l'>{label}</div><div class='v'>{value}</div><div class='s'>{sub}&nbsp;</div></div></div>",
                 unsafe_allow_html=True)


def insight(text):
    st.markdown(f"<div class='insight'>{text}</div>", unsafe_allow_html=True)


def section(text):
    st.markdown(f"<div class='sec'>{text}</div>", unsafe_allow_html=True)


def show(fig, col=None, h=380):
    fig.update_layout(template="plotly_white", height=h, margin=dict(l=10, r=10, t=55, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Poppins, Segoe UI, sans-serif", color="#44506f"),
                      title_font=dict(size=15, color=NAVY), legend_title_text="")
    with (col or st).container(border=True):
        st.plotly_chart(fig, use_container_width=True, config=CFG)


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes", "y"])


LOGO_MODE = "pill"  # "white" = transparent white logos, "pill" = logos on white rounded boxes
RAW = "https://raw.githubusercontent.com/shahdabdelnabyawaad/EraaSoft/main/"
if st.query_params.get("page") != "overview":
    html = """
<style>
body{overflow:hidden}
.cv{position:fixed;inset:0;z-index:99999;overflow:hidden;font-family:'Segoe UI',Tahoma,sans-serif;
background:linear-gradient(rgba(11,19,43,.55),rgba(11,19,43,.55)),
url('https://images.unsplash.com/photo-1576602976047-174e57a47881?q=80&w=1600&auto=format&fit=crop') center/cover no-repeat,
radial-gradient(circle,#26327f,#0b1033)}
.ov{position:absolute;inset:0;background:#050a18;z-index:5;pointer-events:none;animation:fo .8s ease-in-out 2.2s forwards}
@keyframes fo{to{opacity:0}}
.era{position:absolute;z-index:10;left:50%;top:50%;transform:translate(-50%,-50%) scale(1.4);background:#fff;
padding:10px 18px;border-radius:15px;box-shadow:0 0 35px rgba(0,168,204,.5);animation:mv 1.8s cubic-bezier(.77,0,.175,1) .6s forwards}
.era img{height:clamp(34px,6vh,55px);display:block}
@keyframes mv{to{left:3%;top:4%;transform:translate(0,0) scale(.75)}}
.mid{position:absolute;inset:0;z-index:3;display:flex;flex-direction:column;align-items:center;justify-content:center;
gap:clamp(14px,3vh,26px);padding:12vh 0 6vh;opacity:0;animation:fi .9s ease-in-out 2.6s forwards}
.mid img.m{height:clamp(80px,16vh,150px);max-width:70vw;object-fit:contain;filter:drop-shadow(0 0 28px rgba(59,193,214,.5))}
.tb{padding:16px 30px;background:rgba(11,19,43,.7);border:1px solid rgba(0,168,204,.45);border-radius:16px;
box-shadow:0 8px 25px rgba(0,0,0,.3);color:#fff;font-size:clamp(20px,3.2vw,38px);font-weight:800;letter-spacing:.8px;text-align:center;margin:0 16px}
.go{display:inline-block;padding:clamp(10px,1.8vh,14px) clamp(24px,3vw,38px);border-radius:999px;background:#3BC1D6;color:#0b1033!important;
font-weight:700;font-size:18px;text-decoration:none!important;box-shadow:0 0 0 0 rgba(59,193,214,.6);
animation:pulse 2s infinite;transition:transform .2s}
.go:hover{transform:scale(1.08)}
@keyframes pulse{70%{box-shadow:0 0 0 18px rgba(59,193,214,0)}100%{box-shadow:0 0 0 0 rgba(59,193,214,0)}}
.lg{position:absolute;z-index:4;background:rgba(255,255,255,.96);padding:9px 16px;border-radius:13px;
box-shadow:0 7px 20px rgba(0,0,0,.3);opacity:0;animation:fi .8s ease-in-out 2.8s forwards}
.lg img{height:clamp(26px,5vh,42px);display:block}
.ic{top:4%;right:3%}.dg{bottom:4%;left:3%;animation-delay:3s}
@keyframes fi{to{opacity:1}}
</style>
<div class="cv"><div class="ov"></div>
<div class="era"><img src="__RAW__Logo%20EraaSoft.webp"></div>
<div class="mid">
<div class="tb">Pharmacy Performance Dashboard</div>
<a class="go" href="?page=overview" target="_self">Open dashboard</a></div>
<div class="lg ic"><img src="__RAW__Logo%20icareer.webp"></div>
<div class="lg dg"><img src="__RAW__Logo%20Digitera.png"></div></div>"""
    if LOGO_MODE == "white":
        html = html.replace("</style>", ".era,.lg{background:none!important;box-shadow:none!important;padding:0!important}"
                            ".era img,.lg img{filter:brightness(0) invert(1) drop-shadow(0 0 12px rgba(59,193,214,.7))}</style>", 1)
    st.markdown(html.replace("__RAW__", RAW), unsafe_allow_html=True)
    st.stop()

@st.cache_data
def load():
    r = pd.read_csv
    store, prod, emp, cust = r("dim_store.csv"), r("dim_product.csv"), r("dim_employee.csv"), r("dim_customer.csv")
    sales, stock, rx = r("fact_sales.csv"), r("fact_stock.csv"), r("fact_prescriptions.csv")
    sales["sale_date"] = pd.to_datetime(sales["sale_date"])
    rx["issue_date"] = pd.to_datetime(rx["issue_date"])
    rx["doctor_name"] = rx["doctor_name"].astype(str).str.replace(r"^(Dr\.\s*)+", "Dr. ", regex=True)
    pcols = ["product_id", "product_name", "category_name", "cost_price"]
    sales = sales.merge(store[["store_id", "store_name"]], on="store_id").merge(prod[pcols], on="product_id")
    stock = stock.merge(store[["store_id", "store_name"]], on="store_id").merge(prod[pcols], on="product_id")
    stock["at_risk"] = truthy(stock["expiry_risk_flag"])
    stock["below"] = truthy(stock["below_reorder_flag"])
    stock["risk_value"] = stock["quantity"] * stock["cost_price"] * stock["at_risk"]
    rx = rx.merge(store[["store_id", "store_name"]], on="store_id")
    emp = emp.merge(store[["store_id", "store_name"]], on="store_id")
    emp["is_ph"] = truthy(emp["is_pharmacist"])
    cust["loyalty_tier"] = cust["loyalty_tier"].fillna("No Tier")
    sales = sales.merge(cust[["customer_id", "loyalty_tier"]], on="customer_id", how="left")
    sales["loyalty_tier"] = sales["loyalty_tier"].fillna("No Tier")
    return sales, stock, rx, emp, store




if "page" not in st.session_state:
    st.session_state.page = "Overview"


def go(name):
    st.session_state.page = name


def home():
    st.query_params.clear()


sales, stock, rx, emp, store = load()

with st.container(key="hdr"):
    cols = st.columns([1.5, 3.0] + [0.6] * 7, vertical_alignment="center")
    cols[0].image("logo_white.png", width=150)
    cols[1].markdown(f"<div class='ttl'>Pharmacy Performance Dashboard</div><div class='sub'>{st.session_state.page}</div>",
                     unsafe_allow_html=True)
    cols[2].button(" ", help="Back to cover", key="n_home", on_click=home, use_container_width=True)
    for i, (name, icon) in enumerate(PAGES):
        cols[3 + i].button(" ", help=name, key=f"n_{i}", on_click=go, args=(name,),
                           type="primary" if st.session_state.page == name else "secondary", use_container_width=True)
page = st.session_state.page

with st.container(key="flt"):
    f1, f2 = st.columns([3, 2])
    stores = f1.multiselect("Branches (leave empty for all)", sorted(sales["store_name"].unique()))
    d0, d1 = sales["sale_date"].min().date(), sales["sale_date"].max().date()
    dates = f2.date_input("Date range", (d0, d1), min_value=d0, max_value=d1)

if stores:
    sales, stock, rx, emp = [d[d["store_name"].isin(stores)] for d in (sales, stock, rx, emp)]
if len(dates) == 2:
    a, b = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
    sales = sales[sales["sale_date"].between(a, b)]
    rx = rx[rx["issue_date"].between(a, b)]
if sales.empty:
    st.warning("No data for the selected filters.")
    st.stop()

rev, prof = sales["total_amount"].sum(), sales["profit"].sum()
margin = prof / rev
pharm = int(emp["is_ph"].sum())
known = sales.dropna(subset=["customer_id"])
cnt = known.groupby("customer_id")["sale_id"].transform("count")
rep_share = known.loc[cnt > 1, "total_amount"].sum() / rev
st_sum = sales.groupby("store_name").agg(rev=("total_amount", "sum"), prof=("profit", "sum"),
                                          disc=("discount_pct", "mean"), loss=("profit", lambda s: (s < 0).mean())).reset_index()
st_sum["margin"] = st_sum["prof"] / st_sum["rev"]
cat_sum = sales.groupby("category_name").agg(rev=("total_amount", "sum"), prof=("profit", "sum"),
                                              disc=("discount_pct", "mean")).reset_index()
cat_sum["margin"] = cat_sum["prof"] / cat_sum["rev"]
risk = stock["risk_value"].sum()
PCT = dict(tickformat=".0%")

if page == "Overview":
    c = st.columns(4)
    kpi(c[0], "💰", "Total Revenue", f"${rev/1e6:.2f}M", "Selected branches and dates")
    kpi(c[1], "📈", "Total Profit", f"${prof/1e6:.2f}M", f"Overall margin {margin:.1%}", NAVY)
    kpi(c[2], "🏷️", "Average Discount", f"{sales['discount_pct'].mean():.1f}%", f"{(sales['profit'] < 0).mean():.1%} of sales lose money", AMBER)
    kpi(c[3], "⏳", "Expiring Inventory at Risk", f"${risk:,.0f}", "Flagged batches at cost", RED)
    st.write("")
    c = st.columns(4)
    ts, tc = st_sum.sort_values("rev").iloc[-1], cat_sum.sort_values("rev").iloc[-1]
    kpi(c[0], "🏬", "Top Branch by Revenue", ts["store_name"], f"${ts['rev']/1e3:,.0f}K, margin {ts['margin']:.1%}")
    kpi(c[1], "🧴", "Top Category by Revenue", tc["category_name"], f"${tc['rev']/1e3:,.0f}K, margin {tc['margin']:.1%}", NAVY)
    kpi(c[2], "💊", "Prescriptions per Pharmacist", f"{len(rx)/pharm:,.0f}" if pharm else "-", f"{pharm} pharmacists", GREEN)
    kpi(c[3], "🔁", "Repeat-Customer Revenue", f"{rep_share:.1%}", "Customers with 2+ purchases", NAVY)
    best, worst = st_sum.sort_values("margin").iloc[-1], st_sum.sort_values("margin").iloc[0]
    insight(f"{best['store_name']} has the best margin ({best['margin']:.1%}); {worst['store_name']} has the lowest ({worst['margin']:.1%}).")
    m = sales.groupby(sales["sale_date"].dt.to_period("M").astype(str))[["total_amount", "profit"]].sum().reset_index()
    show(px.area(m, x="sale_date", y=["total_amount", "profit"], title="Revenue and profit by month", color_discrete_sequence=[TEAL, NAVY]))
    l, r_ = st.columns(2)
    show(px.bar(st_sum.sort_values("rev"), x="rev", y="store_name", orientation="h", color="margin",
                title="Revenue by branch (color = margin)", color_continuous_scale=["#E8F4F8", TEAL, NAVY]), l)
    show(px.bar(cat_sum.sort_values("rev"), x="rev", y="category_name", orientation="h", color="margin",
                title="Revenue by category (color = margin)", color_continuous_scale=["#E8F4F8", TEAL, NAVY]), r_)

elif page == "Stores":
    section("Which branches are really profitable once discounting is counted?")
    w = st_sum.sort_values("loss").iloc[-1]
    insight(f"{w['store_name']} has the most loss-making sales ({w['loss']:.1%}) with an average discount of {w['disc']:.1f}%.")
    l, r_ = st.columns(2)
    f = px.bar(st_sum.sort_values("margin"), x="margin", y="store_name", orientation="h", title="Margin by branch", color_discrete_sequence=[TEAL])
    f.update_xaxes(**PCT)
    show(f, l)
    f = px.scatter(st_sum, x="disc", y="margin", size="rev", color="loss", text="store_name",
                   title="Discount vs margin (size = revenue)", color_continuous_scale=[GREEN, AMBER, RED])
    f.update_yaxes(**PCT)
    f.update_traces(textposition="top center")
    show(f, r_)
    with st.container(border=True):
        st.dataframe(st_sum.rename(columns={"store_name": "Branch", "rev": "Revenue", "prof": "Profit", "disc": "Avg discount %",
                                            "loss": "Loss-making sales", "margin": "Margin"}).style.format(
            {"Revenue": "${:,.0f}", "Profit": "${:,.0f}", "Avg discount %": "{:.1f}", "Loss-making sales": "{:.1%}", "Margin": "{:.1%}"}),
            use_container_width=True, hide_index=True)
    section("Discount simulator")
    cut = st.slider("Reduce every discount by (%)", 0, 50, 20, 5)
    sim_rev = (sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100 * (1 - cut / 100))).sum()
    sim_prof = sim_rev - sales["cost_amount"].sum()
    c = st.columns(3)
    kpi(c[0], "📊", "Current profit", f"${prof:,.0f}", "As recorded")
    kpi(c[1], "🧪", "Simulated profit", f"${sim_prof:,.0f}", f"Discounts cut by {cut}%", NAVY)
    kpi(c[2], "⚖️", "Profit change", f"{sim_prof - prof:+,.0f}", "Assumes the same quantities are sold", AMBER)

elif page == "Categories":
    section("Which categories drive revenue and margin, and which just drive discounting?")
    md, mm = cat_sum["disc"].median(), cat_sum["margin"].median()
    cat_sum["class"] = cat_sum.apply(lambda x: "Star" if x["margin"] >= mm and x["disc"] < md else ("Discount-driven" if x["disc"] >= md else "Weak"), axis=1)
    insight("Star = margin at or above the median and discount below the median. Discount-driven = discount at or above the median. Everything else is Weak.")
    f = px.scatter(cat_sum, x="disc", y="margin", size="rev", color="class", text="category_name", title="Category map: discount vs margin (size = revenue)",
                   color_discrete_map={"Star": GREEN, "Discount-driven": AMBER, "Weak": RED})
    f.update_yaxes(**PCT)
    f.update_traces(textposition="top center")
    show(f, h=440)
    hm = sales.groupby(["category_name", "store_name"])[["profit", "total_amount"]].sum().reset_index()
    hm["margin"] = hm["profit"] / hm["total_amount"]
    show(px.density_heatmap(hm, x="store_name", y="category_name", z="margin", histfunc="avg", title="Margin by category and branch",
                            color_continuous_scale=["#E8F4F8", TEAL, NAVY]), h=440)
    top = sales.groupby("product_name")["profit"].sum().nlargest(10).reset_index()
    show(px.bar(top.sort_values("profit"), x="profit", y="product_name", orientation="h", title="Top 10 products by profit", color_discrete_sequence=[NAVY]))

elif page == "Inventory":
    section("How much inventory is at risk of expiring unsold, and where?")
    c = st.columns(3)
    kpi(c[0], "⏳", "Expiring Inventory Value", f"${risk:,.0f}", "Flagged batches, qty x cost", RED)
    kpi(c[1], "📦", "Flagged Batches", f"{int(stock['at_risk'].sum()):,}", "Expiry risk flag", AMBER)
    kpi(c[2], "🔔", "Items Below Reorder Level", f"{int(stock['below'].sum()):,}", "Need restocking", NAVY)
    by_s = stock.groupby("store_name")["risk_value"].sum().reset_index().sort_values("risk_value")
    if by_s["risk_value"].sum() > 0:
        insight(f"{by_s.iloc[-1]['store_name']} carries the most expiry risk: ${by_s.iloc[-1]['risk_value']:,.0f}.")
    l, r_ = st.columns(2)
    show(px.bar(by_s, x="risk_value", y="store_name", orientation="h", title="Expiry risk by branch", color_discrete_sequence=[RED]), l)
    by_c = stock.groupby("category_name")["risk_value"].sum().reset_index()
    by_c = by_c[by_c["risk_value"] > 0]
    show(px.treemap(by_c, path=["category_name"], values="risk_value", title="Expiry risk by category", color_discrete_sequence=PAL), r_)
    section("Batches closest to expiry")
    with st.container(border=True):
        near = stock[stock["at_risk"]].sort_values("days_to_expiry_flagged").head(15)
        st.dataframe(near[["store_name", "product_name", "batch_number", "quantity", "expiry_date", "days_to_expiry_flagged"]],
                     use_container_width=True, hide_index=True)

elif page == "Branch Explorer":
    names = sorted(sales["store_name"].unique())
    pick = st.selectbox("Choose a branch", names)
    info = store[store["store_name"] == pick].iloc[0]
    s = sales[sales["store_name"] == pick]
    c = st.columns(4)
    kpi(c[0], "💰", "Revenue", f"${s['total_amount'].sum()/1e3:,.0f}K", f"Manager: {info['manager_name']}")
    kpi(c[1], "📈", "Margin", f"{s['profit'].sum() / s['total_amount'].sum():.1%}", f"{info['city']}, {info['region']}", NAVY)
    kpi(c[2], "⏳", "Expiry risk", f"${stock[stock['store_name'] == pick]['risk_value'].sum():,.0f}", "Flagged batches", RED)
    kpi(c[3], "💊", "Prescriptions", f"{(rx['store_name'] == pick).sum():,}", "In selected dates", AMBER)
    mm_ = s.groupby(s["sale_date"].dt.to_period("M").astype(str))[["total_amount", "profit"]].sum().reset_index()
    l, r_ = st.columns(2)
    show(px.line(mm_, x="sale_date", y=["total_amount", "profit"], markers=True, title="Monthly revenue and profit", color_discrete_sequence=[TEAL, NAVY]), l)
    cc = s.groupby("category_name")["total_amount"].sum().reset_index().sort_values("total_amount")
    show(px.bar(cc, x="total_amount", y="category_name", orientation="h", title="Revenue by category", color_discrete_sequence=[TEAL]), r_)

else:
    section("Is pharmacist staffing matched to prescription volume? Which segments and channels matter?")
    rp = rx.groupby("store_name").size().rename("rx").reset_index().merge(
        emp.groupby("store_name")["is_ph"].sum().rename("ph").reset_index(), on="store_name", how="left")
    rp["per_pharm"] = rp["rx"] / rp["ph"].where(rp["ph"] > 0)
    insight("Prescriptions have no pharmacist field, so the ratio is calculated per branch: prescriptions divided by pharmacists at that branch.")
    l, r_ = st.columns(2)
    show(px.bar(rp.sort_values("per_pharm"), x="per_pharm", y="store_name", orientation="h", title="Prescriptions per pharmacist", color_discrete_sequence=[TEAL]), l)
    docs = rx["doctor_name"].value_counts().head(10).rename_axis("doctor").reset_index(name="rx")
    show(px.bar(docs.sort_values("rx"), x="rx", y="doctor", orientation="h", title="Top prescribing doctors", color_discrete_sequence=[NAVY]), r_)
    l, r_ = st.columns(2)
    show(px.pie(sales, names="payment_method", values="total_amount", hole=.55, title="Revenue by payment method", color_discrete_sequence=PAL), l)
    lt = sales.groupby("loyalty_tier")["total_amount"].sum().reset_index()
    show(px.bar(lt, x="loyalty_tier", y="total_amount", title="Revenue by loyalty tier", color_discrete_sequence=[TEAL]), r_)
