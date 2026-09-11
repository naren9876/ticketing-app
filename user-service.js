// User Service - Authentication & User Management
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

// Database connection
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  host: process.env.DB_HOST || 'postgres',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'ticketing_db'
});

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';

// Initialize database
const initDB = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        phone VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('Database initialized');
  } catch (err) {
    console.error('DB init error:', err);
  }
};

// Register user
app.post('/api/users/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName } = req.body;
    
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    
    const result = await pool.query(
      'INSERT INTO users (email, password, first_name, last_name) VALUES ($1, $2, $3, $4) RETURNING id, email, first_name, last_name',
      [email, hashedPassword, firstName, lastName]
    );

    const user = result.rows[0];
    const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '24h' });

    res.status(201).json({
      user,
      token
    });
  } catch (err) {
    if (err.code === '23505') {
      return res.status(400).json({ error: 'Email already exists' });
    }
    res.status(500).json({ error: err.message });
  }
});

// Login user
app.post('/api/users/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password required' });
    }

    const result = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = result.rows[0];
    const validPassword = await bcrypt.compare(password, user.password);

    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '24h' });

    res.json({
      user: {
        id: user.id,
        email: user.email,
        firstName: user.first_name,
        lastName: user.last_name
      },
      token
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get user profile
app.get('/api/users/profile', authenticateToken, async (req, res) => {
  try {
    const result = await pool.query('SELECT id, email, first_name, last_name, phone, created_at FROM users WHERE id = $1', [req.userId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update user profile
app.put('/api/users/profile', authenticateToken, async (req, res) => {
  try {
    const { firstName, lastName, phone } = req.body;
    
    const result = await pool.query(
      'UPDATE users SET first_name = $1, last_name = $2, phone = $3, updated_at = CURRENT_TIMESTAMP WHERE id = $4 RETURNING id, email, first_name, last_name, phone',
      [firstName, lastName, phone, req.userId]
    );

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Verify token
app.post('/api/users/verify-token', authenticateToken, (req, res) => {
  res.json({ valid: true, userId: req.userId });
});

// Middleware to authenticate token
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.userId = decoded.userId;
    next();
  });
}

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'User Service running' });
});

const PORT = process.env.PORT || 3001;

initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`User Service listening on port ${PORT}`);
  });
});
