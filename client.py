import os
import requests
from dash import Dash, html, dcc, callback, Output, Input, State

def create_dash_app():
    app = Dash(__name__, requests_pathname_prefix="/dash/")

    # Read API_URL from environment (Render)
    API_URL = os.getenv("API_URL", "")

    app.layout = html.Div(children=[

        # Chat window
        html.Div(
            id="output-conversation",
            style={
                "width": "90%",
                "height": "70vh",
                "margin": "auto",
                "whiteSpace": "pre-wrap",
                "overflowY": "scroll",
                "border": "1px solid #444",
                "padding": "10px",
                "backgroundColor": "#f9f9f9"
            }
        ),

        # Input area
        html.Div(children=[
            dcc.Textarea(
                id="input-text",
                placeholder="Type here...",
                style={"width": "100%", "height": "100px"}
            ),

            html.Button(
                "Submit",
                id="input-submit",
                style={"width": "90%", "margin": "10px auto", "display": "block"}
            ),

            dcc.Store(id="store-chat", data="")
        ])
    ])

    @callback(
        Output("output-conversation", "children"),
        Output("store-chat", "data"),
        Input("input-submit", "n_clicks"),
        State("input-text", "value"),
        State("store-chat", "data"),
        prevent_initial_call=True
    )
    def update_chat(n_clicks, user_text, chat_history):
        if not user_text:
            return chat_history, chat_history

        try:
            # Always use a full URL for requests (never a relative path)
            if API_URL:
                # Render deployment
                url = f"{API_URL}/api/chat"
            else:
                # Local development
                url = "http://127.0.0.1:8000/api/chat"

            response = requests.post(url, json={"question": user_text})
            bot_reply = response.json().get("response", "[No response]")

        except Exception as e:
            bot_reply = f"Error contacting server: {e}"

        new_history = f"{chat_history}\nUser: {user_text}\nBot: {bot_reply}\n"
        return new_history, new_history

    return app
