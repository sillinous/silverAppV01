from unittest.mock import MagicMock

def test_run_discovery_success(mocker):
    """
    Tests the successful run of the /discover endpoint, mocking all external services.
    """
    # Imports are inside the test function to ensure monkeypatching happens first
    from fastapi.testclient import TestClient
    from main import app
    from arbitrage_os.db.database import SessionLocal
    from arbitrage_os.db.models import Item
    client = TestClient(app)

    # 1. Mock the external-facing functions
    mocker.patch('main.scrape_url', return_value={
        "text": "Test description with address: 123 Main St",
        "image_urls": ["http://example.com/image1.jpg"]
    })
    
    mocker.patch('main.analyze_description', return_value={
        "score": 85,
        "reasoning": "High potential deal",
        "address": "123 Main St, Anytown, USA",
        "weight_grams": 100.0,
        "purity": 0.925
    })
    
    mocker.patch('main.cleanup_and_geocode', return_value={
        "lat": 40.7128,
        "lng": -74.0060,
        "formatted_address": "123 Main St, New York, NY 10001, USA"
    })
    
    # Mock the httpx.AsyncClient for image downloading
    mock_async_client = MagicMock()
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.content = b'fake-image-bytes'
    mock_get_response.raise_for_status = MagicMock()
    
    mock_async_client.__aenter__.return_value.get.return_value = mock_get_response
    mocker.patch('httpx.AsyncClient', return_value=mock_async_client)

    mocker.patch('main.analyze_image_for_hallmarks', return_value={"hallmark": "found"})
    
    mocker.patch('main.calculate_roi', return_value={"roi_percent": 50.0})

    # 2. Call the API endpoint
    test_url = "http://example.com/test-listing"
    response = client.post(f"/discover/?url={test_url}")

    # 3. Assert the response
    assert response.status_code == 200
    response_data = response.json()
    
    assert response_data["url"] == test_url
    assert response_data["score"] == 85
    assert response_data["analysis"] == "High potential deal"
    assert response_data["latitude"] == 40.7128
    assert response_data["longitude"] == -74.0060
    assert '"roi_percent": 50.0' in response_data["roi_analysis"]
    assert '"hallmark": "found"' in response_data["image_analysis_results"]

    # 4. Verify the item was created in the database
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.url == test_url).first()
    assert db_item is not None
    assert db_item.score == 85
    assert db_item.latitude == 40.7128
    db.close()
        
def test_discover_scraping_fails(mocker):
    """
    Tests that the endpoint returns a 400 error if scraping fails to find a description.
    """
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)

    # Mock scrape_url to return no text
    mocker.patch('main.scrape_url', return_value={"text": "", "image_urls": []})

    response = client.post("/discover/?url=http://example.com/empty")

    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to scrape content from the URL."

