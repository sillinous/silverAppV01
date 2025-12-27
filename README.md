# Arbitrage OS

Arbitrage OS is a powerful, AI-driven application designed to dominate local silver markets. It automates the entire arbitrage workflow, from discovering undervalued silver in online marketplaces to optimizing your route to acquire it.

This application is built as a FastAPI web service, exposing a series of endpoints that correspond to its core modules.

## Core Modules

1.  **Automated Discovery:** Ingests data from marketplace URLs (`ScrapeGraphAI`), uses an LLM to analyze the text for the likelihood of silver (`OpenAI`), and extracts potential addresses.
2.  **Logistics & Geocoding:** Cleans up messy, colloquial addresses using an LLM (`OpenAI`) and converts them to precise geographic coordinates (`GeoPy`). It then optimizes a multi-stop route for acquiring the items (`Route4Me`).
3.  **Computer Vision Verification:** Analyzes images of items to identify silver hallmarks and patterns, providing an extra layer of verification (`Ximilar AI`).
4.  **Real-Time Valuation:** Calculates the real-time value and potential ROI of an item based on its weight, purity, and the live spot price of silver (`Metals-API`).

## Getting Started

### Prerequisites

- Python 3.8+
- An active internet connection

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd silverAppV01
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

This application requires several API keys and configuration values to be set as environment variables.

Create a `.env` file in the root of the project and add the following key-value pairs. The application is set up to work with these variables, but you can also set them directly in your shell.

```
# For Module 1: Discovery & AI Analysis
OPENAI_API_KEY="your_openai_api_key"

# For Module 2: Logistics & Routing
MAPBOX_API_KEY="your_mapbox_api_key"

# For Module 3: Vision Verification
XIMILAR_API_TOKEN="your_ximilar_api_token"
XIMILAR_WORKSPACE_ID="your_ximilar_workspace_id"
XIMILAR_TASK_ID="your_ximilar_recognition_task_id"

# For Module 4: Real-Time Valuation
METALS_API_KEY="your_metals_api_key"
```

### Running the Application

Once the dependencies are installed and the environment variables are set, you can run the application using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

Here is a summary of the available API endpoints:

### Discovery

- **POST `/discover/`**
  - **Description:** Scrapes a URL, analyzes its content for silver, and extracts an address.
  - **Query Parameter:** `url` (string)
  - **Example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/discover/?url=http://example.com"
    ```

### Logistics

- **POST `/logistics/geocode/`**
  - **Description:** Cleans and geocodes a messy address string.
  - **Request Body:** `{"address": "your messy address"}`
  - **Example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/logistics/geocode/" \
    -H "Content-Type: application/json" \
    -d '{"address": "blue house on corner of 5th and main"}'
    ```

- **POST `/logistics/optimize_route/`**
  - **Description:** Takes a list of coordinates and returns an optimized route.
  - **Request Body:** `{"coordinates": [{"lat": 40.7, "lng": -74.0}, ...]}`
  - **Example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/logistics/optimize_route/" \
    -H "Content-Type: application/json" \
    -d '{"coordinates": [{"lat": 40.7128, "lng": -74.0060}, {"lat": 34.0522, "lng": -118.2437}]}'
    ```

### Verification

- **POST `/verification/analyze_image/`**
  - **Description:** Analyzes an uploaded image for silver hallmarks.
  - **Form Data:** `file` (image file)
  - **Example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/verification/analyze_image/" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@/path/to/your/image.jpg"
    ```

### Valuation

- **POST `/valuation/calculate_roi/`**
  - **Description:** Calculates the ROI for a silver item based on live market data.
  - **Request Body:** `{"weight_grams": 100, "purity": 0.925, "purchase_price": 50}`
  - **Example:**
    ```bash
    curl -X POST "http://127.0.0.1:8000/valuation/calculate_roi/" \
    -H "Content-Type: application/json" \
    -d '{"weight_grams": 100, "purity": 0.925, "purchase_price": 50}'
    ```
