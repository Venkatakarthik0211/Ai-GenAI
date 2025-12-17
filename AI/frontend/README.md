# Streamlit Frontend for ML Pipeline

Web interface for natural language ML pipeline configuration using AWS Bedrock.

## Features

- **Natural Language Input**: Describe your ML task in plain English
- **Optional Hints**: Guide configuration extraction with specific hints
- **Real-time Results**: See extracted configuration and confidence scores
- **Search History**: Find similar historical prompts using full-text search
- **Analytics Dashboard**: View aggregate statistics and insights

## Installation

### Prerequisites

- Python 3.8+
- ML Pipeline API running (default: http://localhost:8000)
- PostgreSQL database (for search and analytics)
- AWS Bedrock access configured in API

### Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

## Configuration

### 1. Copy Secrets Template

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

### 2. Edit secrets.toml

```toml
# API endpoint (required)
API_BASE_URL = "http://localhost:8000"

# AWS credentials (optional - for direct Bedrock access)
AWS_ACCESS_KEY_ID = "your_key"
AWS_SECRET_ACCESS_KEY = "your_secret"
AWS_REGION = "us-east-1"
```

**IMPORTANT**: Never commit `secrets.toml` to version control!

## Running the App

### Development Mode

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at http://localhost:8501

### Production Mode

```bash
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## Usage Guide

### Run Pipeline Page

1. **Enter Data Path**: Path to your CSV file (e.g., `/data/house_prices.csv`)

2. **Describe Your Task**: Natural language prompt, examples:
   - "Predict house prices using the price column with 80/20 train-test split"
   - "Classify customer churn using status column"
   - "Build a sales forecasting model"

3. **Advanced Options (Optional)**:
   - Target Column Hint: If you know the exact column name
   - Analysis Type: Force classification or regression
   - Test Size/Random State: Override defaults

4. **Click "Extract Config & Run Pipeline"**

5. **View Results**:
   - Extracted configuration with confidence score
   - AI reasoning for each decision
   - Assumptions and warnings
   - Execution metadata and token usage

### Search History Page

1. **Enter Search Query**: Keywords to find similar prompts
   - Example: "house price prediction"

2. **Set Number of Results**: How many matches to return (1-20)

3. **Click Search**

4. **View Results**:
   - Matching prompts sorted by relevance
   - Original configurations
   - Confidence scores and timestamps

### Analytics Page

1. **Click "Refresh Analytics"** to update data

2. **View Statistics**:
   - Total prompts and success rate
   - Average confidence score
   - Breakdown by analysis type
   - Most common target columns
   - Bar chart visualizations

## Screenshots

### Main Pipeline Page
![Pipeline Page](docs/screenshots/pipeline_page.png)

### Search History
![Search Page](docs/screenshots/search_page.png)

### Analytics Dashboard
![Analytics Page](docs/screenshots/analytics_page.png)

## Troubleshooting

### Cannot Connect to API

**Problem**: "Cannot connect to API. Please ensure the API server is running."

**Solution**:
1. Check API server is running: `curl http://localhost:8000/api/v1/pipeline/health`
2. Verify API_BASE_URL in secrets.toml
3. Check firewall rules

### Request Timeout

**Problem**: "Request timeout. The operation took too long."

**Solution**:
1. Increase timeout in code (default 120s for pipeline, 30s for search)
2. Check Bedrock API latency
3. Verify data file size (large files take longer)

### Low Confidence Scores

**Problem**: Extracted configuration has low confidence (<70%)

**Solution**:
1. Provide more specific prompts
2. Use "Advanced Options" to provide hints
3. Try fallback model (Claude 3.7 Sonnet)
4. Check available column names match your description

### Secrets Not Found

**Problem**: KeyError or secrets not loading

**Solution**:
1. Ensure `.streamlit/secrets.toml` exists
2. Check TOML syntax is correct
3. Restart Streamlit after changing secrets

## Development

### Project Structure

```
frontend/
├── streamlit_app.py              # Main application
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .streamlit/
    ├── config.toml               # Streamlit configuration
    ├── secrets.toml              # Secrets (not in git)
    └── secrets.toml.template     # Template for secrets
```

### Adding New Features

1. **New API Endpoint**: Add function in `streamlit_app.py`
2. **New Page**: Add to navigation radio button and create page function
3. **New Metric**: Update analytics query in backend, display in `analytics_page()`

### Code Style

- Follow PEP 8 conventions
- Use type hints
- Add docstrings to functions
- Keep functions focused and small

## Docker Deployment

### Build Image

```bash
docker build -t ml-pipeline-frontend .
```

### Run Container

```bash
docker run -p 8501:8501 \
  -e API_BASE_URL=http://api:8000 \
  ml-pipeline-frontend
```

### Docker Compose

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:8000
    depends_on:
      - api
```

## Performance Tips

1. **Caching**: Streamlit automatically caches function results
2. **Session State**: Use `st.session_state` for user data
3. **Batch Requests**: Group API calls when possible
4. **Lazy Loading**: Load data only when needed

## Security Considerations

1. **Secrets Management**: Never commit secrets.toml
2. **Input Validation**: Always validate user inputs
3. **HTTPS**: Use HTTPS in production
4. **Authentication**: Add auth layer for production (not included)
5. **Rate Limiting**: Implement rate limiting on API

## Related Documentation

- [API Documentation](../api/README.md)
- [Database Setup](../database/README.md)
- [Bedrock Setup Guide](../docs/BEDROCK_SETUP.md)
- [System Architecture](../docs/SYSTEM_ARCHITECTURE.md)
