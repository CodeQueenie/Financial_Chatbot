import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Questions for the user
questions = [
    "How much is your net fixed income per month?",
    "Transportation costs per month?",
    "Food costs per month?",
    "Outing expenses per month?",
    "Other fixed costs per month?",
    "Do you have any variable costs this year?",
    "How much available savings do you have?",
]

# Month list
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Dictionary to store user responses
user_responses = {}

def get_variable_costs():
    """Capture variable costs per month from the user"""
    months_dict = {}
    for i, month in enumerate(months):
        cost = st.text_input(f"{month} variable costs:", key=f"month_{i}")
        months_dict[month] = int(cost) if cost.isdigit() else 0
    user_responses["Variable costs per month"] = months_dict
    return months_dict

def calculate_available_amount_to_invest():
    savings = int(user_responses.get("How much available savings do you have?", 0))
    income = int(user_responses.get("How much is your net fixed income per month?", 0))
    return savings - income

def calculate_savings_per_month():
    """Calculate the user's savings per month after expenses."""
    income = int(user_responses.get("How much is your net fixed income per month?", 0))
    expenses = sum([
        int(user_responses.get(q, 0)) for q in [
            "Transportation costs per month?", "Food costs per month?",
            "Outing expenses per month?", "Other fixed costs per month?"
        ]
    ])
    return income - expenses

def calculate_savings_per_year():
    return calculate_savings_per_month() * 12

def calculate_income_and_costs():
    """Calculate yearly income and expenses."""
    yearly_income = [int(user_responses.get("How much is your net fixed income per month?", 0))] * len(months)
    
    total_costs_per_year = [
        sum([
            int(user_responses.get(q, 0)) for q in [
                "Transportation costs per month?", "Food costs per month?",
                "Outing expenses per month?", "Other fixed costs per month?"
            ]
        ])
    ] * len(months)

    # Add variable costs if applicable
    variable_costs = user_responses.get("Variable costs per month", {})
    for i, month in enumerate(months):
        total_costs_per_year[i] += variable_costs.get(month, 0)

    return yearly_income, total_costs_per_year

def plot_monthly_breakdown():
    revenus, charges = calculate_income_and_costs()

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = np.arange(len(months))

    income_bars = ax.bar(index - bar_width/4, revenus, bar_width/2, label='Income', color='green')
    costs_bars = ax.bar(index + bar_width/4, charges, bar_width/2, label='Costs', color='red')

    ax.set_xlabel('Month')
    ax.set_ylabel('Value (EUR)')
    ax.set_title('Income and Costs Breakdown (per Month)')
    ax.set_xticks(index)
    ax.set_xticklabels(months)

    for bar, data in zip(income_bars, revenus):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50, str(data), ha='center', va='bottom')

    for bar, data in zip(costs_bars, charges):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50, str(data), ha='center', va='bottom')

    ax.legend()
    st.pyplot(fig)

def plot_pie_chart():
    """Plot a pie chart of expenses and investment capacity."""
    variable_costs = user_responses.get("Variable costs per month", {})

    income, _ = calculate_income_and_costs()
    total_income = sum(income)
    
    fixed_expenses = sum([
        int(user_responses.get(q, 0)) for q in [
            "Transportation costs per month?", "Food costs per month?",
            "Outing expenses per month?", "Other fixed costs per month?"
        ]
    ])

    variable_expense_total = sum(variable_costs.values())
    investment_capacity = total_income - fixed_expenses - variable_expense_total

    sizes = [variable_expense_total, fixed_expenses, investment_capacity]
    labels = ["Variable Costs", "Fixed Costs", "Investment Capacity"]

    if sum(sizes) > 0:
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Ensures pie is a circle
        plt.title('Distribution of Costs and Investment Capacity')
        st.pyplot(plt)
    else:
        st.write("No financial data entered yet.")

def check_integer(user_response, question):
    """Ensure valid integer input."""
    if user_response == "":
        return 0
    try:
        return int(user_response)
    except ValueError:
        st.warning("Error: Please enter a valid integer.")
        return 0

def get_personal_finance():
    """Main function to collect financial data from the user."""
    st.title("💰 Personal Finance Assistant")
    st.write("Chatbot: Welcome to the personal finance module!")

    for i, question in enumerate(questions):
        user_response = st.text_input(question, key=f"finance_input_{i}")
        if "costs" in question.lower() or "income" in question.lower():
            user_responses[question] = check_integer(user_response, question)
        elif question == "Do you have any variable costs this year?":
            response = st.radio("Do you have variable costs this year?", ["No", "Yes"], key=f"variable_{i}")
            if response == "Yes":
                user_responses["Variable costs per month"] = get_variable_costs()
            else:
                user_responses["Variable costs per month"] = {}

    if st.button("Calculate Finances"):
        st.write("### Financial Summary")
        st.write(f"📌 **Available Amount to Invest:** {calculate_available_amount_to_invest()} €")
        st.write(f"📌 **Investment Capacity (per month):** {calculate_savings_per_month()} €")
        st.write(f"📌 **Investment Capacity (per year):** {calculate_savings_per_year()} €")

        # Display charts
        plot_monthly_breakdown()
        plot_pie_chart()