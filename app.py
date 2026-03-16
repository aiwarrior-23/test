"""
Financial Analytics - Streamlit Web App
A simple web app that reads transaction data, separates income and expenses,
calculates totals, and displays interactive charts and a financial summary.
"""

import csv
import io
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def read_transactions_from_text(text):
    """Read transactions from CSV text and return a list of dictionaries."""
    transactions = []
    reader = csv.reader(io.StringIO(text))
    for row in reader:
        if len(row) == 1:
            parts = row[0].split(",")
        else:
            parts = row

        if len(parts) != 3:
            continue

        date_str, category, amount_str = [p.strip() for p in parts]

        if date_str == "date":
            continue

        try:
            amount = float(amount_str)
        except ValueError:
            continue

        transactions.append({
            "date": date_str,
            "category": category,
            "amount": amount,
        })

    return transactions


def separate_income_expenses(transactions):
    """Separate transactions into income (positive) and expenses (negative)."""
    income = [t for t in transactions if t["amount"] > 0]
    expenses = [t for t in transactions if t["amount"] < 0]
    return income, expenses


def calculate_total(transactions):
    """Calculate the total amount from a list of transactions."""
    return sum(t["amount"] for t in transactions)


def spending_breakdown(expenses):
    """Create a spending breakdown by category (returns positive values)."""
    breakdown = {}
    for t in expenses:
        category = t["category"]
        breakdown[category] = breakdown.get(category, 0) + abs(t["amount"])
    return breakdown


def create_bar_chart(breakdown):
    """Create a bar chart figure showing expenses by category."""
    categories = list(breakdown.keys())
    amounts = list(breakdown.values())

    fig, ax = plt.subplots(figsize=(10, 5))
    color_cycle = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12"]
    colors = [color_cycle[i % len(color_cycle)] for i in range(len(categories))]
    bars = ax.bar(categories, amounts, color=colors)
    ax.set_title("Expenses by Category", fontsize=16, fontweight="bold")
    ax.set_xlabel("Category", fontsize=12)
    ax.set_ylabel("Amount ($)", fontsize=12)

    for bar, amount in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            f"${amount:,.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    fig.tight_layout()
    return fig


def create_pie_chart(breakdown):
    """Create a pie chart figure showing expense distribution."""
    categories = list(breakdown.keys())
    amounts = list(breakdown.values())
    color_cycle = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    colors = [color_cycle[i % len(color_cycle)] for i in range(len(categories))]

    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        textprops={"fontsize": 12},
    )
    for autotext in autotexts:
        autotext.set_fontweight("bold")
    ax.set_title("Expense Distribution by Category", fontsize=16, fontweight="bold")
    fig.tight_layout()
    return fig


def load_default_csv():
    """Load the bundled Example1.csv file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "Example1.csv")
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            return f.read()
    return None


def main():
    st.set_page_config(page_title="Financial Analytics", page_icon="$", layout="wide")

    st.title("Financial Analytics Dashboard")
    st.markdown("Upload a CSV or use the bundled **Example1.csv** to analyze your finances.")

    # --- Sidebar: data source ---
    st.sidebar.header("Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        csv_text = uploaded_file.getvalue().decode("utf-8-sig")
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
    else:
        csv_text = load_default_csv()
        if csv_text:
            st.sidebar.info("Using bundled Example1.csv")
        else:
            st.warning("No CSV file found. Please upload one.")
            return

    # --- Process data ---
    transactions = read_transactions_from_text(csv_text)

    if not transactions:
        st.error("No valid transactions found in the CSV file.")
        return

    income_list, expenses_list = separate_income_expenses(transactions)
    total_income = calculate_total(income_list)
    total_expenses = calculate_total(expenses_list)
    net_savings = total_income + total_expenses
    breakdown = spending_breakdown(expenses_list)

    # --- Summary metrics ---
    st.header("Financial Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${total_income:,.2f}")
    col2.metric("Total Expenses", f"${abs(total_expenses):,.2f}")
    col3.metric("Net Savings", f"${net_savings:,.2f}", delta=f"${net_savings:,.2f}")

    st.divider()

    # --- Charts ---
    st.header("Expense Analysis")

    if breakdown:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Expenses by Category")
            bar_fig = create_bar_chart(breakdown)
            st.pyplot(bar_fig)

        with chart_col2:
            st.subheader("Expense Distribution")
            pie_fig = create_pie_chart(breakdown)
            st.pyplot(pie_fig)
    else:
        st.info("No expense transactions to chart.")

    st.divider()

    # --- Spending breakdown table ---
    st.header("Spending Breakdown")
    if breakdown:
        breakdown_data = []
        for category, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
            pct = (amount / abs(total_expenses)) * 100 if total_expenses != 0 else 0
            breakdown_data.append({
                "Category": category,
                "Amount": f"${amount:,.2f}",
                "Percentage": f"{pct:.1f}%",
            })
        st.table(pd.DataFrame(breakdown_data))

    st.divider()

    # --- Transaction tables ---
    st.header("Transaction Details")

    tab1, tab2 = st.tabs(["Income", "Expenses"])

    with tab1:
        if income_list:
            income_df = pd.DataFrame(income_list)
            income_df.columns = ["Date", "Category", "Amount"]
            income_df["Amount"] = income_df["Amount"].apply(lambda x: f"${x:,.2f}")
            st.table(income_df)
        else:
            st.info("No income transactions.")

    with tab2:
        if expenses_list:
            expense_df = pd.DataFrame(expenses_list)
            expense_df.columns = ["Date", "Category", "Amount"]
            expense_df["Amount"] = expense_df["Amount"].apply(lambda x: f"${x:,.2f}")
            st.table(expense_df)
        else:
            st.info("No expense transactions.")


if __name__ == "__main__":
    main()
