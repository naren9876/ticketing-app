// Movie Service - Movie & Theater Management
const express = require('express');
const { Pool } = require('pg');
const redis = require('redis');

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

// Redis cache
const redisClient = redis.createClient({
  host: process.env.REDIS_HOST || 'redis',
  port: process.env.REDIS_PORT || 6379
});

// Initialize database
const initDB = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS movies (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        genre VARCHAR(100),
        duration INT,
        rating DECIMAL(3,1),
        poster_url VARCHAR(500),
        release_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS theaters (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        location VARCHAR(255),
        city VARCHAR(100),
        capacity INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS showtimes (
        id SERIAL PRIMARY KEY,
        movie_id INT REFERENCES movies(id),
        theater_id INT REFERENCES theaters(id),
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP NOT NULL,
        available_seats INT,
        price DECIMAL(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log('Movie database initialized');
  } catch (err) {
    console.error('DB init error:', err);
  }
};

// Get all movies with caching
app.get('/api/movies', async (req, res) => {
  try {
    const cacheKey = 'movies:all';
    
    // Check cache
    const cached = await redisClient.get(cacheKey);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pool.query('SELECT * FROM movies ORDER BY release_date DESC');
    const movies = result.rows;

    // Cache for 1 hour
    await redisClient.setEx(cacheKey, 3600, JSON.stringify(movies));

    res.json(movies);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get movie by ID
app.get('/api/movies/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const cacheKey = `movie:${id}`;

    // Check cache
    const cached = await redisClient.get(cacheKey);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    const result = await pool.query('SELECT * FROM movies WHERE id = $1', [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Movie not found' });
    }

    const movie = result.rows[0];
    
    // Get showtimes for this movie
    const showtimesResult = await pool.query(`
      SELECT st.id, st.start_time, st.end_time, st.available_seats, st.price,
             t.id as theater_id, t.name as theater_name, t.location
      FROM showtimes st
      JOIN theaters t ON st.theater_id = t.id
      WHERE st.movie_id = $1
      ORDER BY st.start_time
    `, [id]);

    movie.showtimes = showtimesResult.rows;

    // Cache for 30 minutes
    await redisClient.setEx(cacheKey, 1800, JSON.stringify(movie));

    res.json(movie);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Search movies
app.get('/api/movies/search', async (req, res) => {
  try {
    const { query, genre, city } = req.query;

    let sql = `
      SELECT DISTINCT m.* FROM movies m
      LEFT JOIN showtimes st ON m.id = st.movie_id
      LEFT JOIN theaters t ON st.theater_id = t.id
      WHERE 1=1
    `;
    const params = [];

    if (query) {
      sql += ` AND (m.title ILIKE $${params.length + 1} OR m.description ILIKE $${params.length + 1})`;
      params.push(`%${query}%`);
    }

    if (genre) {
      sql += ` AND m.genre = $${params.length + 1}`;
      params.push(genre);
    }

    if (city) {
      sql += ` AND t.city = $${params.length + 1}`;
      params.push(city);
    }

    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get all theaters
app.get('/api/theaters', async (req, res) => {
  try {
    const { city } = req.query;
    
    let sql = 'SELECT * FROM theaters';
    const params = [];

    if (city) {
      sql += ' WHERE city = $1';
      params.push(city);
    }

    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get showtimes
app.get('/api/showtimes', async (req, res) => {
  try {
    const { movieId, theaterId, date } = req.query;

    let sql = `
      SELECT st.*, m.title as movie_title, t.name as theater_name
      FROM showtimes st
      JOIN movies m ON st.movie_id = m.id
      JOIN theaters t ON st.theater_id = t.id
      WHERE 1=1
    `;
    const params = [];

    if (movieId) {
      sql += ` AND st.movie_id = $${params.length + 1}`;
      params.push(movieId);
    }

    if (theaterId) {
      sql += ` AND st.theater_id = $${params.length + 1}`;
      params.push(theaterId);
    }

    if (date) {
      sql += ` AND DATE(st.start_time) = $${params.length + 1}`;
      params.push(date);
    }

    sql += ' ORDER BY st.start_time';

    const result = await pool.query(sql, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Add movie (admin)
app.post('/api/movies', async (req, res) => {
  try {
    const { title, description, genre, duration, rating, posterUrl, releaseDate } = req.body;

    const result = await pool.query(
      'INSERT INTO movies (title, description, genre, duration, rating, poster_url, release_date) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *',
      [title, description, genre, duration, rating, posterUrl, releaseDate]
    );

    // Invalidate cache
    await redisClient.del('movies:all');

    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Add showtime (admin)
app.post('/api/showtimes', async (req, res) => {
  try {
    const { movieId, theaterId, startTime, endTime, availableSeats, price } = req.body;

    const result = await pool.query(
      'INSERT INTO showtimes (movie_id, theater_id, start_time, end_time, available_seats, price) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *',
      [movieId, theaterId, startTime, endTime, availableSeats, price]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'Movie Service running' });
});

const PORT = process.env.PORT || 3002;

initDB().then(() => {
  app.listen(PORT, () => {
    console.log(`Movie Service listening on port ${PORT}`);
  });
});
