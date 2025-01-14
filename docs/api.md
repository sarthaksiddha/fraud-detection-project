# API Documentation

## Overview
The Fraud Detection API provides real-time transaction monitoring and fraud detection capabilities.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Predict Fraud

**Endpoint:** `/api/v1/predict`

**Method:** POST

**Request Body:**
```json
{
    "transaction_id": "string",
    "user_id": "integer",
    "amount": "float",
    "currency": "string",
    "merchant_category": "string",
    "timestamp": "string (ISO format)",
    "location": {
        "latitude": "float",
        "longitude": "float"
    }
}
```

**Response:**
```json
{
    "transaction_id": "string",
    "is_fraud": "boolean",
    "fraud_probability": "float",
    "anomaly_score": "float",
    "features": {
        "feature1": "float",
        "feature2": "float"
    }
}
```

### 2. Get Transaction History

**Endpoint:** `/api/v1/transactions/{user_id}`

**Method:** GET

**Parameters:**
- `user_id`: Integer
- `start_date`: Optional[string] (ISO format)
- `end_date`: Optional[string] (ISO format)

**Response:**
```json
{
    "transactions": [
        {
            "transaction_id": "string",
            "amount": "float",
            "timestamp": "string",
            "fraud_probability": "float"
        }
    ]
}
```

### 3. Update Alert Status

**Endpoint:** `/api/v1/alerts/{transaction_id}`

**Method:** PUT

**Request Body:**
```json
{
    "status": "string",
    "notes": "string"
}
```

**Response:**
```json
{
    "message": "Alert updated successfully"
}
```

## Error Responses

**400 Bad Request:**
```json
{
    "detail": "Invalid request parameters"
}
```

**500 Internal Server Error:**
```json
{
    "detail": "Internal server error message"
}
```

## Authentication
All API endpoints require an API key to be included in the request headers:

```
X-API-Key: your_api_key_here
```