import json
import os
from datetime import datetime

# (Assuming you already have your send_telegram_alert function and tokens at the top)

def track_performance_and_alert(current_scanner_df):
    history_file = "performance_history.json"
    
    # Load existing history or create a new one
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
    else:
        history = {"closed_trades": [], "active_trades": []}

    updated_active = []
    
    # 1. Check Active Trades against Today's Prices
    for trade in history.get("active_trades", []):
        stock_data = current_scanner_df[current_scanner_df['Stock'] == trade['Stock']]
        
        if not stock_data.empty:
            current_price = stock_data.iloc[0]['Price']
            
            # 🎯 Target 1 Hit
            if current_price >= trade['Target1']:
                trade['Status'] = 'WIN'
                trade['Exit_Price'] = current_price
                history['closed_trades'].append(trade)
                
                # Fire alert through your existing bot
                msg = f"🎯 *TARGET HIT!*\n\n📈 *{trade['Stock']}* blasted past Target 1!\n💰 *Entry:* ₹{trade['Entry']} ➔ *Current:* ₹{current_price}\n🔥 *Result:* WIN"
                send_telegram_alert(msg)
                
            # 🛑 Stop Loss Hit
            elif current_price <= trade['SL']:
                trade['Status'] = 'LOSS'
                trade['Exit_Price'] = current_price
                history['closed_trades'].append(trade)
                
                # Fire SL alert
                msg = f"🛑 *STOP LOSS HIT*\n\n📉 *{trade['Stock']}* hit SL level.\n💰 *Entry:* ₹{trade['Entry']} ➔ *Exit:* ₹{current_price}\n🛡️ *Result:* Capital Protected."
                send_telegram_alert(msg)
                
            else:
                updated_active.append(trade) # Still active
        else:
            updated_active.append(trade)

    history['active_trades'] = updated_active

    # 2. Log Today's New STRONG BUYs into Active Trades
    new_buys = current_scanner_df[current_scanner_df['Signal'] == 'BUY'].to_dict('records')
    for buy in new_buys:
        # Only add if it's not already active
        if not any(t['Stock'] == buy['Stock'] for t in history['active_trades']):
            history['active_trades'].append({
                "Stock": buy["Stock"],
                "Entry": buy["Entry"],
                "Target1": buy["Target1"],
                "SL": buy["SL"],
                "Date": datetime.now().strftime("%Y-%m-%d")
            })

    # Save the updated ledger
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)
