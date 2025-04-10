# CTCAE Symptom Standardizer

A tool for standardizing clinical symptom descriptions to CTCAE terminology using RAG (Retrieval Augmented Generation) with InterSystems IRIS Vector Store.

## Features

- Processes the official CTCAE v5.0 Excel file from NCI
- Maps free-text symptom descriptions to standardized CTCAE terms
- Determines appropriate symptom grades based on severity descriptions
- Uses vector embeddings stored in InterSystems IRIS for efficient similarity search
- Provides API and command-line interfaces

## Quick Start

### Docker Setup (Recommended)

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ctcae-standardizer.git
cd ctcae-standardizer
```

2. Run the setup script:
```bash
python setup_docker.py
```

3. Access the services:
   - REST API: http://localhost:8000
   - Jupyter Notebook: http://localhost:8888
   - IRIS Management Portal: http://localhost:5274/csp/sys/UtilHome.csp

### Command Line Usage

```bash
# Match a symptom to CTCAE terminology
python scripts/run_symptom_matcher.py "severe headache with nausea" --details "occurs daily, pain level 8/10"
```

### API Usage

```bash
# Using curl
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{"symptom": "severe headache with nausea", "details": "occurs daily, pain level 8/10"}'
```

## How It Works

1. **Data Processing**: The system extracts structured data from the CTCAE v5.0 Excel file, including terms, grades, and descriptions.

2. **Vector Indexing**: CTCAE terms and grade descriptions are embedded and stored in InterSystems IRIS Vector Store for similarity search.

3. **Symptom Matching**: When a user submits a symptom description:
   - The system retrieves the most similar CTCAE terms using vector search
   - It then finds the most appropriate grade descriptions for the term
   - An LLM makes the final match decision based on retrieved context

4. **Result**: The user receives the standardized CTCAE term, grade, and description that best matches their symptom.

## Project Structure

- `scripts/`: Command-line tools for data processing and symptom matching
- `src/`: Core application code and API implementation
- `notebooks/`: Jupyter notebooks for data exploration and examples
- `data/`: Storage for CTCAE data and processed files

## Requirements

- Docker and Docker Compose
- Python 3.8+
- OpenAI API key
- InterSystems IRIS (included in Docker setup)

## License

MIT