import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Pizza Sales Analytics",
    page_icon="🍕",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #fffaf5;
        color: #1f2937;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffedd5;
        border-right: 2px solid #fb923c;
    }

    h1, h2, h3 {
        color: #ea580c !important;
        font-family: 'Poppins', sans-serif;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #fdba74;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
        transition: 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #ea580c;
    }

    .metric-title {
        font-size: 14px;
        color: #9a3412;
        font-weight: 600;
    }

    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #ea580c;
    }

    .chart-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #fed7aa;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():

    df = pd.read_csv("pizza_sales.csv")

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%d-%m-%Y"
    )

    df["hour"] = pd.to_datetime(
        df["order_time"]
    ).dt.hour

    # Profit Calculation
    df["cost"] = (
        df["unit_price"] *
        df["quantity"] * 0.6
    )

    df["profit"] = (
        df["total_price"] -
        df["cost"]
    )

    return df


df = load_data()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("🍕 Pizza Sales Dashboard")

date_range = st.sidebar.date_input(
    "Select Date Range",
    [
        df["order_date"].min(),
        df["order_date"].max()
    ]
)

category = st.sidebar.multiselect(
    "Pizza Category",
    df["pizza_category"].unique(),
    default=df["pizza_category"].unique()
)

size = st.sidebar.multiselect(
    "Pizza Size",
    df["pizza_size"].unique(),
    default=df["pizza_size"].unique()
)

# =====================================================
# FILTER DATA
# =====================================================
filtered_df = df[
    (df["order_date"] >= pd.to_datetime(date_range[0])) &
    (df["order_date"] <= pd.to_datetime(date_range[1])) &
    (df["pizza_category"].isin(category)) &
    (df["pizza_size"].isin(size))
]

# =====================================================
# TITLE
# =====================================================
st.markdown(
    """
    <h1 style='text-align:center;'>
    🍕 PIZZA SALES ANALYTICS DASHBOARD
    </h1>
    """,
    unsafe_allow_html=True
)

st.write("")

# =====================================================
# KPI SECTION
# =====================================================
revenue = filtered_df.total_price.sum()
orders = filtered_df.order_id.nunique()
pizzas_sold = filtered_df.quantity.sum()
profit = filtered_df.profit.sum()

metrics = [
    ("💰 Revenue", f"${revenue:,.2f}"),
    ("📦 Orders", orders),
    ("🍕 Pizzas Sold", pizzas_sold),
    ("📈 Profit", f"${profit:,.2f}")
]

cols = st.columns(4)

for col, (title, value) in zip(cols, metrics):

    with col:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.write("")
st.write("")

# =====================================================
# ROW 1
# =====================================================
col1, col2 = st.columns(2)

# =====================================================
# DAILY REVENUE TREND
# =====================================================
with col1:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("📈 Daily Revenue Trend")

    daily = (
        filtered_df.groupby("order_date")["total_price"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        daily,
        x="order_date",
        y="total_price",
        markers=True,
        color_discrete_sequence=["#ea580c"]
    )

    fig.update_layout(
        template="simple_white",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# HOURLY SALES
# =====================================================
with col2:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("⏰ Hourly Sales Distribution")

    hourly = (
        filtered_df.groupby("hour")["total_price"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        hourly,
        x="hour",
        y="total_price",
        color="total_price",
        color_continuous_scale="Oranges"
    )

    fig.update_layout(
        template="simple_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ROW 2
# =====================================================
col1, col2 = st.columns(2)

# =====================================================
# TOP PIZZAS
# =====================================================
with col1:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("🔥 Top 10 Pizzas by Quantity")

    top_pizzas = (
        filtered_df.groupby("pizza_name")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        top_pizzas,
        x="quantity",
        y="pizza_name",
        orientation="h",
        color="quantity",
        color_continuous_scale="Oranges"
    )

    fig.update_layout(
        template="simple_white",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# CATEGORY SALES
# =====================================================
with col2:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("📊 Revenue by Category")

    category_sales = (
        filtered_df.groupby("pizza_category")["total_price"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        category_sales,
        names="pizza_category",
        values="total_price",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Oranges
    )

    fig.update_layout(
        template="simple_white",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# ROW 3
# =====================================================
col1, col2 = st.columns(2)

# =====================================================
# SIZE REVENUE
# =====================================================
with col1:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("📦 Revenue by Pizza Size")

    size_sales = (
        filtered_df.groupby("pizza_size")["total_price"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        size_sales,
        x="pizza_size",
        y="total_price",
        color="total_price",
        color_continuous_scale="Oranges"
    )

    fig.update_layout(
        template="simple_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# PROFIT BY CATEGORY
# =====================================================
with col2:

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.subheader("💹 Profit by Category")

    profit_cat = (
        filtered_df.groupby("pizza_category")["profit"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        profit_cat,
        x="pizza_category",
        y="profit",
        color="profit",
        color_continuous_scale="Oranges"
    )

    fig.update_layout(
        template="simple_white",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# MONTHLY SALES TREND
# =====================================================
st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("🗓️ Monthly Sales Trend")

filtered_df["month"] = (
    filtered_df["order_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly = (
    filtered_df.groupby("month")["total_price"]
    .sum()
    .reset_index()
)

fig = px.line(
    monthly,
    x="month",
    y="total_price",
    markers=True,
    color_discrete_sequence=["#ea580c"]
)

fig.update_layout(
    template="simple_white",
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# DATA TABLE
# =====================================================
with st.expander("📄 View Filtered Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

# =====================================================
# DOWNLOAD BUTTON
# =====================================================
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Dataset",
    data=csv,
    file_name="pizza_sales_filtered.csv",
    mime="text/csv"
)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")

st.markdown(
    """
    <div style='text-align:center;color:#9a3412;font-size:16px;'>
    ✅ Advanced Dashboard built using Streamlit • Pandas • Plotly
    </div>
    """,
    unsafe_allow_html=True
)