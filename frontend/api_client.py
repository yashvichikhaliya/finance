import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 20

def request(method, path, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token: headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.request(method, f"{API_URL}{path}", headers=headers, timeout=TIMEOUT, **kwargs)
    except requests.RequestException as exc:
        return None, f"API connection failed: {exc}"
    if r.status_code == 204: return {}, None
    try: data = r.json()
    except ValueError: data = r.text
    if r.ok: return data, None
    if isinstance(data, dict): return None, data.get("detail", str(data))
    return None, str(data)

def login(email, password):
    return request("POST", "/auth/login", data={"username": email, "password": password})
def register(name, email, password):
    return request("POST", "/auth/register", json={"name": name, "email": email, "password": password})
def get_me(token): return request("GET", "/auth/me", token=token)
def dashboard(token): return request("GET", "/dashboard/summary", token=token)
def transactions(token, **params): return request("GET", "/transactions", token=token, params=params)
def create_transaction(token, payload): return request("POST", "/transactions", token=token, json=payload)
def update_transaction(token, tid, payload): return request("PUT", f"/transactions/{tid}", token=token, json=payload)
def delete_transaction(token, tid): return request("DELETE", f"/transactions/{tid}", token=token)
def budgets(token): return request("GET", "/budgets", token=token)
def create_budget(token, payload): return request("POST", "/budgets", token=token, json=payload)
def update_budget(token, bid, payload): return request("PUT", f"/budgets/{bid}", token=token, json=payload)
def delete_budget(token, bid): return request("DELETE", f"/budgets/{bid}", token=token)
