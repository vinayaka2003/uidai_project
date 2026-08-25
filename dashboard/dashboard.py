import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------------------------------
# PAGE CONFIG & PROFESSIONAL LIGHT MODE THEME
# -----------------------------------------------------
st.set_page_config(
    page_title="UIDAI Aadhaar Mismatch & Migration Analytics",
    layout="wide"
)

# Custom CSS to force clean Light Mode backgrounds and high-contrast dark text
# (Protects readability even if the client's browser is set to Dark Mode)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Font Override */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Force Light Mode background on app canvas */
    .stApp {
        background-color: #F8FAFC !important;
    }
    
    /* Force Light Mode background on sidebar */
    [data-testid="stSidebar"] {
        background-color: #F1F5F9 !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* Hide top header bar (removes the dark top strip) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    /* FORCE DARK TEXT COLOR FOR READABILITY (OVERRIDING BROWSER DARK MODE TEXTS) */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp p, .stApp label, .stApp li, .stApp span, .stApp p *, .stApp label *, 
    .stApp details summary, .stApp details div, .stApp div.stMarkdown * {
        color: #0F172A !important;
    }
    
    /* Force dark text inside forms, inputs, dropdowns, and widgets */
    div[data-baseweb="select"] * {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    
    /* Ensure selectbox dropdown items are highly visible */
    ul[role="listbox"] li {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #F1F5F9 !important;
    }

    /* Style Streamlit expander to use Light Mode colors instead of default dark */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    
    div[data-testid="stExpander"] details summary {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-radius: 8px 8px 8px 8px !important;
    }
    
    div[data-testid="stExpander"] details[open] summary {
        border-bottom: 1px solid #E2E8F0 !important;
        border-radius: 8px 8px 0 0 !important;
    }
    
    div[data-testid="stExpander"] details div[role="region"] {
        background-color: #FFFFFF !important;
        padding: 16px !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* Elegant Custom Metric Card Layout */
    .metric-container {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 16px;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.08);
        border-color: #CBD5E1;
    }
    
    /* Left-accent color indicators */
    .metric-container.usage { border-left: 5px solid #2563EB !important; }
    .metric-container.enrolment { border-left: 5px solid #F59E0B !important; }
    .metric-container.ratio-stable { border-left: 5px solid #10B981 !important; }
    .metric-container.ratio-warning { border-left: 5px solid #D97706 !important; }
    .metric-container.ratio-danger { border-left: 5px solid #EF4444 !important; }
    .metric-container.districts { border-left: 5px solid #64748B !important; }
    
    .metric-container h4 {
        margin: 0 !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: #64748B !important;
    }
    
    .metric-container h2 {
        margin: 8px 0 4px 0 !important;
        font-size: 2.3rem !important;
        font-weight: 700 !important;
        line-height: 1 !important;
        color: #0F172A !important;
    }
    
    .metric-container p {
        margin: 0 !important;
        font-size: 0.85rem !important;
        color: #475569 !important;
        font-weight: 500 !important;
    }

    /* Style Streamlit Tabs for modern look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E2E8F0 !important;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: transparent !important;
        color: #475569 !important;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #0F172A !important;
        background-color: rgba(255, 255, 255, 0.4) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }

    /* Styled Informational Banners */
    .info-box {
        background-color: #EFF6FF !important;
        border-left: 4px solid #2563EB !important;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #1E3A8A !important;
        font-size: 0.95rem;
    }
    
    .info-box h5, .info-box strong, .info-box li, .info-box p {
        color: #1E3A8A !important;
    }

    /* Mobile Responsiveness Rules */
    @media (max-width: 768px) {
        .metric-container {
            padding: 16px !important;
            margin-bottom: 12px !important;
        }
        .metric-container h2 {
            font-size: 1.8rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            padding: 4px !important;
            border-radius: 8px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 0.8rem !important;
            border-radius: 6px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# CORE ANALYTICAL LOGIC
# -----------------------------------------------------
def simulate_policy_impact(
    df: pd.DataFrame,
    new_centers: int,
    extra_hours: int,
    extra_operators: int
) -> pd.DataFrame:
    """
    Simulates policy interventions and estimates impact on migration pressure
    """
    df = df.copy()

    # --- Assumptions (Explainable & Adjustable) ---
    center_capacity_boost = new_centers * 0.08      # 8% per new center
    hours_capacity_boost = extra_hours * 0.03       # 3% per extra hour
    operator_capacity_boost = extra_operators * 0.015  # 1.5% per operator

    total_capacity_boost = (
        center_capacity_boost +
        hours_capacity_boost +
        operator_capacity_boost
    )

    # Cap max effect to avoid unrealistic results
    total_capacity_boost = min(total_capacity_boost, 0.5)

    # Reduce effective usage pressure
    df["simulated_usage_pressure"] = (
        df["usage_to_enrolment_ratio"] * (1 - total_capacity_boost)
    )

    # Estimated wait time improvement (%)
    df["estimated_wait_time_reduction"] = total_capacity_boost * 100

    return df

def calculate_migration_risk_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Migration Risk Index (MRI) at district-month level
    """
    df = df.sort_values(["state", "district", "month"]).copy()

    # 1️⃣ Month-on-Month Usage Growth
    df["usage_growth"] = (
        df.groupby(["state", "district"])["total_usage"]
        .pct_change()
        .fillna(0)
        .clip(lower=0)   # negative growth not needed for risk
    )

    # 2️⃣ Population Sensitivity Factor
    df["population_sensitivity"] = 1.0
    df.loc[df["total_enrolment"] < 10000, "population_sensitivity"] = 1.3
    df.loc[df["total_enrolment"] < 5000, "population_sensitivity"] = 1.5

    # 3️⃣ Migration Risk Index (MRI)
    df["migration_risk_index"] = (
        df["usage_to_enrolment_ratio"]
        * (1 + df["usage_growth"])
        * df["population_sensitivity"]        
    )

    # 4️⃣ Risk Category
    df["migration_risk_level"] = pd.cut(
        df["migration_risk_index"],
        bins=[-1, 1.2, 2.5, float("inf")],
        labels=["🟢 Stable", "🟨 Medium Risk", "🔴 High Risk"]
    )

    return df

# -----------------------------------------------------
# DATA INGESTION (SPEED OPTIMIZED CACHING)
# -----------------------------------------------------
@st.cache_data
def load_data():
    path = os.path.join("data", "processed", "enrolment_usage_mismatch.csv")
    df = pd.read_csv(path)
    df["month"] = pd.to_datetime(df["month"])
    return df

@st.cache_data
def get_processed_data():
    """Calculates risk index once and caches the result for sub-20ms responsiveness"""
    df_raw = load_data()
    return calculate_migration_risk_index(df_raw)

@st.cache_data
def load_forecast_data():
    path = os.path.join("analysis", "forecast_outputs", "national_usage_trend_2025.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["month"] = pd.to_datetime(df["month"])
        return df
    return None

# Load datasets
try:
    df = get_processed_data()
except Exception as e:
    st.error(f"Error loading processed mismatch data: {e}")
    st.info("Please run the data cleaning pipeline to generate the required datasets.")
    st.stop()

df_forecast = load_forecast_data()

def has_data(d):
    return d is not None and not d.empty

# -----------------------------------------------------
# SIDEBAR FILTERS (STANDARDIZED AND CLEANED)
# -----------------------------------------------------
st.sidebar.markdown("### 🔎 Regional Filters")

states_list = sorted(df["state"].dropna().unique())
state = st.sidebar.selectbox("Select State", ["All India"] + states_list)

filtered_df = df.copy()
if state != "All India":
    filtered_df = filtered_df[filtered_df["state"] == state]

districts_list = sorted(filtered_df["district"].dropna().unique())
district = st.sidebar.selectbox("Select District", ["All Districts"] + districts_list)

if district != "All Districts":
    filtered_df = filtered_df[filtered_df["district"] == district]

# -----------------------------------------------------
# HEADER & INTRODUCTORY GUIDE
# -----------------------------------------------------
st.markdown("<h1 style='color: #0F172A; font-weight: 700; margin-bottom: 5px;'>Aadhaar Migration & Infrastructure Stress Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 1.15rem; margin-bottom: 25px;'>Analyzing spatial discrepancies in Aadhaar enrolments vs. authentication events to monitor population shifts.</p>", unsafe_allow_html=True)

with st.expander("New to this dashboard? Click here to understand what this data shows", expanded=True):
    st.markdown("""
    <div class="info-box">
        <h5>💡 Introduction to Aadhaar-based Migration Analysis</h5>
        Aadhaar is India's national biometric identification system. When citizens relocate for employment, education, or other reasons, they carry their Aadhaar. 
        By comparing <strong>where people originally enrolled</strong> (where their identity was created) vs <strong>where they actually use it</strong> (where they live and access services), we can detect local migration movements in real-time.
    </div>
    
    <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 15px;">
        <div style="flex: 1; min-width: 250px; background-color: #FFFFFF; border-left: 4px solid #10B981; padding: 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <strong style="color: #0F766E;">📈 Mismatch Ratio (Usage/Enrolment)</strong><br/>
            <ul>
                <li><strong>Ratio = 1.0</strong>: Perfect balance. The number of people authenticating matches the registered population base.</li>
                <li><strong>Ratio > 1.2</strong>: High usage pressure. Indicates citizens are <strong>moving into</strong> this district, straining local services.</li>
                <li><strong>Ratio < 0.8</strong>: Low usage pressure. Suggests out-migration.</li>
            </ul>
        </div>
        <div style="flex: 1; min-width: 250px; background-color: #FFFFFF; border-left: 4px solid #EF4444; padding: 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <strong style="color: #B91C1C;">🔴 Migration Risk Index (MRI)</strong><br/>
            An index tracking infrastructure strain by multiplying the mismatch ratio by the Month-on-Month growth rate.
            <ul>
                <li><strong>🔴 High Risk</strong>: Immediate capacity stress on local Aadhaar centers.</li>
                <li><strong>🟨 Medium Risk</strong>: Active monitoring recommended.</li>
                <li><strong>🟢 Stable</strong>: Balanced usage pattern.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# -----------------------------------------------------
# PLOTLY COLOR THEME CONFIG (HIGH CONTRAST & VISIBILITY)
# -----------------------------------------------------
def apply_premium_layout(fig, title_text, xaxis_title="", yaxis_title=""):
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(size=16, family="Plus Jakarta Sans", color="#0F172A")
        ),
        xaxis=dict(
            title=dict(
                text=xaxis_title,
                font=dict(family="Plus Jakarta Sans", color="#475569")
            ),
            gridcolor="#E2E8F0",
            linecolor="#E2E8F0",
            tickfont=dict(family="Plus Jakarta Sans", color="#475569")
        ),
        yaxis=dict(
            title=dict(
                text=yaxis_title,
                font=dict(family="Plus Jakarta Sans", color="#475569")
            ),
            gridcolor="#E2E8F0",
            linecolor="#E2E8F0",
            tickfont=dict(family="Plus Jakarta Sans", color="#475569")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=12, color="#475569"),
        margin=dict(l=40, r=40, t=60, b=40),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Plus Jakarta Sans")
    )
    return fig

# -----------------------------------------------------
# TAB DESIGN & IMPLEMENTATION
# -----------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Mismatch Overview", 
    "🚨 Migration Risk Analysis", 
    "🏛️ Policy Simulator", 
    "🔮 Trend Forecasting"
])

# -----------------------------------------------------
# TAB 1: MISMATCH OVERVIEW
# -----------------------------------------------------
with tab1:
    st.markdown("<p style='font-size: 1.1rem; color: #475569; margin-bottom: 20px;'>Summary of biometric and demographic authentication requests vs. registered local residents.</p>", unsafe_allow_html=True)
    
    # KPIs calculations
    if has_data(filtered_df):
        total_usage = int(filtered_df["total_usage"].sum())
        total_enrol = int(filtered_df["total_enrolment"].fillna(0).sum())
        ratio = total_usage / total_enrol if total_enrol > 0 else 0
        districts_count = filtered_df["district"].nunique()
    else:
        total_usage = total_enrol = ratio = districts_count = 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-container usage">
            <h4>Total Aadhaar Usage</h4>
            <h2>{total_usage:,}</h2>
            <p>Authentication requests</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-container enrolment">
            <h4>Total Enrolment</h4>
            <h2>{total_enrol:,}</h2>
            <p>Registered base population</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        # Determine color block class based on ratio
        ratio_class = "ratio-danger" if ratio > 1.2 else ("ratio-stable" if ratio > 0.8 else "ratio-warning")
        st.markdown(f"""
        <div class="metric-container {ratio_class}">
            <h4>Usage / Enrolment Ratio</h4>
            <h2>{ratio:.2f}</h2>
            <p>NMR (Normalized to baseline)</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-container districts">
            <h4>Districts Covered</h4>
            <h2>{districts_count}</h2>
            <p>Reporting regions</p>
        </div>
        """, unsafe_allow_html=True)

    # 1. Line Trend Plot
    st.markdown("#### 📈 Monthly Authentication vs Enrolment Trend")
    trend_df = (
        filtered_df
        .groupby("month")[["total_usage", "total_enrolment"]]
        .sum()
        .reset_index()
        .sort_values("month")
    )
    
    if has_data(trend_df):
        trend_df["month_str"] = trend_df["month"].dt.strftime("%Y-%b")
        fig_trend = px.line(
            trend_df,
            x="month_str",
            y=["total_usage", "total_enrolment"],
            markers=True,
            labels={"value": "Total Count", "month_str": "Month", "variable": "Metric"},
            color_discrete_map={"total_usage": "#2563EB", "total_enrolment": "#F59E0B"},
            template="plotly_white"
        )
        fig_trend = apply_premium_layout(fig_trend, f"Monthly Usage vs Enrolment Trend ({state})")
        fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("No trend data available for the selected filters.")

    # 2. Demand Distribution & Regional Insights
    st.divider()
    col_dist, col_rank = st.columns(2)
    
    with col_dist:
        st.markdown("#### 📊 Demand Pressure Distribution")
        temp = filtered_df.copy()
        temp["ratio_visual"] = temp["usage_to_enrolment_ratio"].clip(0, 5)
        if has_data(temp):
            fig_hist = px.histogram(
                temp,
                x="ratio_visual",
                nbins=30,
                labels={"ratio_visual": "Usage / Enrolment Ratio (clipped)"},
                color_discrete_sequence=["#2563EB"],
                template="plotly_white"
            )
            fig_hist = apply_premium_layout(fig_hist, "Distribution of Region-Month Ratios (Capped at 5.0)")
            st.plotly_chart(fig_hist, use_container_width=True)
            
    with col_rank:
        st.markdown("#### 🏆 Top Districts by Mismatch Pressure")
        district_rank = (
            filtered_df.groupby("district")["usage_to_enrolment_ratio"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        if has_data(district_rank):
            fig_dist = px.bar(
                district_rank,
                x="usage_to_enrolment_ratio",
                y="district",
                orientation="h",
                labels={"usage_to_enrolment_ratio": "Ratio Value", "district": "District"},
                color="usage_to_enrolment_ratio",
                color_continuous_scale=px.colors.sequential.YlOrRd,
                template="plotly_white"
            )
            fig_dist = apply_premium_layout(fig_dist, "Top 10 Districts by Avg Usage-to-Enrolment Ratio")
            fig_dist.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_dist, use_container_width=True)

# -----------------------------------------------------
# TAB 2: MIGRATION RISK ANALYSIS
# -----------------------------------------------------
with tab2:
    st.markdown("<p style='font-size: 1.1rem; color: #475569; margin-bottom: 20px;'>Assessing capacity constraints based on MoM authentication spikes and active ratios.</p>", unsafe_allow_html=True)

    if has_data(filtered_df):
        avg_mri = filtered_df["migration_risk_index"].mean()
        high_risk_districts = (
            filtered_df[filtered_df["migration_risk_level"] == "🔴 High Risk"]
            ["district"]
            .nunique()
        )
    else:
        avg_mri = 0
        high_risk_districts = 0

    k1, k2 = st.columns(2)
    with k1:
        st.markdown(f"""
        <div class="metric-container districts">
            <h4>Average Migration Risk Index (MRI)</h4>
            <h2>{avg_mri:.2f}</h2>
            <p>Overall baseline stress factor</p>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-container ratio-danger">
            <h4>High Stress Districts</h4>
            <h2>{high_risk_districts}</h2>
            <p>Flagged under 🔴 High Risk categories</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    c_pie, c_bar = st.columns(2)
    
    with c_pie:
        st.markdown("#### 🥧 Overall Migration Signal Share")
        signal_df = (
            filtered_df["migration_signal"]
            .value_counts()
            .reset_index()
        )
        signal_df.columns = ["Category", "Count"]
        if has_data(signal_df):
            fig_signal = px.pie(
                signal_df,
                names="Category",
                values="Count",
                color="Category",
                color_discrete_map={
                    "High Usage vs Enrolment (Possible In-migration)": "#EF4444",
                    "Low Usage vs Enrolment (Possible Out-migration)": "#F59E0B",
                    "Balanced": "#10B981"
                },
                template="plotly_white"
            )
            fig_signal = apply_premium_layout(fig_signal, "Migration Signal Breakdown")
            st.plotly_chart(fig_signal, use_container_width=True)
            
    with c_bar:
        st.markdown("#### 🧭 Top High-Stress Districts (MRI)")
        risk_view = (
            filtered_df.groupby(["state", "district", "migration_risk_level"])
            ["migration_risk_index"]
            .mean()
            .reset_index()
            .sort_values("migration_risk_index", ascending=False)
            .head(10)
        )
        if has_data(risk_view):
            fig_mri = px.bar(
                risk_view,
                x="migration_risk_index",
                y="district",
                color="migration_risk_level",
                orientation="h",
                labels={"migration_risk_index": "Risk Index", "district": "District"},
                color_discrete_map={
                    "🔴 High Risk": "#EF4444",
                    "🟨 Medium Risk": "#F59E0B",
                    "🟢 Stable": "#10B981"
                },
                template="plotly_white"
            )
            fig_mri = apply_premium_layout(fig_mri, "Top Districts by Migration Risk Index")
            fig_mri.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_mri, use_container_width=True)

    st.divider()
    st.markdown("#### 📋 Detailed Data Explorer")
    display_cols = [
        "month", "state", "district",
        "total_usage", "total_enrolment",
        "usage_to_enrolment_ratio",
        "migration_risk_index",
        "migration_risk_level"
    ]
    
    st.dataframe(
        filtered_df[display_cols].sort_values("migration_risk_index", ascending=False),
        use_container_width=True
    )
    
    st.download_button(
        "📥 Download Filtered Mismatch Data (CSV)",
        filtered_df[display_cols].to_csv(index=False),
        "uidai_migration_risk_data.csv",
        "text/csv"
    )

# -----------------------------------------------------
# TAB 3: POLICY IMPACT SIMULATOR
# -----------------------------------------------------
with tab3:
    st.markdown("### 🏛️ Policy Impact Simulator (What-If Analysis)")
    st.markdown("""
    Model local upgrades to physical center infrastructures. Adjust the sliders to simulate changes in physical counters,
    working hours, or operators, and observe expected pressure reductions.
    """)

    # Interactive Simulator Sliders
    c_sliders, c_results = st.columns([1, 2])
    
    with c_sliders:
        st.markdown("<div style='background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown("<strong style='color: #0F172A;'>⚙️ Adjust Policy Sliders</strong>", unsafe_allow_html=True)
        new_centers = st.slider("📍 Add Aadhaar Centres (per district)", 0, 10, 2)
        extra_hours = st.slider("🕒 Increase Working Hours (hrs/day)", 0, 6, 1)
        extra_operators = st.slider("👥 Add Operators (per district)", 0, 30, 10)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_results:
        sim_df = simulate_policy_impact(
            filtered_df,
            new_centers,
            extra_hours,
            extra_operators
        )
        
        if has_data(sim_df):
            avg_pressure_before = filtered_df["usage_to_enrolment_ratio"].mean()
            avg_pressure_after = sim_df["simulated_usage_pressure"].mean()
            avg_wait_reduction = sim_df["estimated_wait_time_reduction"].mean()

            k_b, k_a, k_w = st.columns(3)
            with k_b:
                st.markdown(f"""
                <div class="metric-container usage">
                    <h4>Pressure (Before)</h4>
                    <h2>{avg_pressure_before:.2f}</h2>
                    <p>Original mismatch NMR</p>
                </div>
                """, unsafe_allow_html=True)
            with k_a:
                st.markdown(f"""
                <div class="metric-container ratio-stable">
                    <h4>Pressure (After)</h4>
                    <h2>{avg_pressure_after:.2f}</h2>
                    <p>Simulated mismatch NMR</p>
                </div>
                """, unsafe_allow_html=True)
            with k_w:
                st.markdown(f"""
                <div class="metric-container usage" style="border-left: 5px solid #2563EB;">
                    <h4>Wait-Time Cut</h4>
                    <h2>{avg_wait_reduction:.1f}%</h2>
                    <p>Expected wait time reduction</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Select filter combinations containing active data to simulate.")

    if has_data(sim_df):
        st.divider()
        st.markdown("#### 📊 Policy Impact: Top 10 High-Pressure Districts Before vs After")
        impact_view = (
            sim_df.groupby("district")[["usage_to_enrolment_ratio", "simulated_usage_pressure"]]
            .mean()
            .reset_index()
            .sort_values("usage_to_enrolment_ratio", ascending=False)
            .head(10)
        )
        
        # Melt the dataframe for plotting double bars
        melted_impact = pd.melt(
            impact_view,
            id_vars=["district"],
            value_vars=["usage_to_enrolment_ratio", "simulated_usage_pressure"],
            var_name="Scenario",
            value_name="Usage Pressure"
        )
        melted_impact["Scenario"] = melted_impact["Scenario"].replace({
            "usage_to_enrolment_ratio": "Before Intervention",
            "simulated_usage_pressure": "After Intervention"
        })
        
        fig_policy = px.bar(
            melted_impact,
            x="district",
            y="Usage Pressure",
            color="Scenario",
            barmode="group",
            labels={"district": "District", "Usage Pressure": "Usage / Enrolment Ratio"},
            color_discrete_map={"Before Intervention": "#EF4444", "After Intervention": "#10B981"},
            template="plotly_white"
        )
        fig_policy = apply_premium_layout(fig_policy, "Comparison of Regional Mismatch Stress Levels")
        st.plotly_chart(fig_policy, use_container_width=True)

# -----------------------------------------------------
# TAB 4: TIME-SERIES FORECASTING
# -----------------------------------------------------
with tab4:
    st.markdown("### 🔮 National Aadhaar Usage Trend Forecasting (ARIMA Model)")
    st.markdown("""
    Historical baseline trend analysis. This model filters out seasonal noise to trace underlying population activity.
    """)

    if df_forecast is not None:
        st.markdown("#### 📈 Observed National Usage vs ARIMA Fitted Trend")
        df_forecast["month_str"] = df_forecast["month"].dt.strftime("%Y-%b")
        
        fig_forecast = px.line(
            df_forecast,
            x="month_str",
            y=["total_usage", "usage_trend_fitted"],
            markers=True,
            labels={"value": "Authentication Counts", "month_str": "Month", "variable": "Data Type"},
            color_discrete_map={"total_usage": "#2563EB", "usage_trend_fitted": "#EC4899"},
            template="plotly_white"
        )
        
        # Make the fitted line dashed for visual distinction
        fig_forecast.data[1].line.dash = "dash"
        fig_forecast.data[0].name = "Observed Usage"
        fig_forecast.data[1].name = "ARIMA-Fitted Trend"
        
        fig_forecast = apply_premium_layout(fig_forecast, "ARIMA In-Sample Historical Trend Modeling (National)")
        fig_forecast.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        st.markdown("""
        #### 🔍 Model Diagnostics & Context:
        * **What is ARIMA?** The *AutoRegressive Integrated Moving Average* model analyzes historical timeseries patterns to estimate baseline trends.
        * **Fitted Trend (Pink)**: Represents the smooth baseline usage. Discrepancies between Observed (Blue) and Fitted (Pink) indicate brief seasonal spikes or administrative pauses.
        * **Stability Note**: The model is trained purely on 2025 records to prevent long-term speculative forecasts while confirming stable in-sample fitting.
        """)
    else:
        st.info("No forecasting trend data found. Please run `analysis/forecasting.py` to generate the ARIMA outputs.")
