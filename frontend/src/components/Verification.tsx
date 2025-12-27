import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { Form, Button, Container, Alert, Spinner, Card, Image } from 'react-bootstrap';
import { useDropzone } from 'react-dropzone';

const API_URL = 'http://localhost:8000';

interface AnalysisResult {
    // Define based on expected API response. Let's assume it's an array of objects.
    records?: Array<{
        _id: string;
        best_label: { name: string; prob: number };
    }>;
    // Add other potential fields from the response
    [key: string]: any;
}

const Verification: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles[0]) {
            const currentFile = acceptedFiles[0];
            setFile(currentFile);
            setPreview(URL.createObjectURL(currentFile));
            setResult(null);
            setError(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png'] },
        multiple: false,
    });

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (!file) {
            setError('Please select an image file first.');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post<AnalysisResult>(`${API_URL}/verification/analyze_image/`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err) {
            setError('Failed to analyze image. Please check the file and the API server.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const renderResult = () => {
        if (!result) return null;

        if (result.records && result.records.length > 0) {
            return (
                <ul>
                    {result.records.map(record => (
                        <li key={record._id}>
                            Found: <strong>{record.best_label.name}</strong> with {Math.round(record.best_label.prob * 100)}% confidence.
                        </li>
                    ))}
                </ul>
            );
        }
        
        return <p>No specific hallmarks recognized, or the API returned an unexpected format.</p>;
    };

    return (
        <Container>
            <h1 className="my-4">Image Verification</h1>
            <p>Upload an image of an item to analyze it for silver hallmarks using computer vision.</p>
            
            <Card className="mb-4">
                <Card.Body>
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>Item Image</Form.Label>
                            <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                                <input {...getInputProps()} />
                                {preview ? (
                                    <Image src={preview} thumbnail style={{ maxHeight: '200px' }} />
                                ) : (
                                    <p>Drag 'n' drop an image here, or click to select one</p>
                                )}
                            </div>
                        </Form.Group>
                        <Button variant="primary" type="submit" disabled={!file || loading}>
                            {loading ? <Spinner as="span" animation="border" size="sm" /> : 'Analyze Image'}
                        </Button>
                    </Form>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger" onClose={() => setError(null)} dismissible>{error}</Alert>}

            {result && (
                <Card bg="light">
                    <Card.Header as="h2">Analysis Result</Card.Header>
                    <Card.Body>
                        {renderResult()}
                    </Card.Body>
                </Card>
            )}
        </Container>
    );
};

export default Verification;
