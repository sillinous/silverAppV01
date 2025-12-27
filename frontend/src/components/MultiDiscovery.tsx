import React, { useState } from 'react';
import axios from 'axios';
import { Container, Form, Button, Alert, Spinner, ListGroup } from 'react-bootstrap';

const API_URL = 'http://localhost:8000';

interface DiscoveryResult {
    url: string;
    status: string;
    item_id?: number;
    detail?: string;
}

const MultiDiscovery: React.FC = () => {
    const [urls, setUrls] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [results, setResults] = useState<DiscoveryResult[]>([]);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResults([]);

        const urlList = urls.split('\n').map(u => u.trim()).filter(u => u);

        if (urlList.length === 0) {
            setError('Please enter at least one URL.');
            setLoading(false);
            return;
        }

        try {
            const response = await axios.post<DiscoveryResult[]>(`${API_URL}/discover_multiple/`, { urls: urlList });
            setResults(response.data);
        } catch (err) {
            setError('Failed to run multi-discovery. Please check the URLs and API server, then try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container>
            <h1 className="my-4">Multi-Item Discovery</h1>
            <p>Enter multiple marketplace URLs (one per line) to scrape and analyze them in batch.</p>

            {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

            <Form onSubmit={handleSubmit} className="mb-4">
                <Form.Group className="mb-3" controlId="formUrls">
                    <Form.Label>Marketplace URLs</Form.Label>
                    <Form.Control
                        as="textarea"
                        rows={10}
                        value={urls}
                        onChange={(e) => setUrls(e.target.value)}
                        placeholder="e.g.,
https://www.facebook.com/marketplace/item/12345/
https://www.craigslist.org/d/for-sale/78901/..."
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
                            {' '}Discovering Multiple Items...
                        </>
                    ) : 'Discover Multiple Items'}
                </Button>
            </Form>

            {results.length > 0 && (
                <div className="mt-4">
                    <h3>Discovery Results:</h3>
                    <ListGroup>
                        {results.map((result, index) => (
                            <ListGroup.Item key={index} variant={result.status === "success" ? "success" : "danger"}>
                                <strong>URL:</strong> {result.url} <br />
                                <strong>Status:</strong> {result.status}
                                {result.item_id && ` (Item ID: ${result.item_id})`}
                                {result.detail && ` - ${result.detail}`}
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </div>
            )}
        </Container>
    );
};

export default MultiDiscovery;
