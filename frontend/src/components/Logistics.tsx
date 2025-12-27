import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Form, Button, Container, Alert, Spinner, Card, ListGroup, Row, Col } from 'react-bootstrap';

const API_URL = 'http://localhost:8000';

interface Item {
    id: number;
    url: string;
    analysis: string;
}

interface GeocodedItem extends Item {
    address: string;
    lat: number;
    lng: number;
}

// Assuming the routing API returns an array of coordinates in order
interface OptimizedRoute {
    optimized_route: Array<{ lat: number; lng: number }>;
    // Define based on actual API response from Route4Me
    [key: string]: any;
}

const Logistics: React.FC = () => {
    const [geocodedItems, setGeocodedItems] = useState<GeocodedItem[]>([]);
    const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
    const [route, setRoute] = useState<OptimizedRoute | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const parseAnalysisAndFilter = (items: Item[]): GeocodedItem[] => {
        return items.map(item => {
            try {
                const analysis = JSON.parse(item.analysis);
                // Check for a valid address object with lat/lng
                if (analysis.address && typeof analysis.address === 'object' && analysis.address.lat && analysis.address.lng) {
                    return {
                        ...item,
                        address: analysis.address.formatted_address || `${analysis.address.lat}, ${analysis.address.lng}`,
                        lat: analysis.address.lat,
                        lng: analysis.address.lng,
                    };
                }
                return null;
            } catch (e) {
                return null;
            }
        }).filter((item): item is GeocodedItem => item !== null);
    };

    useEffect(() => {
        const fetchItems = async () => {
            setLoading(true);
            try {
                const response = await axios.get<Item[]>(`${API_URL}/items/`);
                const filtered = parseAnalysisAndFilter(response.data);
                setGeocodedItems(filtered);
            } catch (err) {
                setError('Failed to fetch items for routing.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchItems();
    }, []);

    const handleSelect = (itemId: number) => {
        setSelectedItems(prev => {
            const newSelection = new Set(prev);
            if (newSelection.has(itemId)) {
                newSelection.delete(itemId);
            } else {
                newSelection.add(itemId);
            }
            return newSelection;
        });
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (selectedItems.size < 2) {
            setError("Please select at least two locations to optimize a route.");
            return;
        }

        setLoading(true);
        setError(null);
        setRoute(null);

        const coordinates = geocodedItems
            .filter(item => selectedItems.has(item.id))
            .map(item => ({ lat: item.lat, lng: item.lng }));

        try {
            const response = await axios.post<OptimizedRoute>(`${API_URL}/logistics/optimize_route/`, { coordinates });
            setRoute(response.data);
        } catch (err) {
            setError('Failed to optimize route.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container>
            <h1 className="my-4">Logistics & Route Optimization</h1>
            <p>Select discovered items with valid addresses to calculate the most efficient multi-stop route.</p>
            
            <Row>
                <Col md={6}>
                    <Card>
                        <Card.Header>Available Locations</Card.Header>
                        <Card.Body>
                            {loading && <Spinner animation="border" />}
                            {error && <Alert variant="warning">{error}</Alert>}
                            <Form onSubmit={handleSubmit}>
                                <ListGroup style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                    {geocodedItems.length > 0 ? geocodedItems.map(item => (
                                        <ListGroup.Item key={item.id}>
                                            <Form.Check 
                                                type="checkbox"
                                                id={`item-${item.id}`}
                                                label={
                                                    <>
                                                        <strong>{item.address}</strong>
                                                        <br />
                                                        <small><a href={item.url} target="_blank" rel="noopener noreferrer">Original Listing</a></small>
                                                    </>
                                                }
                                                checked={selectedItems.has(item.id)}
                                                onChange={() => handleSelect(item.id)}
                                            />
                                        </ListGroup.Item>
                                    )) : <p>No items with geocoded addresses found.</p>}
                                </ListGroup>
                                <Button variant="primary" type="submit" disabled={loading || selectedItems.size < 2} className="mt-3">
                                    Optimize Route
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={6}>
                    {route && (
                        <Card>
                            <Card.Header>Optimized Route</Card.Header>
                            <Card.Body>
                                <p>Follow the stops in this order for the most efficient route.</p>
                                <ListGroup variant="flush">
                                    {/* This is a simplified representation. The actual route data structure might be different. */}
                                    {route.optimized_route?.map((stop, index) => (
                                        <ListGroup.Item key={index}>
                                            <strong>Stop {index + 1}:</strong> Lat: {stop.lat.toFixed(4)}, Lng: {stop.lng.toFixed(4)}
                                        </ListGroup.Item>
                                    ))}
                                </ListGroup>
                            </Card.Body>
                        </Card>
                    )}
                </Col>
            </Row>
        </Container>
    );
};

export default Logistics;
