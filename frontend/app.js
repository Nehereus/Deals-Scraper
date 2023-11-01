const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const updateGpuSpecs = require('./updateGPUSpecs');
const app = express();
const port = 3000;
const path = require('path');

// Middleware for parsing JSON bodies
app.use(express.json());
app.use(express.static(path.join(__dirname, './Public')));
// Read database path from environment variable
const dbPath = process.env.SHARED_PATH+"/items_database.db"
// Initialize SQLite database connection
let db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error("Error opening database: ", err.message);
  } else {
    console.log("Database connected");
  }
});

// Sample GET route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'Public', 'index.html'));
});

// POST endpoint to get average price of a specific GPU on a specific date
app.post('/average-price', (req, res) => {
  const { modelName, date } = req.body; // e.g., gpu = "RTX3090", date = "2023-10-31"

  const query = `SELECT AVG(price) as averagePrice FROM "${modelName}" WHERE date_sold = ?`;
  db.get(query, [date], (err, row) => {
    if (err) {
      console.log(err)
      return res.status(500).json({ error: err.message });
    }
    if (row && row.averagePrice !== null) {
      return res.json({ averagePrice: row.averagePrice });
    } else {
      return res.status(404).json({ message: 'No data found for given parameters' });
    }
  });
});

app.post('/specs', (req, res) => {
  const { modelName } = req.body; // e.g., modelName = "rtx-3090"

  const query = `SELECT * FROM gpuSpecs WHERE "${modelName}" = ?`;

  db.get(query, [modelName], (err, row) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (row) {
      return res.json(row);
    } else {
      return res.status(404).json({ message: 'No data found for given modelName' });
    }
  });
});

app.get('/modelsList', (req, res) => {
  const query = `SELECT modelName, benchmark FROM gpuSpecs ORDER BY rank LIMIT 100`;

  db.all(query, [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (rows.length > 0) {
      const formattedRows = rows.map(row => ({

        modelName: row.modelName,
        benchmark: row.benchmark
      }));
      return res.json(formattedRows);
    } else {
      return res.status(404).json({ message: 'No data found' });
    }
  });
});



// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
  updateGpuSpecs()
});
