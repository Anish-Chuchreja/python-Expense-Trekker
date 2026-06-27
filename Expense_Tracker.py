"""
========================================
  EXPENSE TRACKER - Python CLI App
========================================
Features:
  - Add / View / Delete expenses
  - Category-wise breakdown
  - Monthly summary
  - Budget alerts
  - Export to CSV
  - Persistent storage (JSON file)
========================================
"""

import json
import csv
import os
from datetime import datetime, date
from collections import defaultdict

# ── Storage file ──────────────────────────────────────────────────────────────
DATA_FILE = "expenses.json"

# ── Default categories ────────────────────────────────────────────────────────
CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Health & Medical",
    "Bills & Utilities",
    "Education",
    "Travel",
    "Others",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_data() -> dict:
    """Load expenses and settings from the JSON data file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"expenses": [], "budget": 0.0, "next_id": 1}


def save_data(data: dict) -> None:
    """Persist the current data to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def separator(char: str = "─", width: int = 52) -> None:
    print(char * width)


def header(title: str) -> None:
    separator("═")
    print(f"  {title}")
    separator("═")


def pause() -> None:
    input("\n  Press Enter to continue…")

# ── Core features ─────────────────────────────────────────────────────────────

def add_expense(data: dict) -> None:
    header("ADD EXPENSE")

    # Description
    description = input("  Description : ").strip()
    if not description:
        print("  ✗ Description cannot be empty.")
        pause()
        return

    # Amount
    try:
        amount = float(input("  Amount (₹)  : "))
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("  ✗ Enter a valid positive number.")
        pause()
        return

    # Category
    print("\n  Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i:2}. {cat}")
    try:
        cat_idx = int(input("\n  Choose category (number): ")) - 1
        if not (0 <= cat_idx < len(CATEGORIES)):
            raise ValueError
        category = CATEGORIES[cat_idx]
    except ValueError:
        print("  ✗ Invalid choice.")
        pause()
        return

    # Date
    date_str = input(f"  Date (YYYY-MM-DD) [today = {date.today()}]: ").strip()
    if not date_str:
        date_str = str(date.today())
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("  ✗ Invalid date format.")
            pause()
            return

    # Save
    expense = {
        "id": data["next_id"],
        "description": description,
        "amount": round(amount, 2),
        "category": category,
        "date": date_str,
    }
    data["expenses"].append(expense)
    data["next_id"] += 1
    save_data(data)

    print(f"\n  ✓ Expense #{expense['id']} added successfully!")

    # Budget alert
    if data["budget"] > 0:
        month = date_str[:7]
        monthly_total = sum(
            e["amount"] for e in data["expenses"] if e["date"].startswith(month)
        )
        if monthly_total > data["budget"]:
            print(f"\n  ⚠  BUDGET ALERT! Monthly spend ₹{monthly_total:,.2f}"
                  f" exceeds budget ₹{data['budget']:,.2f}")

    pause()


def view_expenses(data: dict) -> None:
    header("VIEW EXPENSES")

    expenses = data["expenses"]
    if not expenses:
        print("  No expenses recorded yet.")
        pause()
        return

    # Filter options
    print("  Filter by:")
    print("  1. All expenses")
    print("  2. This month")
    print("  3. By category")
    print("  4. By date range")
    choice = input("\n  Choice: ").strip()

    filtered = expenses[:]

    if choice == "2":
        month = str(date.today())[:7]
        filtered = [e for e in expenses if e["date"].startswith(month)]
    elif choice == "3":
        print("\n  Categories:")
        for i, cat in enumerate(CATEGORIES, 1):
            print(f"    {i}. {cat}")
        try:
            cat_idx = int(input("  Choose: ")) - 1
            cat = CATEGORIES[cat_idx]
            filtered = [e for e in expenses if e["category"] == cat]
        except (ValueError, IndexError):
            print("  ✗ Invalid choice.")
            pause()
            return
    elif choice == "4":
        start = input("  Start date (YYYY-MM-DD): ").strip()
        end = input("  End   date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
            filtered = [e for e in expenses if start <= e["date"] <= end]
        except ValueError:
            print("  ✗ Invalid date format.")
            pause()
            return

    if not filtered:
        print("\n  No expenses match the filter.")
        pause()
        return

    # Display table
    print()
    separator()
    print(f"  {'ID':>4}  {'Date':<12}  {'Category':<18}  {'Amount':>10}  Description")
    separator()
    for e in sorted(filtered, key=lambda x: x["date"]):
        print(f"  {e['id']:>4}  {e['date']:<12}  {e['category']:<18}  ₹{e['amount']:>9,.2f}  {e['description']}")
    separator()
    total = sum(e["amount"] for e in filtered)
    print(f"  {'TOTAL':>38}  ₹{total:>9,.2f}")
    separator()

    pause()


def delete_expense(data: dict) -> None:
    header("DELETE EXPENSE")

    if not data["expenses"]:
        print("  No expenses to delete.")
        pause()
        return

    try:
        exp_id = int(input("  Enter Expense ID to delete: "))
    except ValueError:
        print("  ✗ Invalid ID.")
        pause()
        return

    for i, e in enumerate(data["expenses"]):
        if e["id"] == exp_id:
            confirm = input(f"  Delete '{e['description']}' (₹{e['amount']:.2f})? [y/N]: ")
            if confirm.lower() == "y":
                data["expenses"].pop(i)
                save_data(data)
                print("  ✓ Expense deleted.")
            else:
                print("  Cancelled.")
            pause()
            return

    print(f"  ✗ Expense ID #{exp_id} not found.")
    pause()


def monthly_summary(data: dict) -> None:
    header("MONTHLY SUMMARY")

    expenses = data["expenses"]
    if not expenses:
        print("  No expenses recorded yet.")
        pause()
        return

    # Group by month
    by_month: dict = defaultdict(lambda: defaultdict(float))
    for e in expenses:
        month = e["date"][:7]
        by_month[month][e["category"]] += e["amount"]

    for month in sorted(by_month.keys(), reverse=True):
        cat_totals = by_month[month]
        month_total = sum(cat_totals.values())
        dt = datetime.strptime(month, "%Y-%m")
        print(f"\n  ── {dt.strftime('%B %Y')} ──────────────────────────────")
        for cat, amt in sorted(cat_totals.items(), key=lambda x: -x[1]):
            bar_len = int((amt / month_total) * 20)
            bar = "█" * bar_len
            print(f"  {cat:<20}  ₹{amt:>9,.2f}  {bar}")
        print(f"  {'TOTAL':<20}  ₹{month_total:>9,.2f}")

        if data["budget"] > 0:
            remaining = data["budget"] - month_total
            status = "✓ Under budget" if remaining >= 0 else "✗ Over budget"
            print(f"  Budget (₹{data['budget']:,.2f})   Remaining: ₹{abs(remaining):,.2f}  {status}")

    pause()


def set_budget(data: dict) -> None:
    header("SET MONTHLY BUDGET")

    print(f"  Current budget: ₹{data['budget']:,.2f}" if data["budget"] else "  No budget set.")
    try:
        budget = float(input("  Enter new monthly budget (₹): "))
        if budget < 0:
            raise ValueError
        data["budget"] = round(budget, 2)
        save_data(data)
        print(f"  ✓ Budget set to ₹{data['budget']:,.2f}")
    except ValueError:
        print("  ✗ Invalid amount.")

    pause()


def export_to_csv(data: dict) -> None:
    header("EXPORT TO CSV")

    if not data["expenses"]:
        print("  No expenses to export.")
        pause()
        return

    filename = f"expenses_{date.today()}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description"])
        writer.writeheader()
        writer.writerows(sorted(data["expenses"], key=lambda x: x["date"]))

    print(f"  ✓ Exported {len(data['expenses'])} records to '{filename}'")
    pause()


def category_summary(data: dict) -> None:
    header("CATEGORY BREAKDOWN (ALL TIME)")

    expenses = data["expenses"]
    if not expenses:
        print("  No expenses recorded yet.")
        pause()
        return

    by_cat: dict = defaultdict(float)
    for e in expenses:
        by_cat[e["category"]] += e["amount"]

    total = sum(by_cat.values())
    print(f"\n  {'Category':<22}  {'Amount':>10}  {'Share':>6}  Chart")
    separator()
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = (amt / total) * 100
        bar = "█" * int(pct / 5)
        print(f"  {cat:<22}  ₹{amt:>9,.2f}  {pct:5.1f}%  {bar}")
    separator()
    print(f"  {'TOTAL':<22}  ₹{total:>9,.2f}")

    pause()

# ── Main menu ─────────────────────────────────────────────────────────────────

def main_menu(data: dict) -> None:
    while True:
        clear_screen()
        header("💰 EXPENSE TRACKER")

        budget_line = f"₹{data['budget']:,.2f}" if data["budget"] else "Not set"
        month = str(date.today())[:7]
        month_total = sum(e["amount"] for e in data["expenses"] if e["date"].startswith(month))
        print(f"  Monthly Budget : {budget_line}")
        print(f"  Spent this month: ₹{month_total:,.2f}")
        separator()
        print("  1. Add Expense")
        print("  2. View Expenses")
        print("  3. Delete Expense")
        print("  4. Monthly Summary")
        print("  5. Category Breakdown")
        print("  6. Set Monthly Budget")
        print("  7. Export to CSV")
        print("  8. Exit")
        separator()

        choice = input("  Your choice: ").strip()

        if choice == "1":
            clear_screen()
            add_expense(data)
        elif choice == "2":
            clear_screen()
            view_expenses(data)
        elif choice == "3":
            clear_screen()
            delete_expense(data)
        elif choice == "4":
            clear_screen()
            monthly_summary(data)
        elif choice == "5":
            clear_screen()
            category_summary(data)
        elif choice == "6":
            clear_screen()
            set_budget(data)
        elif choice == "7":
            clear_screen()
            export_to_csv(data)
        elif choice == "8":
            print("\n  Goodbye! Keep tracking your expenses. 👋\n")
            break
        else:
            print("  ✗ Invalid choice. Try again.")
            pause()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app_data = load_data()
    main_menu(app_data)