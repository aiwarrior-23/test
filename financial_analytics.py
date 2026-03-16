"""
Financial Analytics Tool
Reads transaction data from Example1.csv, separates income and expenses,
calculates totals, and generates a spending breakdown with visualizations.
"""

import csv
import os

import matplotlib.pyplot as plt


def read_transactions(filepath):
    """Read transactions from CSV file and return a list of dictionaries."""
    transactions = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            # Each row is a single quoted string like: "date,category,amount"
            # The csv reader may parse it as one field or multiple
            if len(row) == 1:
                parts = row[0].split(",")
            else:
                parts = row

            if len(parts) != 3:
                continue

            date_str, category, amount_str = [p.strip() for p in parts]

            # Skip header row
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


def generate_bar_chart(breakdown, output_path="expenses_by_category.png"):
    """Generate a bar chart showing expenses by category."""
    categories = list(breakdown.keys())
    amounts = list(breakdown.values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, amounts, color=["#e74c3c", "#3498db", "#2ecc71", "#f39c12"])
    plt.title("Expenses by Category", fontsize=16, fontweight="bold")
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Amount ($)", fontsize=12)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Add value labels on bars
    for bar, amount in zip(bars, amounts):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5,
            f"${amount:,.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"\nBar chart saved to: {output_path}")


def print_financial_summary(income_list, expenses_list, total_income, total_expenses, net_savings, breakdown):
    """Print a formatted financial summary report."""
    print("=" * 55)
    print("         FINANCIAL SUMMARY REPORT")
    print("=" * 55)

    print("\n--- Income Transactions ---")
    for t in income_list:
        print(f"  {t['date']}  {t['category']:<15} ${t['amount']:>10,.2f}")

    print("\n--- Expense Transactions ---")
    for t in expenses_list:
        print(f"  {t['date']}  {t['category']:<15} ${t['amount']:>10,.2f}")

    print("\n" + "-" * 55)
    print(f"  Total Income:       ${total_income:>10,.2f}")
    print(f"  Total Expenses:     ${total_expenses:>10,.2f}")
    print(f"  Net Savings:        ${net_savings:>10,.2f}")
    print("-" * 55)

    print("\n--- Spending Breakdown by Category ---")
    for category, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        pct = (amount / abs(total_expenses)) * 100
        print(f"  {category:<15} ${amount:>10,.2f}  ({pct:5.1f}%)")

    print("\n" + "=" * 55)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "Example1.csv")

    # 1. Read transactions
    transactions = read_transactions(csv_path)
    print(f"Loaded {len(transactions)} transactions from Example1.csv\n")

    # 2. Separate income and expenses
    income_list, expenses_list = separate_income_expenses(transactions)

    # 3. Calculate total income
    total_income = calculate_total(income_list)

    # 4. Calculate total expenses
    total_expenses = calculate_total(expenses_list)

    # 5. Calculate net savings
    net_savings = total_income + total_expenses  # expenses are negative

    # 6. Create spending breakdown by category
    breakdown = spending_breakdown(expenses_list)

    # 7. Generate bar chart
    chart_path = os.path.join(script_dir, "expenses_by_category.png")
    generate_bar_chart(breakdown, output_path=chart_path)

    # 8. Print financial summary report
    print_financial_summary(
        income_list, expenses_list, total_income, total_expenses, net_savings, breakdown
    )


if __name__ == "__main__":
    main()
