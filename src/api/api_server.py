from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import logging
from datetime import datetime

from src.models.fraud_detector import FraudDetector
from src.feature_engineering.feature_processor import FeatureProcessor
from src.database.db_connector import MongoDBConnector
from src.config.config_manager import ConfigurationManager

# Initialize FastAPI app
app = FastAPI(
    title="Fraud Detection API",
    description="API for real-time fraud detection and transaction monitoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    transaction_id: str
    user_id: int
    amount: float
    currency: str
    merchant_category: str
    timestamp: datetime
    location: Dict[str, float]

@app.post("/api/v1/predict")
async def predict_fraud(
    transaction: Transaction,
    db: MongoDBConnector = Depends(get_db)
):
    """Predict fraud probability for a transaction."""
    try:
        # Store transaction
        db.store_transaction(transaction.dict())
        
        # Generate features
        features = feature_processor.process_transaction(transaction.dict())
        
        # Get prediction
        prediction = fraud_detector.predict(features)
        
        return {
            "transaction_id": transaction.transaction_id,
            **prediction,
            "features": features
        }
        
    except Exception as e:
        logging.error(f"Error processing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def start_api_server():
    """Start the API server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    start_api_server()