<!-- USE HTML LINK TAGS INSTEAD OF @IMPORT FOR STREAMLIT -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
    /* Force typography overrides across the entire app */
    * {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Target all our specific data/number elements with the mono font */
    .mono, .pick-stock, .pick-buy-badge, .pick-cell-val, .pick-cell-lbl, .sec-hdr-text, 
    .ticker-label, .ticker-val, .mood-value, .pick-rr, .pick-meta span, .sq-title, .sq-chip {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* ... (keep the rest of your background colors and card CSS the same below this) ... */
