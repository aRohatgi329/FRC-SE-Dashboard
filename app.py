import pandas as pd
import streamlit as st

st.set_page_config(page_title="FRC SE Dashboard", layout="wide", page_icon="🤖")

RTM_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=828480827&single=true&output=csv"
MOPS_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=1329821145&single=true&output=csv"
TRADE_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSQgaMOpy2wqYeqs6X2O4cdYbvlp6uriUkjyIsOrF90ZAP3qXyA-Aq8_PQIPpkRt2MdQ6jyuz_p4Hvp/pub?gid=1956824063&single=true&output=csv"

FOOTER = "Data updates every 60 seconds from Google Sheets"


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
    styled = df.style.map(style_rtm_status, subset=["Status"])
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
    styled = df.drop(columns=["Pass Direction"], errors="ignore").style.map(style_mops_status, subset=["Status"])
    st.dataframe(styled, use_container_width=True)
    st.caption(FOOTER)


def render_trade_studies(df):
    st.info("Scores are 1–5: 1 = poor, 5 = excellent. Higher weighted score = preferred option.")
    for decision, group in df.groupby("Decision"):
        st.subheader(decision)
        pivot = group.pivot_table(
            index="Option", columns="Criterion", values="Weighted Score", aggfunc="sum"
        )
        pivot["Total Weighted Score"] = pivot.sum(axis=1)
        winner = pivot["Total Weighted Score"].idxmax()

        def bold_winner(row):
            return ["font-weight: bold"] * len(row) if row.name == winner else [""] * len(row)

        styled = pivot.style.apply(bold_winner, axis=1)
        st.dataframe(styled, use_container_width=True)
        st.success("✅ Winning option: " + str(winner))

    st.caption(FOOTER)


def main():
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2ECC71;
    }
    h3 {
        border-left: 4px solid #2ECC71;
        padding-left: 10px;
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

    tab_rtm, tab_mops, tab_trade = st.tabs(["RTM", "MOPs", "Trade Studies"])

    with tab_rtm:
        render_rtm(rtm_df)

    with tab_mops:
        render_mops(mops_df)

    with tab_trade:
        render_trade_studies(trade_df)


if __name__ == "__main__":
    main()
