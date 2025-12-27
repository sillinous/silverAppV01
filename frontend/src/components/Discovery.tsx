import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Container, Alert, Spinner } from 'react-bootstrap';

const API_URL = 'http://localhost:8000';

const Discovery: React.FC = () => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await axios.post(`${API_URL}/discover/?url=${encodeURIComponent(url)}`);
            navigate('/'); // Redirect to dashboard on success
        } catch (err) {
            setError('Failed to discover URL. Please check the URL and API server, then try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container>
            <h1 className="my-4">Discover a New Item</h1>
            <p>Enter the URL of a marketplace listing to scrape and analyze it for silver.</p>
            
            {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

            <Form onSubmit={handleSubmit} className="mb-4">
                <Form.Group className="mb-3" controlId="formUrl">
                    <Form.Label>Marketplace URL</Form.Label>
                    <Form.Control
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="e.g., https://www.facebook.com/marketplace/item/..."
                        required
                        disabled={loading}
                    />
                </Form.Group>
                <Button variant="primary" type="submit" disabled={loading}>
                    {loading ? (
                        <>
                            <Spinner
                                as="span"
                                animation="border"
                                size="sm"
                                role="status"
                                aria-hidden="true"
                            />
                            {' '}Discovering...
                        </>
                    ) : 'Discover Item'}
                </Button>
            </Form>
        </Container>
    );
};

export default Discovery;
