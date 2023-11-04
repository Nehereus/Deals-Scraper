const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { parseAndInsert } = require('./updateGPUSpecs');
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
  const { modelName, startDate, endDate } = req.body; // e.g., modelName = "RTX3090", startDate = "2023-10-01", endDate = "2023-10-31"

  // The SQL BETWEEN operator is inclusive, so we subtract one day from endDate to make it exclusive
  const query = `SELECT date_sold, AVG(price) as averagePrice 
                 FROM "${modelName}" 
                 WHERE date_sold BETWEEN ? AND date(?, '-1 day') 
                 GROUP BY date_sold 
                 ORDER BY date_sold`;

  db.all(query, [startDate, endDate], (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: err.message });
    }
    if (rows && rows.length > 0) {
      const averagePrices = {};
      rows.forEach(row => {
        averagePrices[row.date_sold] = row.averagePrice;
      });
      return res.json(averagePrices);
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
  parseAndInsert();
});
