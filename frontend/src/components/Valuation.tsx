import React, { useState } from 'react';
import axios from 'axios';
import { Form, Button, Container, Alert, Spinner, Card, Row, Col } from 'react-bootstrap';

const API_URL = 'http://localhost:8000';

interface RoiFormState {
    weight_grams: string;
    purity: string;
    purchase_price: string;
}

interface RoiResult {
    silver_value: number;
    profit: number;
    roi_percentage: number;
}

const Valuation: React.FC = () => {
    const [formState, setFormState] = useState<RoiFormState>({
        weight_grams: '',
        purity: '0.925', // Default to sterling
        purchase_price: '',
    });
    const [result, setResult] = useState<RoiResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = event.target;
        setFormState(prevState => ({
            ...prevState,
            [name]: value,
        }));
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const payload = {
                weight_grams: parseFloat(formState.weight_grams),
                purity: parseFloat(formState.purity),
                purchase_price: parseFloat(formState.purchase_price),
            };
            const response = await axios.post<RoiResult>(`${API_URL}/valuation/calculate_roi/`, payload);
            setResult(response.data);
        } catch (err) {
            setError('Failed to calculate ROI. Please check your inputs and the API server.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container>
            <h1 className="my-4">Real-Time Valuation</h1>
            <p>Calculate the potential ROI of a silver item based on its weight, purity, and your purchase price, using live market data.</p>
            
            <Card className="mb-4">
                <Card.Body>
                    <Form onSubmit={handleSubmit}>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3" controlId="weight_grams">
                                    <Form.Label>Weight (grams)</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="weight_grams"
                                        value={formState.weight_grams}
                                        onChange={handleChange}
                                        placeholder="e.g., 31.1"
                                        required
                                        step="any"
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3" controlId="purity">
                                    <Form.Label>Purity</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="purity"
                                        value={formState.purity}
                                        onChange={handleChange}
                                        placeholder="e.g., 0.925 for Sterling"
                                        required
                                        step="any"
                                        min="0"
                                        max="1"
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3" controlId="purchase_price">
                                    <Form.Label>Purchase Price ($)</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="purchase_price"
                                        value={formState.purchase_price}
                                        onChange={handleChange}
                                        placeholder="e.g., 20.00"
                                        required
                                        step="any"
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Button variant="primary" type="submit" disabled={loading}>
                            {loading ? <Spinner as="span" animation="border" size="sm" /> : 'Calculate ROI'}
                        </Button>
                    </Form>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

            {result && (
                <Card bg="light">
                    <Card.Header as="h2">Calculation Result</Card.Header>
                    <Card.Body>
                        <Row className="text-center">
                            <Col>
                                <Card.Title>Melt Value</Card.Title>
                                <Card.Text className="fs-4">${result.silver_value.toFixed(2)}</Card.Text>
                            </Col>
                            <Col>
                                <Card.Title>Potential Profit</Card.Title>
                                <Card.Text className={`fs-4 ${result.profit > 0 ? 'text-success' : 'text-danger'}`}>
                                    ${result.profit.toFixed(2)}
                                </Card.Text>
                            </Col>
                            <Col>
                                <Card.Title>ROI</Card.Title>
                                <Card.Text className={`fs-4 ${result.roi_percentage > 0 ? 'text-success' : 'text-danger'}`}>
                                    {result.roi_percentage.toFixed(2)}%
                                </Card.Text>
                            </Col>
                        </Row>
                    </Card.Body>
                </Card>
            )}
        </Container>
    );
};

export default Valuation;
