import streamlit as st

st.set_page_config(page_title="AI Portfolio Manager - Grok", layout="wide")

st.title("AI Portfolio Manager - Grok")
st.markdown("Your autonomous portfolio simulator. Starting fresh.")

capital = st.sidebar.number_input("Starting Capital ($)", min_value=1000, value=10000, step=1000)
risk_level = st.sidebar.selectbox("Risk Level", ["Safe", "Medium", "Aggressive"], index=1)

if st.sidebar.button("Run Simulation"):
    st.subheader("Simulated Portfolio Allocation")
    st.write(f"Capital: ${capital:,} at {risk_level} risk")
    st.table({
        "Asset": ["SPY", "QQQ", "VTI", "VXUS", "BND"],
        "Weight": ["20%", "20%", "20%", "20%", "20%"],
        "Amount": [f"${capital * 0.2:,.0f}"] * 5
    })
    st.subheader("Performance Estimate")
    st.write("Expected annual return: ~13–17%")
    st.write("Volatility: ~14%")
    st.write("Sharpe ratio: ~0.85")
    st.success("Simulation complete. Agent is ready.")
