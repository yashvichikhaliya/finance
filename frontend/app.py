import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import api_client as api

st.set_page_config(page_title="FinanceFlow", page_icon="💸", layout="wide")

# ---------- Simple UI theme ----------
st.markdown("""
<style>
.block-container {padding-top:1.5rem;max-width:1200px}
[data-testid='stMetric'] {background:#111827;padding:16px;border-radius:14px;border:1px solid #263244}
</style>
""", unsafe_allow_html=True)

if "token" not in st.session_state: st.session_state.token = None
if "user_name" not in st.session_state: st.session_state.user_name = ""


def login_screen():
    st.title("💸 FinanceFlow")
    st.caption("Your personal income and expense dashboard")
    mode = st.radio("Account", ["Login", "Register"], horizontal=True)
    with st.form("auth_form"):
        name = st.text_input("Full name") if mode == "Register" else None
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button(mode, use_container_width=True)
    if submit:
        if mode == "Register":
            data, err = api.register(name or "", email, password)
            if err: st.error(str(err))
            else: st.success("Account registered! Now log in.")
        else:
            data, err = api.login(email, password)
            if err: st.error(str(err))
            else:
                st.session_state.token = data["access_token"]
                st.session_state.user_name = data.get("name", "User")
                st.rerun()


def dashboard_page():
    st.title("Overview")
    data, err = api.dashboard(st.session_state.token)
    if err: st.error(err); return
    income = data.get("income", 0); expense = data.get("expense", 0); net = data.get("net", 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("Income this month", f"₹{income:,.2f}")
    c2.metric("Expenses this month", f"₹{expense:,.2f}")
    c3.metric("Net this month", f"₹{net:,.2f}")
    st.subheader("Expense breakdown")
    cats = data.get("category_spending", {})
    if cats:
        df = pd.DataFrame([{"Category": k, "Amount": v} for k, v in cats.items()])
        st.plotly_chart(px.pie(df, names="Category", values="Amount", hole=.5), use_container_width=True)
    else: st.info("No expenses recorded for this month yet.")
    st.subheader("Recent transactions")
    recent = data.get("recent_transactions", [])
    if recent: st.dataframe(pd.DataFrame(recent), use_container_width=True, hide_index=True)
    else: st.caption("No transactions yet.")


def transaction_page():
    st.title("Transactions")
    tab_add, tab_view = st.tabs(["➕ Add transaction", "📋 View & manage"])
    with tab_add:
        with st.form("add_tx"):
            ttype = st.selectbox("Type", ["expense", "income"])
            title = st.text_input("Description", placeholder="e.g. Groceries or Monthly salary")
            amount = st.number_input("Amount (₹)", min_value=0.01, step=100.0)
            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Salary", "Freelance", "Entertainment", "Other"])
            txdate = st.date_input("Date", value=date.today())
            note = st.text_area("Note (optional)")
            submitted = st.form_submit_button("Save transaction", use_container_width=True)
        if submitted:
            payload = {"title": title, "amount": amount, "type": ttype, "category": category, "note": note, "date": txdate.isoformat()}
            data, err = api.create_transaction(st.session_state.token, payload)
            if err: st.error(err)
            else: st.success("Transaction saved!"); st.rerun()
    with tab_view:
        rows, err = api.transactions(st.session_state.token)
        if err: st.error(err)
        elif rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
            ids = [r["id"] for r in rows]
            selected = st.selectbox("Select transaction ID to delete", ids)
            if st.button("Delete selected transaction", type="secondary"):
                _, err = api.delete_transaction(st.session_state.token, selected)
                if err: st.error(err)
                else: st.success("Deleted"); st.rerun()
        else: st.info("No transactions yet.")


def budget_page():
    st.title("Budgets")
    with st.form("budget_form"):
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"])
        limit = st.number_input("Monthly limit (₹)", min_value=1.0, step=500.0)
        today = date.today()
        month = st.selectbox("Month", list(range(1,13)), index=today.month-1)
        year = st.number_input("Year", min_value=2000, max_value=2100, value=today.year)
        save = st.form_submit_button("Create budget")
    if save:
        payload = {"category": category, "monthly_limit": limit, "month": month, "year": int(year)}
        data, err = api.create_budget(st.session_state.token, payload)
        if err: st.error(err)
        else: st.success("Budget created"); st.rerun()
    rows, err = api.budgets(st.session_state.token)
    if err: st.error(err)
    elif rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        bid = st.selectbox("Budget to remove", [r["id"] for r in rows], key="delete_budget_id")
        if st.button("Delete budget"):
            _, err = api.delete_budget(st.session_state.token, bid)
            if err: st.error(err)
            else: st.success("Budget deleted"); st.rerun()
    else: st.info("No budgets created yet.")


def analytics_page():
    st.title("Analytics")
    rows, err = api.transactions(st.session_state.token)
    if err: st.error(err); return
    if not rows: st.info("Add transactions to see your analytics."); return
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    expenses = df[df["type"] == "expense"]
    income = df[df["type"] == "income"]
    if not expenses.empty:
        st.subheader("Expenses by category")
        chart = expenses.groupby("category", as_index=False)["amount"].sum()
        st.plotly_chart(px.bar(chart, x="category", y="amount", title="Expense totals by category"), use_container_width=True)
        st.subheader("Expense history")
        daily = expenses.groupby("date", as_index=False)["amount"].sum()
        st.plotly_chart(px.line(daily, x="date", y="amount", markers=True), use_container_width=True)
    st.write(f"Total income: ₹{income.amount.sum() if not income.empty else 0:,.2f}")
    st.write(f"Total expenses: ₹{expenses.amount.sum() if not expenses.empty else 0:,.2f}")


if not st.session_state.token:
    login_screen()
else:
    with st.sidebar:
        st.title("💸 FinanceFlow")
        st.write(f"Hello, {st.session_state.user_name}")
        page = st.radio("Navigation", ["Overview", "Transactions", "Budgets", "Analytics"])
        if st.button("Log out"):
            st.session_state.token = None; st.session_state.user_name = ""; st.rerun()
    if page == "Overview": dashboard_page()
    elif page == "Transactions": transaction_page()
    elif page == "Budgets": budget_page()
    elif page == "Analytics": analytics_page()
