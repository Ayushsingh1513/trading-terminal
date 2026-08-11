# 1. Load the old results (performance_history.json) with safe padding
        history_df = pd.DataFrame()
        if os.path.exists("performance_history.json"):
            try:
                with open("performance_history.json", "r") as f:
                    data = json.load(f)
                    
                if data:
                    if isinstance(data, dict):
                        # Fix for "All arrays must be of the same length"
                        try:
                            history_df = pd.DataFrame(data)
                        except ValueError:
                            # Find the longest column and pad shorter columns with blanks (None)
                            max_len = max([len(v) for v in data.values() if isinstance(v, list)], default=0)
                            padded_data = {
                                k: (v + [None] * (max_len - len(v)) if isinstance(v, list) else [v] * max_len)
                                for k, v in data.items()
                            }
                            history_df = pd.DataFrame(padded_data)
                    elif isinstance(data, list):
                        # If data is a standard list of rows
                        history_df = pd.DataFrame(data)
            except Exception as e:
                st.error(f"Error loading history: {e}")