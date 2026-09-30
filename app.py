import base64
import os
import pandas as pd
import plotly.express as px
import streamlit as st

os.chdir(os.path.dirname(os.path.abspath(__file__)))
NAVY, TEAL, AMBER, RED = "#1F2A6B", "#1B8AA6", "#F2A93B", "#E5484D"
PAL = [TEAL, NAVY, "#3BC1D6", AMBER, RED, "#6C7AE0", "#2FB67C"]

st.set_page_config(page_title="Pharmacy Performance Dashboard", page_icon="💊", layout="wide")
st.markdown(f"""
<style>
.stApp{{background:linear-gradient(180deg,#eef3fa,#f8fafd)}}
section[data-testid=stSidebar]{{background:linear-gradient(180deg,{NAVY},#141b4d)}}
section[data-testid=stSidebar] *{{color:#fff!important}}
.kpi{{background:#fff;border-radius:16px;padding:18px 20px;border-left:6px solid {TEAL};
box-shadow:0 6px 18px rgba(31,42,107,.10);transition:transform .2s,box-shadow .2s}}
.kpi:hover{{transform:translateY(-4px);box-shadow:0 12px 26px rgba(31,42,107,.18)}}
.kpi .l{{font-size:13px;color:#6b7690}}.kpi .v{{font-size:30px;font-weight:700;color:{NAVY}}}
.kpi .s{{font-size:12px;color:{TEAL}}}
.insight{{background:{NAVY};color:#fff;border-radius:14px;padding:14px 18px;margin:10px 0 18px;
border-left:6px solid #3BC1D6}}
h1,h2,h3{{color:{NAVY}}}
</style>""", unsafe_allow_html=True)


def kpi(col, label, value, sub="", color=TEAL):
    col.markdown(f"<div class='kpi' style='border-left-color:{color}'><div class='l'>{label}</div>"
                 f"<div class='v'>{value}</div><div class='s'>{sub}</div></div>", unsafe_allow_html=True)


def insight(text):
    st.markdown(f"<div class='insight'>{text}</div>", unsafe_allow_html=True)


def style(fig, h=380):
    fig.update_layout(template="plotly_white", height=h, margin=dict(l=10, r=10, t=50, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      title_font=dict(size=16, color=NAVY))
    return fig


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "1", "yes", "y"])


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


RAW = "https://raw.githubusercontent.com/shahdabdelnabyawaad/EraaSoft/main/"
if st.query_params.get("page") != "overview":
    mer = base64.b64encode(open("logo_white.png", "rb").read()).decode()
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
.era img{height:55px;display:block}
@keyframes mv{to{left:3%;top:4%;transform:translate(0,0) scale(.75)}}
.mid{position:absolute;inset:0;z-index:3;display:flex;flex-direction:column;align-items:center;justify-content:center;
gap:26px;opacity:0;animation:fi .9s ease-in-out 2.6s forwards}
.mid img.m{height:150px;filter:drop-shadow(0 0 28px rgba(59,193,214,.5))}
.tb{padding:16px 30px;background:rgba(11,19,43,.7);border:1px solid rgba(0,168,204,.45);border-radius:16px;
box-shadow:0 8px 25px rgba(0,0,0,.3);color:#fff;font-size:38px;font-weight:800;letter-spacing:.8px}
.go{display:inline-block;padding:14px 38px;border-radius:999px;background:#3BC1D6;color:#0b1033!important;
font-weight:700;font-size:18px;text-decoration:none!important;box-shadow:0 0 0 0 rgba(59,193,214,.6);
animation:pulse 2s infinite;transition:transform .2s}
.go:hover{transform:scale(1.08)}
@keyframes pulse{70%{box-shadow:0 0 0 18px rgba(59,193,214,0)}100%{box-shadow:0 0 0 0 rgba(59,193,214,0)}}
.lg{position:absolute;z-index:4;background:rgba(255,255,255,.96);padding:9px 16px;border-radius:13px;
box-shadow:0 7px 20px rgba(0,0,0,.3);opacity:0;animation:fi .8s ease-in-out 2.8s forwards}
.lg img{height:42px;display:block}
.ic{top:4%;right:3%}.dg{bottom:4%;left:3%;animation-delay:3s}
@keyframes fi{to{opacity:1}}
</style>
<div class="cv"><div class="ov"></div>
<div class="era"><img src="__RAW__Logo%20EraaSoft.webp"></div>
<div class="mid"><img class="m" src="data:image/png;base64,__MER__">
<div class="tb">Pharmacy Performance Dashboard</div>
<a class="go" href="?page=overview" target="_self">Open dashboard</a></div>
<div class="lg ic"><img src="__RAW__Logo%20icareer.webp"></div>
<div class="lg dg"><img src="__RAW__Logo%20Digitera.png"></div></div>"""
    st.markdown(html.replace("__RAW__", RAW).replace("__MER__", mer), unsafe_allow_html=True)
    st.stop()


sales, stock, rx, emp, store = load()

with st.sidebar:
    st.image("logo_white.png", use_container_width=True)
    page = st.radio("Navigate", ["Overview", "Stores", "Categories", "Inventory", "People & Customers", "Branch Explorer"])
    st.markdown("<a href='?' target='_self'>Back to cover</a>", unsafe_allow_html=True)
    stores = st.multiselect("Branches", sorted(sales["store_name"].unique()))
    d0, d1 = sales["sale_date"].min().date(), sales["sale_date"].max().date()
    dates = st.date_input("Date range", (d0, d1), min_value=d0, max_value=d1)

if stores:
    sales, stock, rx, emp = [d[d["store_name"].isin(stores)] for d in (sales, stock, rx, emp)]
if len(dates) == 2:
    a, b = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
    sales = sales[sales["sale_date"].between(a, b)]
    rx = rx[rx["issue_date"].between(a, b)]

rev, prof = sales["total_amount"].sum(), sales["profit"].sum()
margin = prof / rev if rev else 0
pharm = int(emp["is_ph"].sum())
cnt = sales.dropna(subset=["customer_id"]).groupby("customer_id")["sale_id"].transform("count")
rep_share = sales.dropna(subset=["customer_id"]).loc[cnt > 1, "total_amount"].sum() / rev if rev else 0
st_sum = sales.groupby("store_name").agg(rev=("total_amount", "sum"), prof=("profit", "sum"),
                                          disc=("discount_pct", "mean"), loss=("profit", lambda s: (s < 0).mean())).reset_index()
st_sum["margin"] = st_sum["prof"] / st_sum["rev"]
cat_sum = sales.groupby("category_name").agg(rev=("total_amount", "sum"), prof=("profit", "sum"),
                                              disc=("discount_pct", "mean")).reset_index()
cat_sum["margin"] = cat_sum["prof"] / cat_sum["rev"]
risk = stock["risk_value"].sum()

h1, h2 = st.columns([1, 5])
h1.image("logo.png", width=170)
h2.title("Pharmacy Performance Dashboard")

if page == "Overview":
    c = st.columns(4)
    kpi(c[0], "Total Revenue", f"${rev/1e6:.2f}M", "All selected branches")
    kpi(c[1], "Total Profit", f"${prof/1e6:.2f}M", f"Overall margin {margin:.1%}", NAVY)
    kpi(c[2], "Average Discount", f"{sales['discount_pct'].mean():.1f}%", f"{(sales['profit']<0).mean():.1%} of sales lose money", AMBER)
    kpi(c[3], "Expiring Inventory at Risk", f"${risk:,.0f}", "Flagged batches at cost", RED)
    c = st.columns(4)
    top_s = st_sum.sort_values("rev").iloc[-1] if len(st_sum) else None
    top_c = cat_sum.sort_values("rev").iloc[-1] if len(cat_sum) else None
    kpi(c[0], "Top Branch by Revenue", top_s["store_name"] if top_s is not None else "-", f"${top_s['rev']/1e3:,.0f}K, margin {top_s['margin']:.1%}" if top_s is not None else "")
    kpi(c[1], "Top Category by Revenue", top_c["category_name"] if top_c is not None else "-", f"${top_c['rev']/1e3:,.0f}K, margin {top_c['margin']:.1%}" if top_c is not None else "", NAVY)
    kpi(c[2], "Prescriptions per Pharmacist", f"{len(rx)/pharm:,.0f}" if pharm else "-", f"{pharm} pharmacists", TEAL)
    kpi(c[3], "Repeat-Customer Revenue Share", f"{rep_share:.1%}", "Customers with 2+ purchases", NAVY)
    if len(st_sum):
        best, worst = st_sum.sort_values("margin").iloc[-1], st_sum.sort_values("margin").iloc[0]
        insight(f"{best['store_name']} has the best margin ({best['margin']:.1%}); {worst['store_name']} has the lowest ({worst['margin']:.1%}).")
    m = sales.groupby(sales["sale_date"].dt.to_period("M").astype(str))[["total_amount", "profit"]].sum().reset_index()
    st.plotly_chart(style(px.area(m, x="sale_date", y=["total_amount", "profit"], title="Revenue and profit by month",
                                  color_discrete_sequence=[TEAL, NAVY])), use_container_width=True)
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.bar(st_sum.sort_values("rev"), x="rev", y="store_name", orientation="h", color="margin",
                                title="Revenue by branch (color = margin)", color_continuous_scale=["#E8F4F8", TEAL, NAVY])), use_container_width=True)
    r_.plotly_chart(style(px.bar(cat_sum.sort_values("rev"), x="rev", y="category_name", orientation="h", color="margin",
                                 title="Revenue by category (color = margin)", color_continuous_scale=["#E8F4F8", TEAL, NAVY])), use_container_width=True)

elif page == "Stores":
    st.subheader("Which branches are really profitable once discounting is counted?")
    worst = st_sum.sort_values("loss").iloc[-1]
    insight(f"{worst['store_name']} has the most loss-making sales ({worst['loss']:.1%}) with an average discount of {worst['disc']:.1f}%.")
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.bar(st_sum.sort_values("margin"), x="margin", y="store_name", orientation="h",
                                title="Margin by branch", color_discrete_sequence=[TEAL])), use_container_width=True)
    r_.plotly_chart(style(px.scatter(st_sum, x="disc", y="margin", size="rev", color="loss", text="store_name",
                                     title="Discount vs margin (size = revenue, color = loss-making share)",
                                     color_continuous_scale=["#2FB67C", AMBER, RED])), use_container_width=True)
    st.dataframe(st_sum.rename(columns={"rev": "Revenue", "prof": "Profit", "disc": "Avg discount %", "loss": "Loss-making sales", "margin": "Margin"})
                 .style.format({"Revenue": "${:,.0f}", "Profit": "${:,.0f}", "Avg discount %": "{:.1f}", "Loss-making sales": "{:.1%}", "Margin": "{:.1%}"}),
                 use_container_width=True)

    st.markdown("#### Discount simulator")
    cut = st.slider("Reduce every discount by (%)", 0, 50, 20, 5)
    sim_rev = (sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100 * (1 - cut / 100))).sum()
    sim_prof = sim_rev - sales["cost_amount"].sum()
    c = st.columns(3)
    kpi(c[0], "Current profit", f"${prof:,.0f}", "")
    kpi(c[1], "Simulated profit", f"${sim_prof:,.0f}", f"Discounts cut by {cut}%", NAVY)
    kpi(c[2], "Profit change", f"{sim_prof - prof:+,.0f}", "Assumes the same quantities are sold", AMBER)

elif page == "Categories":
    st.subheader("Which categories drive revenue and margin, and which just drive discounting?")
    md, mm = cat_sum["disc"].median(), cat_sum["margin"].median()
    cat_sum["class"] = cat_sum.apply(lambda x: "Star" if x["margin"] >= mm and x["disc"] < md else ("Discount-driven" if x["disc"] >= md else "Weak"), axis=1)
    insight("Classification rule: Star = margin at or above the median and discount below the median. Discount-driven = discount at or above the median. Everything else is Weak.")
    st.plotly_chart(style(px.scatter(cat_sum, x="disc", y="margin", size="rev", color="class", text="category_name",
                                     title="Category map: discount vs margin (size = revenue)",
                                     color_discrete_map={"Star": "#2FB67C", "Discount-driven": AMBER, "Weak": RED}), 440), use_container_width=True)
    hm = sales.groupby(["category_name", "store_name"])[["profit", "total_amount"]].sum().reset_index()
    hm["margin"] = hm["profit"] / hm["total_amount"]
    st.plotly_chart(style(px.density_heatmap(hm, x="store_name", y="category_name", z="margin", histfunc="avg",
                                             title="Margin by category and branch", color_continuous_scale=["#E8F4F8", TEAL, NAVY]), 440), use_container_width=True)
    top = sales.groupby("product_name")["profit"].sum().nlargest(10).reset_index()
    st.plotly_chart(style(px.bar(top.sort_values("profit"), x="profit", y="product_name", orientation="h", title="Top 10 products by profit",
                                 color_discrete_sequence=[NAVY])), use_container_width=True)

elif page == "Inventory":
    st.subheader("How much inventory is at risk of expiring unsold, and where?")
    c = st.columns(3)
    kpi(c[0], "Expiring Inventory Value", f"${risk:,.0f}", "Flagged batches, qty x cost", RED)
    kpi(c[1], "Flagged Batches", f"{int(stock['at_risk'].sum()):,}", "Expiry risk flag", AMBER)
    kpi(c[2], "Items Below Reorder Level", f"{int(stock['below'].sum()):,}", "Need restocking", NAVY)
    by_s = stock.groupby("store_name")["risk_value"].sum().reset_index().sort_values("risk_value")
    if by_s["risk_value"].sum() > 0:
        insight(f"{by_s.iloc[-1]['store_name']} carries the most expiry risk: ${by_s.iloc[-1]['risk_value']:,.0f}.")
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.bar(by_s, x="risk_value", y="store_name", orientation="h", title="Expiry risk by branch", color_discrete_sequence=[RED])), use_container_width=True)
    by_c = stock.groupby("category_name")["risk_value"].sum().reset_index()
    r_.plotly_chart(style(px.treemap(by_c[by_c["risk_value"] > 0], path=["category_name"], values="risk_value", title="Expiry risk by category",
                                     color_discrete_sequence=PAL)), use_container_width=True)
    near = stock[stock["at_risk"]].sort_values("days_to_expiry_flagged").head(15)
    st.markdown("#### Batches closest to expiry")
    st.dataframe(near[["store_name", "product_name", "batch_number", "quantity", "expiry_date", "days_to_expiry_flagged"]], use_container_width=True)

elif page == "Branch Explorer":
    names = sorted(sales["store_name"].unique())
    if not names:
        st.warning("No data for the selected filters.")
        st.stop()
    pick = st.selectbox("Choose a branch", names)
    info = store[store["store_name"] == pick].iloc[0]
    s = sales[sales["store_name"] == pick]
    c = st.columns(4)
    kpi(c[0], "Revenue", f"${s['total_amount'].sum()/1e3:,.0f}K", f"Manager: {info['manager_name']}")
    kpi(c[1], "Margin", f"{s['profit'].sum() / s['total_amount'].sum():.1%}", f"{info['city']}, {info['region']}", NAVY)
    kpi(c[2], "Expiry risk", f"${stock[stock['store_name'] == pick]['risk_value'].sum():,.0f}", "Flagged batches", RED)
    kpi(c[3], "Prescriptions", f"{(rx['store_name'] == pick).sum():,}", "In selected dates", AMBER)
    mm = s.groupby(s["sale_date"].dt.to_period("M").astype(str))[["total_amount", "profit"]].sum().reset_index()
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.line(mm, x="sale_date", y=["total_amount", "profit"], markers=True, title="Monthly revenue and profit",
                                 color_discrete_sequence=[TEAL, NAVY])), use_container_width=True)
    cc = s.groupby("category_name")["total_amount"].sum().reset_index().sort_values("total_amount")
    r_.plotly_chart(style(px.bar(cc, x="total_amount", y="category_name", orientation="h", title="Revenue by category",
                                 color_discrete_sequence=[TEAL])), use_container_width=True)

else:
    st.subheader("Is pharmacist staffing matched to prescription volume? Which segments and channels matter?")
    rp = rx.groupby("store_name").size().rename("rx").reset_index().merge(
        emp.groupby("store_name")["is_ph"].sum().rename("ph").reset_index(), on="store_name", how="left")
    rp["per_pharm"] = rp["rx"] / rp["ph"].where(rp["ph"] > 0)
    insight("Prescriptions have no pharmacist field, so the ratio is calculated per branch: prescriptions divided by pharmacists working at that branch.")
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.bar(rp.sort_values("per_pharm"), x="per_pharm", y="store_name", orientation="h",
                                title="Prescriptions per pharmacist", color_discrete_sequence=[TEAL])), use_container_width=True)
    docs = rx["doctor_name"].value_counts().head(10).rename_axis("doctor").reset_index(name="rx")
    r_.plotly_chart(style(px.bar(docs.sort_values("rx"), x="rx", y="doctor", orientation="h", title="Top prescribing doctors",
                                 color_discrete_sequence=[NAVY])), use_container_width=True)
    l, r_ = st.columns(2)
    l.plotly_chart(style(px.pie(sales, names="payment_method", values="total_amount", hole=.55, title="Revenue by payment method",
                                color_discrete_sequence=PAL)), use_container_width=True)
    lt = sales.groupby("loyalty_tier")["total_amount"].sum().reset_index()
    r_.plotly_chart(style(px.bar(lt, x="loyalty_tier", y="total_amount", title="Revenue by loyalty tier",
                                 color_discrete_sequence=[TEAL])), use_container_width=True)
