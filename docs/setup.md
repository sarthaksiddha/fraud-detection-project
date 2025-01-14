# Setup Guide

## Prerequisites

### System Requirements
- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 20GB minimum

### Software Requirements
- Python 3.9+
- Docker & Docker Compose
- Git

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/sarthaksiddha/fraud-detection-project.git
cd fraud-detection-project
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start required services:
```bash
docker-compose up -d kafka mongodb
```

6. Initialize the database:
```bash
python scripts/init_db.py
```

7. Start the API server:
```bash
python src/api/api_server.py
```

## Configuration

### Kafka Configuration
Edit `config/config.yaml` to configure Kafka settings:
```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  group_id: "fraud_detection_group"
```

### MongoDB Configuration
Update MongoDB settings in `config/config.yaml`:
```yaml
mongodb:
  host: "localhost"
  port: 27017
  database: "fraud_detection"
```

### Model Configuration
Adjust model parameters in `config/config.yaml`:
```yaml
fraud_detection:
  alert_threshold: 0.8
  model:
    contamination: 0.1
    random_state: 42
```

## Monitoring Setup

1. Start Prometheus:
```bash
docker-compose up -d prometheus
```

2. Access Grafana dashboard:
```
http://localhost:3000
```

3. Import dashboard templates from `monitoring/dashboards/`

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run with coverage:
```bash
python -m pytest --cov=src tests/
```