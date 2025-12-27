import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Alert, Spinner, Card, Row, Col, Badge } from 'react-bootstrap';

const API_URL = 'http://localhost:8000';

interface Item {
    id: number;
    url: string;
    description: string;
    analysis: string; // Now stores only AI reasoning
    status: string;
    score: number | null;
    latitude: number | null;
    longitude: number | null;
    image_urls: string | null; // JSON string of image URLs
}

const Dashboard: React.FC = () => {
    const [items, setItems] = useState<Item[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchItems = async () => {
        try {
            setLoading(true);
            const response = await axios.get<Item[]>(`${API_URL}/items/`);
            // Sort items by ID descending to show newest first
            setItems(response.data.sort((a, b) => b.id - a.id));
            setError(null);
        } catch (err) {
            setError('Failed to fetch items.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    const getScoreBadgeVariant = (score: number | null) => {
        if (score === null) return 'secondary';
        if (score >= 8) return 'success';
        if (score >= 5) return 'warning';
        return 'danger';
    };

    const parseImageUrls = (imageUrlsJson: string | null): string[] => {
        try {
            return imageUrlsJson ? JSON.parse(imageUrlsJson) : [];
        } catch (e) {
            console.error("Error parsing image URLs:", e);
            return [];
        }
    };

    if (loading) {
        return (
            <Container className="text-center mt-5">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className="mt-5">
                <Alert variant="danger">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container>
            <h1 className="my-4">Discovered Items Dashboard</h1>
            {items.length > 0 ? (
                <Row xs={1} md={2} lg={3} className="g-4">
                    {items.map((item) => {
                        const imageUrls = parseImageUrls(item.image_urls);
                        const firstImageUrl = imageUrls.length > 0 ? imageUrls[0] : null;
                        const googleMapsLink = (item.latitude && item.longitude) 
                            ? `https://www.google.com/maps/search/?api=1&query=${item.latitude},${item.longitude}`
                            : null;

                        return (
                            <Col key={item.id}>
                                <Card className="h-100">
                                    {firstImageUrl && (
                                        <Card.Img variant="top" src={firstImageUrl} alt="Item image" style={{ height: '200px', objectFit: 'cover' }} />
                                    )}
                                    <Card.Header as="h5">
                                        Item #{item.id}
                                        <Badge bg={getScoreBadgeVariant(item.score)} className="ms-2">
                                            Score: {item.score !== null ? `${item.score} / 10` : 'N/A'}
                                        </Badge>
                                    </Card.Header>
                                    <Card.Body>
                                        <Card.Text>
                                            <strong>Reasoning:</strong> {item.analysis || 'N/A'}
                                        </Card.Text>
                                        <Card.Text>
                                            <strong>Location:</strong> 
                                            {googleMapsLink ? (
                                                <a href={googleMapsLink} target="_blank" rel="noopener noreferrer">
                                                    {item.latitude}, {item.longitude}
                                                </a>
                                            ) : 'Not found'}
                                        </Card.Text>
                                        <Card.Text>
                                            <strong>Status:</strong> <Badge bg="secondary">{item.status}</Badge>
                                        </Card.Text>
                                    </Card.Body>
                                    <Card.Footer>
                                        <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
                                            View Listing
                                        </a>
                                    </Card.Footer>
                                </Card>
                            </Col>
                        );
                    })}
                </Row>
            ) : (
                <Alert variant="info">No items discovered yet. Use the "Discovery" page to add some.</Alert>
            )}
        </Container>
    );
};

export default Dashboard;
