import requests
import json

def test_predict():
    url = "http://localhost:8000/api/v1/predict"
    payload = {
        "age": 30,
        "monthly_income": 50000.0,
        "employment_years": 5.0,
        "loan_amount": 200000.0,
        "loan_term_months": 36,
        "interest_rate": 15.0,
        "past_due_30d": 0,
        "inquiries_6m": 1
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_predict()
