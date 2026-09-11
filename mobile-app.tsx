import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  Alert,
  FlatList,
  TextInput,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

// Main App Component
export default function App() {
  const [screen, setScreen] = useState('home');
  const [auth, setAuth] = useState({ isAuthenticated: false, token: null, user: null });
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [showtimes, setShowtimes] = useState([]);
  const [booking, setBooking] = useState(null);
  const [selectedSeats, setSelectedSeats] = useState([]);

  useEffect(() => {
    checkAuth();
    if (screen === 'home' || screen === 'movies') {
      fetchMovies();
    }
  }, [screen]);

  const checkAuth = async () => {
    const token = await AsyncStorage.getItem('authToken');
    if (token) {
      setAuth(prev => ({ ...prev, isAuthenticated: true, token }));
    }
  };

  const fetchMovies = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/movies`);
      setMovies(response.data);
    } catch (err) {
      Alert.alert('Error', 'Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  };

  const fetchShowtimes = async (movieId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/showtimes?movieId=${movieId}`);
      setShowtimes(response.data);
    } catch (err) {
      Alert.alert('Error', 'Failed to fetch showtimes');
    } finally {
      setLoading(false);
    }
  };

  const handleMovieSelect = (movie) => {
    setSelectedMovie(movie);
    fetchShowtimes(movie.id);
    setScreen('showtimes');
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('authToken');
    setAuth({ isAuthenticated: false, token: null, user: null });
    setScreen('home');
  };

  return (
    <View style={styles.container}>
      <Header screen={screen} setScreen={setScreen} auth={auth} handleLogout={handleLogout} />
      <View style={styles.content}>
        {screen === 'home' && <HomeScreen movies={movies} loading={loading} onMovieSelect={handleMovieSelect} />}
        {screen === 'movies' && <MoviesScreen movies={movies} loading={loading} onMovieSelect={handleMovieSelect} />}
        {screen === 'showtimes' && selectedMovie && (
          <ShowtimesScreen
            movie={selectedMovie}
            showtimes={showtimes}
            loading={loading}
            setScreen={setScreen}
            setBooking={setBooking}
          />
        )}
        {screen === 'booking' && booking && (
          <BookingScreen
            booking={booking}
            selectedSeats={selectedSeats}
            setSelectedSeats={setSelectedSeats}
            setScreen={setScreen}
            auth={auth}
          />
        )}
        {screen === 'login' && <LoginScreen auth={auth} setAuth={setAuth} setScreen={setScreen} />}
        {screen === 'register' && <RegisterScreen setAuth={setAuth} setScreen={setScreen} />}
        {screen === 'profile' && auth.isAuthenticated && <ProfileScreen auth={auth} />}
      </View>
    </View>
  );
}

// Header Component
function Header({ screen, setScreen, auth, handleLogout }) {
  return (
    <View style={styles.header}>
      <Text style={styles.logo}>🎬 MovieTickets</Text>
      <View style={styles.headerNav}>
        {auth.isAuthenticated ? (
          <>
            <TouchableOpacity onPress={() => setScreen('profile')}>
              <Text style={styles.navButton}>Profile</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={handleLogout}>
              <Text style={[styles.navButton, styles.logoutBtn]}>Logout</Text>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <TouchableOpacity onPress={() => setScreen('login')}>
              <Text style={styles.navButton}>Login</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setScreen('register')}>
              <Text style={[styles.navButton, styles.registerBtn]}>Register</Text>
            </TouchableOpacity>
          </>
        )}
      </View>
    </View>
  );
}

// Home Screen
function HomeScreen({ movies, loading, onMovieSelect }) {
  return (
    <ScrollView style={styles.screen}>
      <View style={styles.hero}>
        <Text style={styles.heroTitle}>Book Your Movie</Text>
        <Text style={styles.heroSubtitle}>Discover great movies and reserve your seats</Text>
      </View>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Featured Movies</Text>
        {loading ? (
          <ActivityIndicator size="large" color="#667eea" style={styles.loader} />
        ) : (
          <FlatList
            data={movies.slice(0, 6)}
            keyExtractor={(item) => item.id.toString()}
            renderItem={({ item }) => <MovieItem movie={item} onPress={() => onMovieSelect(item)} />}
            scrollEnabled={false}
          />
        )}
      </View>
    </ScrollView>
  );
}

// Movies Screen
function MoviesScreen({ movies, loading, onMovieSelect }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filtered, setFiltered] = useState(movies);

  useEffect(() => {
    const result = movies.filter(m => m.title.toLowerCase().includes(searchTerm.toLowerCase()));
    setFiltered(result);
  }, [searchTerm, movies]);

  return (
    <View style={styles.screen}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search movies..."
        placeholderTextColor="#666"
        value={searchTerm}
        onChangeText={setSearchTerm}
      />
      {loading ? (
        <ActivityIndicator size="large" color="#667eea" style={styles.loader} />
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => <MovieItem movie={item} onPress={() => onMovieSelect(item)} />}
        />
      )}
    </View>
  );
}

// Movie Item Component
function MovieItem({ movie, onPress }) {
  return (
    <TouchableOpacity style={styles.movieCard} onPress={onPress}>
      <Image
        source={{ uri: movie.poster_url || 'https://via.placeholder.com/100x150' }}
        style={styles.moviePoster}
      />
      <View style={styles.movieInfo}>
        <Text style={styles.movieTitle} numberOfLines={2}>{movie.title}</Text>
        <Text style={styles.movieGenre}>{movie.genre}</Text>
        <Text style={styles.movieRating}>⭐ {movie.rating}/10</Text>
        <TouchableOpacity style={styles.bookBtn} onPress={onPress}>
          <Text style={styles.bookBtnText}>Book Tickets</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

// Showtimes Screen
function ShowtimesScreen({ movie, showtimes, loading, setScreen, setBooking }) {
  const handleShowtimeSelect = (showtime) => {
    setBooking({ movie, showtime, selectedSeats: [] });
    setScreen('booking');
  };

  return (
    <ScrollView style={styles.screen}>
      <TouchableOpacity onPress={() => setScreen('movies')} style={styles.backButton}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.movieTitle}>{movie.title}</Text>
      <Text style={styles.movieDescription}>{movie.description}</Text>
      <Text style={styles.sectionTitle}>Select Showtime</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#667eea" style={styles.loader} />
      ) : (
        <FlatList
          data={showtimes}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <ShowtimeCard showtime={item} onPress={() => handleShowtimeSelect(item)} />
          )}
          scrollEnabled={false}
        />
      )}
    </ScrollView>
  );
}

// Showtime Card Component
function ShowtimeCard({ showtime, onPress }) {
  const time = new Date(showtime.start_time).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <TouchableOpacity style={styles.showtimeCard} onPress={onPress}>
      <View>
        <Text style={styles.theaterName}>{showtime.theater_name}</Text>
        <Text style={styles.showtimeTime}>{time}</Text>
        <View style={styles.showtimeInfo}>
          <Text style={styles.price}>${showtime.price}</Text>
          <Text style={styles.seats}>{showtime.available_seats} seats</Text>
        </View>
      </View>
      <TouchableOpacity style={styles.selectBtn}>
        <Text style={styles.selectBtnText}>Select</Text>
      </TouchableOpacity>
    </TouchableOpacity>
  );
}

// Booking Screen
function BookingScreen({ booking, selectedSeats, setSelectedSeats, setScreen, auth }) {
  const handleSeatSelect = (seatId) => {
    setSelectedSeats(prev =>
      prev.includes(seatId) ? prev.filter(s => s !== seatId) : [...prev, seatId]
    );
  };

  const handleConfirmBooking = async () => {
    if (!auth.isAuthenticated) {
      setScreen('login');
      return;
    }

    if (selectedSeats.length === 0) {
      Alert.alert('Error', 'Please select at least one seat');
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/api/bookings`,
        {
          userId: auth.user?.id,
          showtimeId: booking.showtime.id,
          seats: selectedSeats,
        },
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );

      await axios.post(
        `${API_URL}/api/payments`,
        {
          bookingId: response.data.id,
          userId: auth.user?.id,
          amount: booking.showtime.price * selectedSeats.length,
        },
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );

      Alert.alert('Success', `Booking confirmed! Ref: ${response.data.bookingReference}`);
      setScreen('profile');
    } catch (err) {
      Alert.alert('Error', 'Booking failed. Please try again.');
    }
  };

  const totalPrice = booking.showtime.price * selectedSeats.length;
  const seats = Array.from({ length: 80 }, (_, i) => {
    const row = String.fromCharCode(65 + Math.floor(i / 10));
    const col = (i % 10) + 1;
    return `${row}${col}`;
  });

  return (
    <ScrollView style={styles.screen}>
      <TouchableOpacity onPress={() => setScreen('showtimes')} style={styles.backButton}>
        <Text style={styles.backButtonText}>← Back</Text>
      </TouchableOpacity>
      <Text style={styles.bookingTitle}>Select Seats</Text>
      <View style={styles.seatGrid}>
        {seats.map(seat => (
          <TouchableOpacity
            key={seat}
            style={[styles.seat, selectedSeats.includes(seat) && styles.seatSelected]}
            onPress={() => handleSeatSelect(seat)}
          >
            <Text style={styles.seatText}>{seat}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={styles.summary}>
        <Text style={styles.summaryTitle}>Booking Summary</Text>
        <View style={styles.summaryItem}>
          <Text>Movie:</Text>
          <Text>{booking.movie.title}</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text>Theater:</Text>
          <Text>{booking.showtime.theater_name}</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text>Seats:</Text>
          <Text>{selectedSeats.join(', ') || 'None'}</Text>
        </View>
        <View style={styles.summaryTotal}>
          <Text style={styles.summaryTotalLabel}>Total:</Text>
          <Text style={styles.summaryTotalPrice}>${totalPrice.toFixed(2)}</Text>
        </View>
        <TouchableOpacity
          style={[styles.confirmBtn, selectedSeats.length === 0 && styles.confirmBtnDisabled]}
          onPress={handleConfirmBooking}
          disabled={selectedSeats.length === 0}
        >
          <Text style={styles.confirmBtnText}>Confirm Booking</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

// Login Screen
function LoginScreen({ auth, setAuth, setScreen }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/users/login`, { email, password });
      await AsyncStorage.setItem('authToken', response.data.token);
      setAuth({
        isAuthenticated: true,
        token: response.data.token,
        user: response.data.user,
      });
      setScreen('home');
    } catch (err) {
      Alert.alert('Error', 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.screen}>
      <View style={styles.authContainer}>
        <Text style={styles.authTitle}>Login</Text>
        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#666"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#666"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        <TouchableOpacity
          style={styles.submitBtn}
          onPress={handleLogin}
          disabled={loading}
        >
          <Text style={styles.submitBtnText}>{loading ? 'Logging in...' : 'Login'}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setScreen('register')}>
          <Text style={styles.linkText}>Don't have an account? Register</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

// Register Screen
function RegisterScreen({ setAuth, setScreen }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!email || !password || !firstName || !lastName) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/users/register`, {
        email,
        password,
        firstName,
        lastName,
      });
      await AsyncStorage.setItem('authToken', response.data.token);
      setAuth({
        isAuthenticated: true,
        token: response.data.token,
        user: response.data.user,
      });
      setScreen('home');
    } catch (err) {
      Alert.alert('Error', 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.screen}>
      <View style={styles.authContainer}>
        <Text style={styles.authTitle}>Register</Text>
        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor="#666"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
        />
        <TextInput
          style={styles.input}
          placeholder="First Name"
          placeholderTextColor="#666"
          value={firstName}
          onChangeText={setFirstName}
        />
        <TextInput
          style={styles.input}
          placeholder="Last Name"
          placeholderTextColor="#666"
          value={lastName}
          onChangeText={setLastName}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor="#666"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
        />
        <TouchableOpacity
          style={styles.submitBtn}
          onPress={handleRegister}
          disabled={loading}
        >
          <Text style={styles.submitBtnText}>{loading ? 'Registering...' : 'Register'}</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setScreen('login')}>
          <Text style={styles.linkText}>Already have an account? Login</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

// Profile Screen
function ProfileScreen({ auth }) {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/api/bookings/user/${auth.user?.id}`,
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );
      setBookings(response.data);
    } catch (err) {
      Alert.alert('Error', 'Failed to fetch bookings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.screen}>
      <Text style={styles.profileTitle}>My Bookings</Text>
      {loading ? (
        <ActivityIndicator size="large" color="#667eea" style={styles.loader} />
      ) : bookings.length === 0 ? (
        <Text style={styles.noBookings}>No bookings yet</Text>
      ) : (
        <FlatList
          data={bookings}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => <BookingItem booking={item} />}
          scrollEnabled={false}
        />
      )}
    </ScrollView>
  );
}

// Booking Item Component
function BookingItem({ booking }) {
  return (
    <View style={styles.bookingItem}>
      <Text style={styles.bookingRef}>#{booking.booking_reference}</Text>
      <View style={styles.bookingDetail}>
        <Text style={styles.bookingLabel}>Status:</Text>
        <Text style={styles.bookingValue}>{booking.status}</Text>
      </View>
      <View style={styles.bookingDetail}>
        <Text style={styles.bookingLabel}>Seats:</Text>
        <Text style={styles.bookingValue}>{JSON.parse(booking.seats).join(', ')}</Text>
      </View>
      <View style={styles.bookingDetail}>
        <Text style={styles.bookingLabel}>Total:</Text>
        <Text style={styles.bookingValue}>${booking.total_price}</Text>
      </View>
    </View>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f0f',
  },
  header: {
    backgroundColor: '#667eea',
    padding: 16,
    paddingTop: 40,
  },
  logo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 12,
  },
  headerNav: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  navButton: {
    color: 'white',
    fontSize: 14,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  logoutBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  registerBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  content: {
    flex: 1,
  },
  screen: {
    flex: 1,
    backgroundColor: '#0f0f0f',
  },
  hero: {
    backgroundColor: '#667eea',
    padding: 30,
    borderRadius: 10,
    marginBottom: 20,
    marginHorizontal: 16,
  },
  heroTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  heroSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  section: {
    paddingHorizontal: 16,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 12,
  },
  loader: {
    marginVertical: 20,
  },
  movieCard: {
    flexDirection: 'row',
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    marginBottom: 12,
    overflow: 'hidden',
  },
  moviePoster: {
    width: 100,
    height: 150,
  },
  movieInfo: {
    flex: 1,
    padding: 12,
    justifyContent: 'space-between',
  },
  movieTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  movieGenre: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  movieRating: {
    fontSize: 12,
    color: '#ffd700',
    marginBottom: 8,
  },
  bookBtn: {
    backgroundColor: '#667eea',
    padding: 8,
    borderRadius: 5,
    alignItems: 'center',
  },
  bookBtnText: {
    color: 'white',
    fontWeight: 'bold',
  },
  searchInput: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 12,
    color: 'white',
    marginHorizontal: 16,
    marginVertical: 12,
    borderWidth: 2,
    borderColor: '#333',
  },
  backButton: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  backButtonText: {
    color: '#667eea',
    fontSize: 14,
    fontWeight: 'bold',
  },
  movieDescription: {
    color: '#ccc',
    paddingHorizontal: 16,
    marginBottom: 16,
    lineHeight: 20,
  },
  showtimeCard: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
    marginHorizontal: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#333',
  },
  theaterName: {
    color: '#667eea',
    fontWeight: 'bold',
    marginBottom: 4,
  },
  showtimeTime: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  showtimeInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  price: {
    color: 'white',
    fontWeight: 'bold',
  },
  seats: {
    color: '#999',
    fontSize: 12,
  },
  selectBtn: {
    backgroundColor: '#667eea',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 5,
  },
  selectBtnText: {
    color: 'white',
    fontWeight: 'bold',
  },
  bookingTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  seatGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    marginBottom: 20,
    justifyContent: 'center',
  },
  seat: {
    width: '10%',
    aspectRatio: 1,
    backgroundColor: '#333',
    borderRadius: 5,
    margin: 4,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#555',
  },
  seatSelected: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  seatText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 10,
  },
  summary: {
    backgroundColor: '#1a1a1a',
    marginHorizontal: 16,
    borderRadius: 8,
    padding: 16,
    marginBottom: 20,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 12,
  },
  summaryItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
    color: '#ccc',
  },
  summaryTotal: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    marginVertical: 8,
  },
  summaryTotalLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
  summaryTotalPrice: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
  },
  confirmBtn: {
    backgroundColor: '#667eea',
    paddingVertical: 12,
    borderRadius: 5,
    marginTop: 12,
  },
  confirmBtnDisabled: {
    opacity: 0.5,
  },
  confirmBtnText: {
    color: 'white',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  authContainer: {
    marginHorizontal: 16,
    marginVertical: 40,
    backgroundColor: '#1a1a1a',
    borderRadius: 10,
    padding: 20,
  },
  authTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#0f0f0f',
    borderWidth: 2,
    borderColor: '#333',
    borderRadius: 5,
    paddingVertical: 10,
    paddingHorizontal: 12,
    color: 'white',
    marginBottom: 12,
  },
  submitBtn: {
    backgroundColor: '#667eea',
    paddingVertical: 12,
    borderRadius: 5,
    marginTop: 12,
  },
  submitBtnText: {
    color: 'white',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  linkText: {
    color: '#667eea',
    textAlign: 'center',
    marginTop: 16,
  },
  profileTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    paddingHorizontal: 16,
    paddingTop: 16,
    marginBottom: 16,
  },
  noBookings: {
    color: '#999',
    textAlign: 'center',
    marginTop: 20,
  },
  bookingItem: {
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#667eea',
  },
  bookingRef: {
    color: '#667eea',
    fontWeight: 'bold',
    marginBottom: 8,
  },
  bookingDetail: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  bookingLabel: {
    color: '#999',
  },
  bookingValue: {
    color: '#ccc',
    fontWeight: 'bold',
  },
});
