# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A Streamlit dashboard for FRC (FIRST Robotics Competition) Systems Engineering, currently displaying a Requirements Traceability Matrix (RTM) pulled live from Google Sheets.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

The entire application lives in `app.py`. Data flows in one direction:

1. `load_rtm_data()` fetches a Google Sheet as a CSV export (cached for 60 seconds via `@st.cache_data`)
2. `main()` renders the Streamlit UI using that data

The Google Sheet URL is hardcoded in `load_rtm_data()`. The sheet ID and `gid` (tab ID) are the two parameters to change when pointing at a different sheet or tab.

`.streamlit/` is gitignored — any Streamlit config (theme, server settings) goes there locally but is not committed.
