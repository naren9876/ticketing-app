// Booking Service - Ticket Booking Management
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

const PAYMENT_SERVICE_URL = process.env.PAYMENT_SERVICE_URL || 'http://localhost:3004';
const NOTIFICATION_SERVICE_URL = process.env.NOTIFICATION_SERVICE_URL || 'http://localhost:3005';

// Initialize database
const initDB = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        showtime_id INT NOT NULL,
        seats JSONB,
        total_price DECIMAL(10,2),
        status VARCHAR(50) DEFAULT 'pending',
        booking_reference VARCHAR(50) UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS seats (
        id SERIAL PRIMARY KEY,
        showtime_id INT NOT NULL,
        seat_number VARCHAR(10),
        is_available BOOLEAN DEFAULT TRUE,
        booked_by INT,
        booked_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('Booking database initialized');
  } catch (err) {
    console.error('DB init error:', err);
  }
};

// Create booking
app.post('/api/bookings', async (req, res) => {
  const client = await pool.connect();
  try {
    const { userId, showtimeId, seats } = req.body;

    if (!userId || !showtimeId || !seats || seats.length === 0) {
      return res.status(400).json({ error: 'Invalid booking data' });
    }

    await client.query('BEGIN');

    // Check seat availability
    const seatCheck = await client.query(
      'SELECT COUNT(*) as count FROM seats WHERE showtime_id = $1 AND seat_number = ANY($2) AND is_available = FALSE',
      [showtimeId, seats]
    );

    if (parseInt(seatCheck.rows[0].count) > 0) {
      await client.query('ROLLBACK');
      return res.status(400).json({ error: 'Some seats are no longer available' });
    }

    // Reserve seats
    await client.query(
      'UPDATE seats SET is_available = FALSE, booked_by = $1, booked_at = CURRENT_TIMESTAMP WHERE showtime_id = $2 AND seat_number = ANY($3)',
      [userId, showtimeId, seats]
    );

    // Calculate total price
    const priceResult = await client.query(
      'SELECT price FROM showtimes WHERE id = $1',
      [showtimeId]
    );

    const price = parseFloat(priceResult.rows[0].price);
    const totalPrice = price * seats.length;
    const bookingReference = `BK${Date.now()}${Math.random().toString(36).substr(2, 9)}`;

    // Create booking
    const bookingResult = await client.query(
      'INSERT INTO bookings (user_id, showtime_id, seats, total_price, booking_reference, status) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *',
      [userId, showtimeId, JSON.stringify(seats), totalPrice, bookingReference, 'pending']
    );

    await client.query('COMMIT');

    const booking = bookingResult.rows[0];

    res.status(201).json({
      id: booking.id,
      bookingReference: booking.booking_reference,
      seats: booking.seats,
      totalPrice: booking.total_price,
      status: booking.status
    });
  } catch (err) {
    await client.query('ROLLBACK');
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// Get booking
app.get('/api/bookings/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      'SELECT id, user_id, showtime_id, seats, total_price, status, booking_reference, created_at FROM bookings WHERE id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get user bookings
app.get('/api/bookings/user/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const result = await pool.query(
      'SELECT id, user_id, showtime_id, seats, total_price, status, booking_reference, created_at FROM bookings WHERE user_id = $1 ORDER BY created_at DESC',
      [userId]
    );

    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Cancel booking
app.put('/api/bookings/:id/cancel', async (req, res) => {
  const client = await pool.connect();
  try {
    const { id } = req.params;

    await client.query('BEGIN');

    const bookingResult = await client.query(
      'SELECT seats, total_price, status FROM bookings WHERE id = $1',
      [id]
    );

    if (bookingResult.rows.length === 0) {
      await client.query('ROLLBACK');
      return res.status(404).json({ error: 'Booking not found' });
    }

    const booking = bookingResult.rows[0];

    if (booking.status === 'cancelled') {
      await client.query('ROLLBACK');
      return res.status(400).json({ error: 'Booking already cancelled' });
    }

    // Release seats
    const seats = JSON.parse(booking.seats);
    await client.query(
      'UPDATE seats SET is_available = TRUE, booked_by = NULL, booked_at = NULL WHERE seat_number = ANY($1)',
      [seats]
    );

    // Update booking status
    await client.query(
      'UPDATE bookings SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2',
      ['cancelled', id]
    );

    await client.query('COMMIT');

    res.json({ message: 'Booking cancelled successfully' });
  } catch (err) {
    await client.query('ROLLBACK');
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

// Confirm booking (after payment)
app.put('/api/bookings/:id/confirm', async (req, res) => {
  try {
    const { id } = req.params;
    const { paymentId } = req.body;

    const result = await pool.query(
      'UPDATE bookings SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *',
      ['confirmed', id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Booking not found' });
    }

    // Send notification
    try {
      await axios.post(`${NOTIFICATION_SERVICE_URL}/api/notifications/email`, {
        bookingId: id,
        type: 'booking_confirmation'
      });
    } catch (notifErr) {
      console.log('Notification service error:', notifErr.message);
    }

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get available seats for showtime
app.get('/api/showtimes/:showtimeId/seats', async (req, res) => {
  try {
    const { showtimeId } = req.params;

    const result = await pool.query(
      'SELECT seat_number, is_available FROM seats WHERE showtime_id = $1 ORDER BY seat_number',
      [showtimeId]
    );

    const layout = {};
    result.rows.forEach(seat => {
      layout[seat.seat_number] = seat.is_available;
    });

    res.json(layout);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'Booking Service running' });
});

const PORT = process.env.PORT || 3003;

initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Booking Service listening on port ${PORT}`);
  });
});
