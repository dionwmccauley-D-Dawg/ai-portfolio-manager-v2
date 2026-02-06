import streamlit as st

# Navigation setup (multi-page)
pages = {
    "Dashboard": st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
    "Backtest": st.Page("pages/backtest.py", title="Backtest", icon=":material/analytics:"),
    "Settings": st.Page("pages/settings.py", title="Settings", icon=":material/settings:"),
    "Agent Chat": st.Page("pages/chat.py", title="Agent Chat", icon=":material/smart_toy:"),
}

pg = st.navigation(pages, position="sidebar")
pg.run()
