const axios = require('axios');
const csv = require('csv-parser');
const stream = require('stream');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const sharedPath = process.env.SHARED_PATH;
const dbPath = sharedPath+"/items_database.db"
let db = new sqlite3.Database(dbPath);
const cheerio = require('cheerio');

    async function parseAndInsert() {
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
}

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

async function update3DMark() {
    try {
        const url = 'https://www.videocardbenchmark.net/high_end_gpus.html';
        // Fetch the content from the URL
        const response = await axios.get(url);
        const html = response.data;

        // Load the HTML into cheerio
        const $ = cheerio.load(html);

        // Initialize an array to hold our processed data
        const processedData = [];

        // Find all elements with the class 'chartlist' and their children with class 'alt'
        $('.chartlist .alt').each(function () {
            // Find the children with class 'prdname' and 'count'
            const prdName = $(this).find('.prdname').text().trim();
            const count = $(this).find('.count').text().trim();

            // Process the product name: remove the first word, convert to lowercase and replace spaces with hyphens
            const processedPrdName = prdName.split(' ').slice(1).join(' ').toLowerCase().replace(/\s+/g, '-');

            // Store in our array
            processedData.push({
                productName: processedPrdName,
                count: count
            });
        });

        return processedData;

    } catch (error) {
    console.error(error);
    throw error;}
}

module.exports ={update3DMark,parseAndInsert}

