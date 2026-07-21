# ══════════════════════════════════════════════════════════════════════════════
# SEBI SHIELD & PREMIUM ANIMATIONS
# ══════════════════════════════════════════════════════════════════════════════
if "legal_accepted" not in st.session_state:
    st.session_state.legal_accepted = False

# Premium CSS Animations
st.markdown("""
<style>
/* Animated Breathing Background */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.stApp {
    background: linear-gradient(-45deg, #07091A, #0D1120, #040914, #0A0E1E) !important;
    background-size: 400% 400% !important;
    animation: gradientBG 15s ease infinite !important;
}

/* Pulsing Glow for Buy Badges */
@keyframes pulseGlow {
    0% { box-shadow: 0 0 5px rgba(0,214,143,0.1); }
    50% { box-shadow: 0 0 15px rgba(0,214,143,0.6); }
    100% { box-shadow: 0 0 5px rgba(0,214,143,0.1); }
}
.pick-buy-badge {
    animation: pulseGlow 2s infinite;
}

/* Legal Modal Styling */
.legal-modal {
    background: #0D1120; border: 1px solid #FF4C4C; border-radius: 12px;
    padding: 30px; margin: 40px auto; max-width: 600px; text-align: center;
    box-shadow: 0 10px 30px rgba(255, 76, 76, 0.15);
}
.legal-title { color: #FF4C4C; font-size: 20px; font-weight: 800; font-family: 'JetBrains Mono', monospace; margin-bottom: 15px; }
.legal-text { color: #94A3B8; font-size: 14px; line-height: 1.6; margin-bottom: 25px; text-align: left; }
</style>
""", unsafe_allow_html=True)

# The SEBI Shield Popup
if not st.session_state.legal_accepted and st.session_state.page == "terminal":
    st.markdown("""
    <div class="legal-modal">
        <div class="legal-title">⚠️ MANDATORY RISK DISCLOSURE</div>
        <div class="legal-text">
            <b>1. Not SEBI Registered:</b> The creator of Momentum Frenzy is NOT a SEBI-registered entity, financial advisor, or research analyst.<br><br>
            <b>2. Educational Use Only:</b> All data, momentum scores, and stock setups provided here are purely algorithmic and for educational/paper-trading purposes only.<br><br>
            <b>3. 100% Your Risk:</b> Trading in equities and F&O involves extreme financial risk. You alone are responsible for your capital. We hold zero liability for any financial losses incurred based on this data.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("I Understand & Agree to these Terms", type="primary", use_container_width=True):
            st.session_state.legal_accepted = True
            st.rerun()
    st.stop() # Stops the rest of the website from loading until they click agree
