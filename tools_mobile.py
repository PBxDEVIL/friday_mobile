import requests
import os
import openai
import json
import datetime
from memory_mobile import add_error

available_functions = {}

def tool(name):
    def decorator(func):
        available_functions[name] = func
        return func
    return decorator

@tool("web_search")
def web_search(query):
    key = os.getenv("SERPAPI_KEY")
    if not key:
        return "Search API key missing."
    resp = requests.get("https://serpapi.com/search", params={"q": query, "api_key": key})
    results = resp.json().get("organic_results", [])
    snippets = [f"{r['title']}: {r['snippet']}" for r in results[:5]]
    return "\n".join(snippets) if snippets else "No results."

@tool("execute_python")
def execute_python(code):
    # Highly restricted sandbox: run only safe code in a separate thread with timeout
    import sys
    from io import StringIO
    import threading
    output = ""
    def target():
        nonlocal output
        try:
            sys.stdout = StringIO()
            exec(code, {"__builtins__": {"print": print, "len": len, "range": range, "int": int, "float": float, "str": str, "list": list, "dict": dict, "abs": abs, "sum": sum, "min": min, "max": max}})
            output = sys.stdout.getvalue()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = sys.__stdout__
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout=5)
    if thread.is_alive():
        return "Timeout."
    return output[:1000]

@tool("send_email")
def send_email(to, subject, body):
    import smtplib
    from email.mime.text import MIMEText
    user = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(user, password)
            server.send_message(msg)
        return f"Email sent to {to}."
    except Exception as e:
        add_error(f"send_email to {to}", str(e))
        return f"Email failed: {e}"

@tool("stock_price")
def stock_price(ticker):
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if not data.empty:
            price = data['Close'].iloc[-1]
            return f"{ticker} current price: ${price:.2f}"
        return "Ticker not found."
    except Exception as e:
        return f"Error: {e}"

# Additional tools as needed
