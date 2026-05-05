import os
import requests
from dash import Dash, html, dcc, callback, Output, Input, State

# Bulletproof initialization
app = Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Simple, high-contrast layout
app.layout = html.Div([
    html.H1("System Status: Online"),
    
    dcc.Store(id="store-chat", data=""),

    html.Div(id="output-conversation", style={
        "height": "400px", 
        "overflowY": "scroll", 
        "border": "2px solid black",
        "padding": "10px",
        "margin-bottom": "10px",
        "backgroundColor": "white"
    }),

    dcc.Input(id="input-text", type="text", placeholder="Type here...", style={"width": "80%"}),
    html.Button("Submit", id="input-submit", n_clicks=0)
], style={"padding": "50px"})

@callback(
    Output("output-conversation", "children"),
    Output("store-chat", "data"),
    Output("input-text", "value"),
    Input("input-submit", "n_clicks"),
    State("input-text", "value"),
    State("store-chat", "data"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_text, chat_history):
    if not user_text:
        return chat_history, chat_history, ""
    
    try:
        # In client.py
        response = requests.post("http://127.0.0.1:8000/api/chat", json={"question": user_text})
        data = response.json()
        print(f"Full Server Response: {data}") # Debug line
        bot_reply = data.get("response", "No response key found")
    except Exception as e:
        bot_reply = f"System Error: {e}"

    new_history = f"{chat_history}\nUser: {user_text}\nBot: {bot_reply}\n"
    return new_history, new_history, ""

if __name__ == "__main__":
    # Force IPv4 and disable the reloader which can cause M1 hangs
    app.run(host="127.0.0.1", port=8050, debug=False, dev_tools_ui=False)