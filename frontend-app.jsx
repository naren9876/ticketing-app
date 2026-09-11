import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

// Main App Component
function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    token: null,
    user: null
  });
  const [movies, setMovies] = useState([]);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [showtimes, setShowtimes] = useState([]);
  const [booking, setBooking] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuth(prev => ({ ...prev, isAuthenticated: true, token }));
      verifyToken(token);
    }
  }, []);

  useEffect(() => {
    if (currentPage === 'home' || currentPage === 'movies') {
      fetchMovies();
    }
  }, [currentPage]);

  const verifyToken = async (token) => {
    try {
      const response = await axios.post(`${API_URL}/api/users/verify-token`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAuth(prev => ({ ...prev, isAuthenticated: true }));
    } catch (err) {
      localStorage.removeItem('authToken');
      setAuth(prev => ({ ...prev, isAuthenticated: false, token: null }));
    }
  };

  const fetchMovies = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/movies`);
      setMovies(response.data);
    } catch (err) {
      console.error('Error fetching movies:', err);
    }
  };

  const fetchShowtimes = async (movieId) => {
    try {
      const response = await axios.get(`${API_URL}/api/showtimes?movieId=${movieId}`);
      setShowtimes(response.data);
    } catch (err) {
      console.error('Error fetching showtimes:', err);
    }
  };

  const handleMovieSelect = (movie) => {
    setSelectedMovie(movie);
    fetchShowtimes(movie.id);
    setCurrentPage('showtimes');
  };

  return (
    <div className="app">
      <Header auth={auth} setAuth={setAuth} currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="app-content">
        {currentPage === 'home' && <HomePage movies={movies} onMovieSelect={handleMovieSelect} />}
        {currentPage === 'movies' && <MoviesPage movies={movies} onMovieSelect={handleMovieSelect} />}
        {currentPage === 'showtimes' && selectedMovie && (
          <ShowtimesPage movie={selectedMovie} showtimes={showtimes} setCurrentPage={setCurrentPage} setBooking={setBooking} />
        )}
        {currentPage === 'booking' && booking && (
          <BookingPage booking={booking} auth={auth} setCurrentPage={setCurrentPage} />
        )}
        {currentPage === 'profile' && auth.isAuthenticated && <ProfilePage auth={auth} />}
        {currentPage === 'login' && <LoginPage auth={auth} setAuth={setAuth} setCurrentPage={setCurrentPage} />}
        {currentPage === 'register' && <RegisterPage setAuth={setAuth} setCurrentPage={setCurrentPage} />}
      </main>
      <Footer />
    </div>
  );
}

// Header Component
function Header({ auth, setAuth, currentPage, setCurrentPage }) {
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    setAuth({ isAuthenticated: false, token: null, user: null });
    setCurrentPage('home');
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo" onClick={() => setCurrentPage('home')}>
          🎬 MovieTickets
        </div>
        <nav className="nav">
          <button onClick={() => setCurrentPage('movies')} className={currentPage === 'movies' ? 'active' : ''}>
            Movies
          </button>
          {auth.isAuthenticated && (
            <>
              <button onClick={() => setCurrentPage('profile')} className={currentPage === 'profile' ? 'active' : ''}>
                My Bookings
              </button>
              <button onClick={handleLogout} className="logout-btn">Logout</button>
            </>
          )}
          {!auth.isAuthenticated && (
            <>
              <button onClick={() => setCurrentPage('login')} className={currentPage === 'login' ? 'active' : ''}>
                Login
              </button>
              <button onClick={() => setCurrentPage('register')} className="register-btn">Register</button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

// Home Page
function HomePage({ movies, onMovieSelect }) {
  return (
    <section className="home-page">
      <div className="hero">
        <h1>Book Your Movie Tickets</h1>
        <p>Discover and book your favorite movies</p>
      </div>
      <div className="featured-movies">
        <h2>Featured Movies</h2>
        <div className="movies-grid">
          {movies.slice(0, 6).map(movie => (
            <MovieCard key={movie.id} movie={movie} onSelect={onMovieSelect} />
          ))}
        </div>
      </div>
    </section>
  );
}

// Movies Page
function MoviesPage({ movies, onMovieSelect }) {
  const [filteredMovies, setFilteredMovies] = useState(movies);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const filtered = movies.filter(movie =>
      movie.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredMovies(filtered);
  }, [searchTerm, movies]);

  return (
    <section className="movies-page">
      <div className="search-container">
        <input
          type="text"
          placeholder="Search movies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>
      <div className="movies-grid">
        {filteredMovies.map(movie => (
          <MovieCard key={movie.id} movie={movie} onSelect={onMovieSelect} />
        ))}
      </div>
    </section>
  );
}

// Movie Card Component
function MovieCard({ movie, onSelect }) {
  return (
    <div className="movie-card" onClick={() => onSelect(movie)}>
      <div className="movie-poster">
        <img src={movie.poster_url || 'https://via.placeholder.com/250x350'} alt={movie.title} />
      </div>
      <div className="movie-info">
        <h3>{movie.title}</h3>
        <p className="genre">{movie.genre}</p>
        <p className="rating">⭐ {movie.rating}/10</p>
        <button className="book-btn">Book Tickets</button>
      </div>
    </div>
  );
}

// Showtimes Page
function ShowtimesPage({ movie, showtimes, setCurrentPage, setBooking }) {
  const [selectedShowtime, setSelectedShowtime] = useState(null);

  const handleShowtimeSelect = (showtime) => {
    setSelectedShowtime(showtime);
    setBooking({ movie, showtime, selectedSeats: [] });
    setCurrentPage('booking');
  };

  return (
    <section className="showtimes-page">
      <button onClick={() => setCurrentPage('movies')} className="back-btn">← Back</button>
      <h1>{movie.title}</h1>
      <p className="movie-description">{movie.description}</p>
      <div className="showtimes-container">
        <h2>Select Showtime</h2>
        <div className="showtimes-grid">
          {showtimes.map(showtime => (
            <div key={showtime.id} className="showtime-card">
              <div className="theater-name">{showtime.theater_name}</div>
              <div className="showtime-time">
                {new Date(showtime.start_time).toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
              <div className="showtime-info">
                <span>${showtime.price}</span>
                <span>{showtime.available_seats} seats</span>
              </div>
              <button
                className="select-btn"
                onClick={() => handleShowtimeSelect(showtime)}
                disabled={showtime.available_seats === 0}
              >
                {showtime.available_seats > 0 ? 'Select' : 'Sold Out'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Booking Page
function BookingPage({ booking, auth, setCurrentPage }) {
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSeatSelect = (seatId) => {
    setSelectedSeats(prev => 
      prev.includes(seatId) ? prev.filter(s => s !== seatId) : [...prev, seatId]
    );
  };

  const handleBooking = async () => {
    if (!auth.isAuthenticated) {
      setCurrentPage('login');
      return;
    }

    if (selectedSeats.length === 0) {
      alert('Please select at least one seat');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API_URL}/api/bookings`,
        {
          userId: auth.user?.id,
          showtimeId: booking.showtime.id,
          seats: selectedSeats
        },
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );

      // Process payment
      const paymentResponse = await axios.post(
        `${API_URL}/api/payments`,
        {
          bookingId: response.data.id,
          userId: auth.user?.id,
          amount: booking.showtime.price * selectedSeats.length
        },
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );

      alert(`Booking confirmed! Reference: ${response.data.bookingReference}`);
      setCurrentPage('profile');
    } catch (err) {
      alert('Booking failed: ' + err.response?.data?.error);
    } finally {
      setLoading(false);
    }
  };

  const totalPrice = booking.showtime.price * selectedSeats.length;

  return (
    <section className="booking-page">
      <button onClick={() => setCurrentPage('showtimes')} className="back-btn">← Back</button>
      <div className="booking-container">
        <div className="seats-selection">
          <h2>Select Seats</h2>
          <div className="seat-grid">
            {Array.from({ length: 80 }, (_, i) => {
              const row = String.fromCharCode(65 + Math.floor(i / 10));
              const col = (i % 10) + 1;
              const seatId = `${row}${col}`;
              const isSelected = selectedSeats.includes(seatId);

              return (
                <button
                  key={seatId}
                  className={`seat ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSeatSelect(seatId)}
                >
                  {col}
                </button>
              );
            })}
          </div>
        </div>
        <div className="booking-summary">
          <h3>Booking Summary</h3>
          <div className="summary-item">
            <span>Movie:</span>
            <span>{booking.movie.title}</span>
          </div>
          <div className="summary-item">
            <span>Theater:</span>
            <span>{booking.showtime.theater_name}</span>
          </div>
          <div className="summary-item">
            <span>Seats:</span>
            <span>{selectedSeats.join(', ') || 'None selected'}</span>
          </div>
          <div className="summary-item">
            <span>Price per seat:</span>
            <span>${booking.showtime.price}</span>
          </div>
          <div className="summary-total">
            <span>Total:</span>
            <span>${totalPrice.toFixed(2)}</span>
          </div>
          <button
            onClick={handleBooking}
            disabled={selectedSeats.length === 0 || loading}
            className="confirm-btn"
          >
            {loading ? 'Processing...' : 'Proceed to Payment'}
          </button>
        </div>
      </div>
    </section>
  );
}

// Login Page
function LoginPage({ auth, setAuth, setCurrentPage }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/users/login`, { email, password });
      localStorage.setItem('authToken', response.data.token);
      setAuth({
        isAuthenticated: true,
        token: response.data.token,
        user: response.data.user
      });
      setCurrentPage('home');
    } catch (err) {
      alert('Login failed: ' + err.response?.data?.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-container">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>{loading ? 'Logging in...' : 'Login'}</button>
        </form>
        <p>
          Don't have an account? 
          <button onClick={() => setCurrentPage('register')} className="link-btn">Register</button>
        </p>
      </div>
    </section>
  );
}

// Register Page
function RegisterPage({ setAuth, setCurrentPage }) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: ''
  });
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/users/register`, formData);
      localStorage.setItem('authToken', response.data.token);
      setAuth({
        isAuthenticated: true,
        token: response.data.token,
        user: response.data.user
      });
      setCurrentPage('home');
    } catch (err) {
      alert('Registration failed: ' + err.response?.data?.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-container">
        <h2>Register</h2>
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          <input
            type="text"
            placeholder="First Name"
            value={formData.firstName}
            onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
          />
          <input
            type="text"
            placeholder="Last Name"
            value={formData.lastName}
            onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
          <button type="submit" disabled={loading}>{loading ? 'Registering...' : 'Register'}</button>
        </form>
        <p>
          Already have an account? 
          <button onClick={() => setCurrentPage('login')} className="link-btn">Login</button>
        </p>
      </div>
    </section>
  );
}

// Profile Page (My Bookings)
function ProfilePage({ auth }) {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBookings();
  }, [auth.user]);

  const fetchBookings = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/bookings/user/${auth.user?.id}`,
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );
      setBookings(response.data);
    } catch (err) {
      console.error('Error fetching bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="profile-page">
      <h1>My Bookings</h1>
      {loading ? (
        <p>Loading...</p>
      ) : bookings.length === 0 ? (
        <p>No bookings yet</p>
      ) : (
        <div className="bookings-list">
          {bookings.map(booking => (
            <div key={booking.id} className="booking-item">
              <h3>Booking #{booking.booking_reference}</h3>
              <p>Status: <strong>{booking.status}</strong></p>
              <p>Seats: {JSON.parse(booking.seats).join(', ')}</p>
              <p>Total: ${booking.total_price}</p>
              <p>Booked: {new Date(booking.created_at).toLocaleDateString()}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

// Footer Component
function Footer() {
  return (
    <footer className="footer">
      <p>&copy; 2024 MovieTickets. All rights reserved.</p>
      <div className="footer-links">
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
        <a href="#privacy">Privacy</a>
      </div>
    </footer>
  );
}

export default App;
