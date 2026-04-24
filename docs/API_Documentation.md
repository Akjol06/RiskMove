# 🔌 Документация API

## 🚀 Базовый URL
`http://localhost:8000/api/v1`

---

## 📋 Эндпоинт Предсказания
**POST** `/predict`

### 📥 Входные данные (Request Body)
```json
{
  "age": 30,
  "monthly_income": 50000.0,
  "employment_years": 5.0,
  "loan_amount": 200000.0,
  "loan_term_months": 36,
  "interest_rate": 15.0,
  "past_due_30d": 0,
  "inquiries_6m": 1
}
```

### 📤 Структура ответа (Response Body)
```json
{
  "probability": 0.0548,
  "base_value": 0.3062,
  "decision": "APPROVE",
  "explanation": [
    { 
      "feature": "interest_rate", 
      "impact": -0.1505,
      "description": "снижает риск на 15.1%" 
    },
    { 
      "feature": "loan_amount", 
      "impact": -0.0408,
      "description": "снижает риск на 4.1%" 
    }
  ],
  "message": "Заявка одобрена на основе низкого профиля риска.",
  "analysis_summary": "Основные факторы: Ставка снижает вероятность дефолта на 15.1%."
}
```

---

## 🛠 Как протестировать

### Через `curl` 💻
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: application/json" \
     -d '{"age": 30, "monthly_income": 50000.0, "employment_years": 5.0, "loan_amount": 200000.0, "loan_term_months": 36, "interest_rate": 15.0, "past_due_30d": 0, "inquiries_6m": 1}'
```

### Через Python 🐍
```python
import requests
response = requests.post("http://localhost:8000/api/v1/predict", json={...})
print(response.json())
```

> [!TIP]
> Вы также можете использовать **Интерактивный Swagger UI** по адресу: `http://localhost:8000/docs` 🔍
