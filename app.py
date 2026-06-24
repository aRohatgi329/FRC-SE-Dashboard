import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="FRC SE Dashboard", layout="wide", page_icon="🔥")

RTM_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=828480827&single=true&output=csv"
MOPS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=1329821145&single=true&output=csv"
TRADE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=1956824063&single=true&output=csv"
TIMELINE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=1473212198&single=true&output=csv"

FOOTER = "Data updates every 60 seconds from Google Sheets"

HEADER_STYLE = [
    {"selector": "th", "props": [
        ("background-color", "#f0f0f0"),
        ("color", "black"),
        ("font-weight", "bold"),
    ]},
    {"selector": "th.row_heading", "props": [
        ("color", "black"),
        ("font-weight", "normal"),
    ]},
]

PHASE_ORDER = ["Design", "Build", "Test"]
SUBSYSTEM_PALETTE = [
    "#5B8DB8", "#5BBF8A", "#E0A458", "#9B7FBF",
    "#D98CA1", "#5FB0C9", "#C97F7F", "#86B85B",
]


def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r}, {g}, {b}, {alpha})"


@st.cache_data(ttl=60)
def load_rtm():
    try:
        df = pd.read_csv(RTM_URL)
        df["Status"] = df["Status"].fillna("Unverified")
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()


@st.cache_data(ttl=60)
def load_mops():
    try:
        df = pd.read_csv(MOPS_URL)
        df["Status"] = df["Status"].fillna("Unverified")
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()


@st.cache_data(ttl=60)
def load_trade_study():
    try:
        return pd.read_csv(TRADE_URL)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
        return pd.DataFrame()


@st.cache_data(ttl=60)
def load_timeline():
    try:
        return pd.read_csv(TIMELINE_URL)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()
        return pd.DataFrame()


def style_rtm_status(val):
    colors = {"Verified": "background-color: #d4edda", "Failed": "background-color: #f8d7da"}
    return colors.get(val, "background-color: #fff3cd")


def style_mops_status(val):
    colors = {"Pass": "background-color: #d4edda", "Fail": "background-color: #f8d7da", "At Risk": "background-color: #fff3cd; color: #856404"}
    return colors.get(val, "background-color: #fff3cd")


def render_rtm(df):
    total = len(df)
    verified = int((df["Status"] == "Verified").sum())
    failed = int((df["Status"] == "Failed").sum())

    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    c1.metric("Total Requirements", total)
    c2.metric("Verified", verified)
    c3.metric("Failed", failed)

    df = df.copy()
    df.index = range(1, len(df) + 1)
    styled = (
        df.style
        .map(style_rtm_status, subset=["Status"])
        .set_table_styles(HEADER_STYLE)
    )
    st.dataframe(styled, use_container_width=True)
    st.caption(FOOTER)


def render_mops(df):
    total = len(df)
    passing = int((df["Status"] == "Pass").sum())
    failing = int((df["Status"] == "Fail").sum())

    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
    c1.metric("Total Metrics", total)
    c2.metric("Pass", passing)
    c3.metric("Fail", failing)

    df = df.copy()
    df.index = range(1, len(df) + 1)
    df["Target"] = df["Target"].apply(lambda x: f"{x:g}").astype(str) + " " + df["Unit"].fillna("").astype(str)
    df["Actual"] = df["Actual"].apply(lambda x: f"{x:g}").astype(str) + " " + df["Unit"].fillna("").astype(str)
    df["Target"] = df["Target"].str.strip()
    df["Actual"] = df["Actual"].str.strip()
    styled = (
        df.drop(columns=["Pass Direction", "Unit"], errors="ignore")
        .style
        .map(style_mops_status, subset=["Status"])
        .set_table_styles(HEADER_STYLE)
    )
    st.dataframe(styled, use_container_width=True)
    st.caption(FOOTER)


def render_trade_studies(df):
    st.info("Scores are 1–5: 1 = Poor, 5 = Excellent. Higher weighted score = preferred option.")
    for decision, group in df.groupby("Decision"):
        st.subheader(decision)
        pivot = group.pivot_table(
            index="Option", columns="Criterion", values="Weighted Score", aggfunc="first"
        )
        pivot["Total Weighted Score"] = pivot.sum(axis=1)
        winner = pivot["Total Weighted Score"].idxmax()

        def highlight_pivot(df):
            styles = pd.DataFrame("", index=df.index, columns=df.columns)
            for col in df.columns:
                if col == "Total Weighted Score":
                    max_val = df[col].max()
                    min_val = df[col].min()
                    for idx in df.index:
                        if df.loc[idx, col] == max_val:
                            styles.loc[idx, col] = "background-color: #d4edda; font-weight: bold"
                        elif df.loc[idx, col] == min_val:
                            styles.loc[idx, col] = "background-color: #f8d7da"
                else:
                    max_val = df[col].max()
                    for idx in df.index:
                        if df.loc[idx, col] == max_val:
                            styles.loc[idx, col] = "font-weight: bold"
            return styles

        styled = (
            pivot.style
            .apply(highlight_pivot, axis=None)
            .format(lambda x: f"{x:g}" if isinstance(x, float) else x)
            .set_table_styles(HEADER_STYLE)
        )
        st.dataframe(styled, use_container_width=True)
        st.success("✅ Winning option: " + str(winner))

    st.caption(FOOTER)


def build_timeline_fig(df):
    base_date = datetime.date(2026, 1, 10)
    df = df.copy()
    df = df.dropna(subset=["Start Week", "End Week"])
    df["Start Week"] = df["Start Week"].astype(int)
    df["End Week"] = df["End Week"].astype(int)
    df["Start Date"] = df["Start Week"].apply(lambda w: base_date + datetime.timedelta(weeks=w - 1))
    df["End Date"] = df["End Week"].apply(lambda w: base_date + datetime.timedelta(weeks=w))
    subsystem_order = list(dict.fromkeys(df["Subsystem"]))
    phase_rank = {p: i for i, p in enumerate(PHASE_ORDER)}
    df["_sub"] = df["Subsystem"].map({s: i for i, s in enumerate(subsystem_order)})
    df["_phase"] = df["Phase"].map(phase_rank).fillna(len(PHASE_ORDER))
    df = df.sort_values(["_sub", "_phase"]).reset_index(drop=True)
    df["Row"] = df["Subsystem"] + " — " + df["Phase"]
    color_map = {s: SUBSYSTEM_PALETTE[i % len(SUBSYSTEM_PALETTE)] for i, s in enumerate(subsystem_order)}
    display_order = df["Row"].tolist()
    fig = px.timeline(
        df,
        x_start="Start Date",
        x_end="End Date",
        y="Row",
        color="Subsystem",
        color_discrete_map=color_map,
        category_orders={"Subsystem": subsystem_order},
        custom_data=["Subsystem", "Phase", "Critical Path", "Start Week", "End Week"],
    )
    crit = df.set_index("Row")["Critical Path"].to_dict()
    for tr in fig.data:
        tr.marker.line.width = [3 if crit.get(r) == "Yes" else 0 for r in tr.y]
        tr.marker.line.color = "#C0392B"
    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]} — %{customdata[1]}</b><br>"
            "Week %{customdata[3]} to %{customdata[4]}<br>"
            "Critical Path: %{customdata[2]}<extra></extra>"
        ),
    )
    shapes, annotations = [], []
    idx = 0
    for s in subsystem_order:
        n = int((df["Subsystem"] == s).sum())
        start, end = idx, idx + n - 1
        center = (start + end) / 2
        shapes.append(dict(
            type="rect", xref="paper", x0=0, x1=1,
            yref="y", y0=start - 0.5, y1=end + 0.5,
            fillcolor=_rgba(color_map[s], 0.10), line_width=0, layer="below",
        ))
        if end + 1 < len(display_order):
            shapes.append(dict(
                type="line", xref="paper", x0=0, x1=1,
                yref="y", y0=end + 0.5, y1=end + 0.5,
                line=dict(color="rgba(0,0,0,0.12)", width=1),
            ))
        annotations.append(dict(
            xref="paper", x=-0.10, yref="y", y=center,
            text=f"<b>{s}</b>", showarrow=False,
            font=dict(size=13, color=color_map[s]),
            xanchor="right", yanchor="middle",
        ))
        idx += n
    fig.update_yaxes(
        categoryorder="array", categoryarray=display_order, autorange="reversed",
        tickmode="array", tickvals=display_order,
        ticktext=[r.split(" — ")[1] for r in display_order],
        title="",
    )
    fig.update_xaxes(
        title="Build Week",
        tickvals=[base_date + datetime.timedelta(weeks=i) for i in range(6)],
        ticktext=[f"Week {i + 1}" for i in range(6)],
        range=[base_date - datetime.timedelta(days=1), base_date + datetime.timedelta(weeks=6, days=1)],
        showgrid=True, gridcolor="rgba(0,0,0,0.08)",
    )
    fig.update_layout(
        title="Build Season Timeline (6 Weeks)",
        shapes=shapes, annotations=annotations,
        showlegend=False, bargap=0.35,
        margin=dict(l=200, r=20, t=60, b=40),
        height=max(420, 42 * len(display_order) + 120),
    )
    return fig


def render_timeline(df):
    total_subsystems = df["Subsystem"].nunique()
    critical_count = df[df["Critical Path"] == "Yes"]["Subsystem"].nunique()
    c1, c2, _ = st.columns([1, 1, 4])
    c1.metric("Total Subsystems", total_subsystems)
    c2.metric("Critical Path Subsystems", critical_count)
    fig = build_timeline_fig(df)
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "Each subsystem is a tier, with its Design → Build → Test phases grouped together. "
        "Bars outlined in red are on the critical path — delays there push out the overall build-season end date."
    )
    st.caption(FOOTER)


def main():
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2ECC71;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.05rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("TORCH 5804 | FRC Systems Engineering Dashboard")
    st.markdown('<p style="color: gray; margin-top: -12px;">ISO 15288 Systems Engineering | 2025-26 Season</p>', unsafe_allow_html=True)
    st.divider()

    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    rtm_df = load_rtm()
    mops_df = load_mops()
    trade_df = load_trade_study()

    tab_rtm, tab_mops, tab_trade, tab_timeline = st.tabs(["RTM", "MOPs", "Trade Studies", "Build Timeline"])

    with tab_rtm:
        render_rtm(rtm_df)

    with tab_mops:
        render_mops(mops_df)

    with tab_trade:
        render_trade_studies(trade_df)

    with tab_timeline:
        timeline_df = load_timeline()
        render_timeline(timeline_df)


if __name__ == "__main__":
    main()
