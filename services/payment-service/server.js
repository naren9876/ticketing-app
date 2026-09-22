// Payment Service - Payment Processing
const express = require('express');
const { Pool } = require('pg');
const axios = require('axios');

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

const BOOKING_SERVICE_URL = process.env.BOOKING_SERVICE_URL || 'http://localhost:3003';
const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY || 'sk_test_dummy';

// Initialize database
const initDB = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS payments (
        id SERIAL PRIMARY KEY,
        booking_id INT NOT NULL,
        user_id INT NOT NULL,
        amount DECIMAL(10,2),
        currency VARCHAR(3) DEFAULT 'USD',
        status VARCHAR(50) DEFAULT 'pending',
        payment_method VARCHAR(50),
        stripe_payment_id VARCHAR(255),
        transaction_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS refunds (
        id SERIAL PRIMARY KEY,
        payment_id INT REFERENCES payments(id),
        amount DECIMAL(10,2),
        reason VARCHAR(255),
        status VARCHAR(50) DEFAULT 'pending',
        stripe_refund_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('Payment database initialized');
  } catch (err) {
    console.error('DB init error:', err);
  }
};

// Process payment
app.post('/api/payments', async (req, res) => {
  try {
    const { bookingId, userId, amount, paymentMethod, stripeToken } = req.body;

    if (!bookingId || !userId || !amount) {
      return res.status(400).json({ error: 'Invalid payment data' });
    }

    // In production, integrate with Stripe API
    // For demo, simulate payment processing
    const stripePaymentId = `pi_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const transactionId = `txn_${Date.now()}`;

    const result = await pool.query(
      'INSERT INTO payments (booking_id, user_id, amount, payment_method, stripe_payment_id, transaction_id, status) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *',
      [bookingId, userId, amount, paymentMethod || 'card', stripePaymentId, transactionId, 'completed']
    );

    const payment = result.rows[0];

    // Confirm booking after successful payment
    try {
      await axios.put(`${BOOKING_SERVICE_URL}/api/bookings/${bookingId}/confirm`, {
        paymentId: payment.id
      });
    } catch (err) {
      console.log('Booking confirmation error:', err.message);
    }

    res.status(201).json({
      id: payment.id,
      bookingId: payment.booking_id,
      amount: payment.amount,
      status: payment.status,
      transactionId: payment.transaction_id
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get payment
app.get('/api/payments/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      'SELECT id, booking_id, user_id, amount, currency, status, payment_method, transaction_id, created_at FROM payments WHERE id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Refund payment
app.post('/api/payments/:id/refund', async (req, res) => {
  const client = await pool.connect();
  try {
    const { id } = req.params;
    const { reason } = req.body;

    await client.query('BEGIN');

    const paymentResult = await client.query(
      'SELECT amount, status FROM payments WHERE id = $1',
      [id]
    );

    if (paymentResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({ error: 'Payment not found' });
    }

    const payment = paymentResult.rows[0];

    if (payment.status !== 'completed') {
      await client.query('ROLLBACK');
      return res.status(400).json({ error: 'Only completed payments can be refunded' });
    }

    // Simulate Stripe refund
    const stripeRefundId = `re_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const refundResult = await client.query(
      'INSERT INTO refunds (payment_id, amount, reason, stripe_refund_id, status) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [id, payment.amount, reason || 'Customer request', stripeRefundId, 'completed']
    );

    await client.query(
      'UPDATE payments SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2',
      ['refunded', id]
    );

    await client.query('COMMIT');

    res.json({
      refund: refundResult.rows[0],
      message: 'Refund processed successfully'
    });
  } catch (err) {
    await client.query('ROLLBACK');
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// Get payment history for user
app.get('/api/payments/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const result = await pool.query(
      'SELECT id, booking_id, amount, status, transaction_id, created_at FROM payments WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'Payment Service running' });
});

const PORT = process.env.PORT || 3004;

initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Payment Service listening on port ${PORT}`);
  });
});
