// Notification Service
const express = require('express');
const app = express();

app.post('/send-notification', (req, res) => {
  res.json({ status: 'notification sent' });
});

app.listen(3005, () => console.log('Notification Service running on port 3005'));
