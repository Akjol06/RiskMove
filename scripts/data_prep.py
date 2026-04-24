import pandas as pd
import numpy as np
from pathlib import Path

def prepare_data():
    data_path = Path("data/credit_scoring_dataset.csv")
    if not data_path.exists():
        print("Data not found!")
        return

    df = pd.read_csv(data_path)
    
    # 1. Create Data Dictionary
    dictionary = [
        {"feature": "credit_id", "description": "Unique ID for each credit application", "type": "int"},
        {"feature": "age", "description": "Age of the applicant", "type": "int"},
        {"feature": "monthly_income", "description": "Monthly income of the applicant", "type": "float"},
        {"feature": "employment_years", "description": "Number of years in current employment", "type": "float"},
        {"feature": "loan_amount", "description": "Requested loan amount", "type": "float"},
        {"feature": "loan_term_months", "description": "Loan term in months", "type": "int"},
        {"feature": "interest_rate", "description": "Interest rate for the loan", "type": "float"},
        {"feature": "past_due_30d", "description": "Number of times past due 30 days in last 2 years", "type": "int"},
        {"feature": "inquiries_6m", "description": "Number of credit inquiries in last 6 months", "type": "int"},
        {"feature": "target", "description": "1 = Default (Bad), 0 = Non-Default (Good)", "type": "int"},
    ]
    pd.DataFrame(dictionary).to_csv("data/data_dictionary.csv", index=False)
    print("Created data/data_dictionary.csv")

    # 2. Create Correlations
    numeric_df = df.select_dtypes(include=[np.number])
    correlations = numeric_df.corr()['target'].sort_values(ascending=False).reset_index()
    correlations.columns = ['feature', 'correlation_with_target']
    correlations.to_csv("data/correlations_with_target.csv", index=False)
    print("Created data/correlations_with_target.csv")

if __name__ == "__main__":
    prepare_data()
