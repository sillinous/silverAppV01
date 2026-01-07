import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, useNavigate } from 'react-router-dom';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import Dashboard from './components/Dashboard';
import Discovery from './components/Discovery';
import Logistics from './components/Logistics';
import Verification from './components/Verification';
import Valuation from './components/Valuation';
import MultiDiscovery from './components/MultiDiscovery';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

const LogoutButton: React.FC = () => {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    navigate('/login');
  };

  if (!isLoggedIn) return null;

  return (
    <Button variant="outline-light" size="sm" onClick={handleLogout}>
      Logout
    </Button>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg">
          <Container>
            <Navbar.Brand as={Link} to="/">Arbitrage OS</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
                <Nav.Link as={Link} to="/discover">Discovery</Nav.Link>
                <Nav.Link as={Link} to="/multi-discover">Multi-Discovery</Nav.Link>
                <Nav.Link as={Link} to="/logistics">Logistics</Nav.Link>
                <Nav.Link as={Link} to="/verification">Verification</Nav.Link>
                <Nav.Link as={Link} to="/valuation">Valuation</Nav.Link>
              </Nav>
              <LogoutButton />
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container className="mt-4">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/discover" element={<ProtectedRoute><Discovery /></ProtectedRoute>} />
            <Route path="/multi-discover" element={<ProtectedRoute><MultiDiscovery /></ProtectedRoute>} />
            <Route path="/logistics" element={<ProtectedRoute><Logistics /></ProtectedRoute>} />
            <Route path="/verification" element={<ProtectedRoute><Verification /></ProtectedRoute>} />
            <Route path="/valuation" element={<ProtectedRoute><Valuation /></ProtectedRoute>} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;