// API Gateway - Request Routing & Authentication
const express = require('express');
const httpProxy = require('express-http-proxy');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Environment variables for service URLs
const USER_SERVICE = process.env.USER_SERVICE_URL || 'http://localhost:3001';
const MOVIE_SERVICE = process.env.MOVIE_SERVICE_URL || 'http://localhost:3002';
const BOOKING_SERVICE = process.env.BOOKING_SERVICE_URL || 'http://localhost:3003';
const PAYMENT_SERVICE = process.env.PAYMENT_SERVICE_URL || 'http://localhost:3004';
const NOTIFICATION_SERVICE = process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:3005';

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

const strictLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10 // strict limit for payment endpoints
});

app.use(limiter);

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }
  next();
});

// Authentication middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  // Skip auth for public endpoints
  if (isPublicEndpoint(req.path)) {
    return next();
  }

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.userId = decoded.userId;
    req.userEmail = decoded.email;
    next();
  });
}

// List of public endpoints
function isPublicEndpoint(path) {
  const publicPaths = [
    '/api/users/register',
    '/api/users/login',
    '/api/movies',
    '/health'
  ];
  return publicPaths.some(p => path.startsWith(p));
}

app.use(authenticateToken);

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'API Gateway running',
    timestamp: new Date().toISOString()
  });
});

// User Service routes
app.use('/api/users', httpProxy(USER_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/users' + (req.url.startsWith('/api/users') ? req.url.substring('/api/users'.length) : req.url);
  },
  userResDecorator: (proxyRes, proxyResData, userReq, userRes) => {
    userRes.header('X-Service', 'user-service');
    return proxyResData;
  }
}));

// Movie Service routes
app.use('/api/movies', httpProxy(MOVIE_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/movies' + (req.url.startsWith('/api/movies') ? req.url.substring('/api/movies'.length) : req.url);
  }
}));

app.use('/api/theaters', httpProxy(MOVIE_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/theaters' + (req.url.startsWith('/api/theaters') ? req.url.substring('/api/theaters'.length) : req.url);
  }
}));

app.use('/api/showtimes', httpProxy(MOVIE_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/showtimes' + (req.url.startsWith('/api/showtimes') ? req.url.substring('/api/showtimes'.length) : req.url);
  }
}));

// Booking Service routes
app.use('/api/bookings', httpProxy(BOOKING_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/bookings' + (req.url.startsWith('/api/bookings') ? req.url.substring('/api/bookings'.length) : req.url);
  }
}));

// Payment Service routes (with strict rate limiting)
app.use('/api/payments', strictLimiter, httpProxy(PAYMENT_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/payments' + (req.url.startsWith('/api/payments') ? req.url.substring('/api/payments'.length) : req.url);
  }
}));

// Notification Service routes
app.use('/api/notifications', httpProxy(NOTIFICATION_SERVICE, {
  proxyReqPathResolver: (req) => {
    return '/api/notifications' + (req.url.startsWith('/api/notifications') ? req.url.substring('/api/notifications'.length) : req.url);
  }
}));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Gateway error:', err);
  res.status(500).json({
    error: 'Gateway error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`API Gateway listening on port ${PORT}`);
  console.log(`User Service: ${USER_SERVICE}`);
  console.log(`Movie Service: ${MOVIE_SERVICE}`);
  console.log(`Booking Service: ${BOOKING_SERVICE}`);
  console.log(`Payment Service: ${PAYMENT_SERVICE}`);
  console.log(`Notification Service: ${NOTIFICATION_SERVICE}`);
});
