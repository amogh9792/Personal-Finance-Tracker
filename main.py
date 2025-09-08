import pandas as pd
import csv
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description, date_format


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]

    @classmethod
    def initialize_csv(cls):
        try:

            pd.read_csv(cls.CSV_FILE)

        except FileNotFoundError:

            df = pd.DataFrame(columns = cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):

        new_entry = {
            "date": date, 
            "amount": amount, 
            "category": category,
            "description": description
        }

        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)

        print("Entry added successfully")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format = date_format)
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        
        mask = (df["date"] >= start_date) & (df["date"] <= end_date)

        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found in the given date range.")

        else:
            print(f"Transactions from {start_date.strftime(date_format)} to {end_date.strftime(date_format)}")

            print(filtered_df.to_string(index = False, formatters = {"date": lambda x: x.strftime(date_format)}))

            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()

            print("\n Summary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")
        
        return filtered_df
    
def add():

    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or enter for today's date:", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)

CSV.get_transactions("01-09-2025", "08-09-2025")
# add()


# CSV.initialize_csv()
# CSV.add_entry("20-07-2024", 125.65, "income", "Salary")
