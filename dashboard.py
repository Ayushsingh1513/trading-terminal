def style_sig(val):
        if val == "BUY":   return "background:rgba(0, 214, 143, 0.1);color:#00D68F;font-weight:700;"
        if val == "WATCH": return "background:rgba(255, 176, 32, 0.1);color:#FFB020;font-weight:700;"
        if val == "AVOID": return "background:rgba(255, 76, 76, 0.1);color:#FF4C4C;font-weight:700;"
        return ""
    
    st.dataframe(
        filt.style.map(style_sig, subset=["Signal"]),
        column_config={
            "Price": st.column_config.NumberColumn(format="₹%.2f"),
            "RSI": st.column_config.ProgressColumn("RSI", format="%.1f", min_value=0, max_value=100),
            "Score": st.column_config.ProgressColumn("Confluence Score", format="%f", min_value=0, max_value=100),
            "VolSurge": st.column_config.NumberColumn("Volume Surge", format="%.2fx"),
            "RS": st.column_config.NumberColumn("Relative Strength", format="%+.2f%%"),
            "52W%": st.column_config.NumberColumn("From 52W High", format="%.2f%%"),
        },
        hide_index=True, use_container_width=True, height=360
    )
