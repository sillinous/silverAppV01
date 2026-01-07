import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Button, Container, Alert, Spinner, Card } from 'react-bootstrap';
import { API_URL } from '../config';

const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Create FormData for OAuth2PasswordRequestForm
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axios.post(`${API_URL}/auth/token`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            // Store the access token in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('token_type', response.data.token_type);

            // Redirect to dashboard
            navigate('/');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="mt-5" style={{ maxWidth: '500px' }}>
            <Card>
                <Card.Body>
                    <h2 className="text-center mb-4">Login to Arbitrage OS</h2>
                    {error && <Alert variant="danger">{error}</Alert>}
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3" controlId="username">
                            <Form.Label>Username</Form.Label>
                            <Form.Control
                                type="text"
                                placeholder="Enter username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </Form.Group>

                        <Form.Group className="mb-3" controlId="password">
                            <Form.Label>Password</Form.Label>
                            <Form.Control
                                type="password"
                                placeholder="Enter password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </Form.Group>

                        <Button variant="primary" type="submit" disabled={loading} className="w-100">
                            {loading ? <Spinner animation="border" size="sm" /> : 'Login'}
                        </Button>
                    </Form>
                    <div className="text-center mt-3">
                        <p>Don't have an account? <Link to="/register">Register here</Link></p>
                    </div>
                </Card.Body>
            </Card>
        </Container>
    );
};

export default Login;
