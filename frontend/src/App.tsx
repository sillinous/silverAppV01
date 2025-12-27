import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { Navbar, Nav, Container } from 'react-bootstrap';
import Dashboard from './components/Dashboard';
import Discovery from './components/Discovery';
import Logistics from './components/Logistics';
import Verification from './components/Verification';
import Valuation from './components/Valuation';
import MultiDiscovery from './components/MultiDiscovery'; // Import the new component
import './App.css';

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
                <Nav.Link as={Link} to="/multi-discover">Multi-Discovery</Nav.Link> {/* New Nav Link */}
                <Nav.Link as={Link} to="/logistics">Logistics</Nav.Link>
                <Nav.Link as={Link} to="/verification">Verification</Nav.Link>
                <Nav.Link as={Link} to="/valuation">Valuation</Nav.Link>
              </Nav>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/discover" element={<Discovery />} />
            <Route path="/multi-discover" element={<MultiDiscovery />} /> {/* New Route */}
            <Route path="/logistics" element={<Logistics />} />
            <Route path="/verification" element={<Verification />} />
            <Route path="/valuation" element={<Valuation />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;