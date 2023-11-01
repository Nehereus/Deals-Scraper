const axios = require('axios');
const csv = require('csv-parser');
const stream = require('stream');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');

const sharedPath = process.env.SHARED_PATH;
const dbPath = sharedPath+"/items_database.db"
let db = new sqlite3.Database(dbPath);

module.exports = async function parseAndInsert() {
    const response = await axios.get('https://www.userbenchmark.com/resources/download/csv/GPU_UserBenchmarks.csv', { responseType: 'stream' });
    const readable = new stream.Readable().wrap(response.data);

    db.run(`CREATE TABLE IF NOT EXISTS gpuSpecs (
            modelName TEXT PRIMARY KEY,
            type TEXT,
            partNumber TEXT,
            brand TEXT,
            rank INTEGER,
            benchmark REAL,
            samples INTEGER,
            url TEXT UNIQUE
        );`);

    readable
        .pipe(csv())
        .on('data', (row) => {
            const validBrands=["Intel","Nvidia","AMD",""]

            let modelName = row['Model'];
            let brand = row['Brand'];

            if (modelName.toLowerCase().includes('laptop')) return;
            if(!validBrands.includes(brand)){
                console.log(brand)
                return;
            }
            modelName = modelName.replace(/\(|\)/g, '').toLowerCase().replace(/ /g, '-');
            db.run(`INSERT OR IGNORE INTO gpuSpecs (modelName, type, partNumber, brand, rank, benchmark, samples, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
                [modelName, row['Type'], row['Part Number'], row['Brand'], row['Rank'], row['Benchmark'], row['Samples'], row['URL']]);
        })
        .on('end', () => {
            console.log('CSV file successfully processed');
            writeTop100ToJSON();
        });
};

function writeTop100ToJSON() {
    let top100GPUs = {};
    const filePath = `${sharedPath}/config.json`;

    // Check if the file exists and delete it
    if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
    }

    db.all(`SELECT modelName FROM gpuSpecs ORDER BY rank LIMIT 100`, [], (err, rows) => {
        if (err) throw err;
        rows.forEach((row) => {
            let formattedModelName = row.modelName;
            top100GPUs[formattedModelName] = { "MinPrice": 100, "MaxPrice": 5000 };
        });

        // Write to the file
        fs.writeFileSync(filePath, JSON.stringify(top100GPUs, null, 2));
    });
    }

