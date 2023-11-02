let modelsList;

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('priceHistoryChart').getContext('2d');
    let priceHistoryChart;

    // Fetch the models list
    fetch('./modelsList')
        .then(response => response.json())
        .then(models => {
            modelsList = models; // Store in a local variable
            fetchAndPlotData(models.slice(0, 5), 7); // Default top 5 and last 7 days
        });

    document.getElementById("numModels").addEventListener("change", function(event) {
        let selectedValue = parseInt(event.target.value, 10);
        fetchAndPlotData(modelsList.slice(0, selectedValue), 7); // Use local variable, default to last 7 days
    });

    document.getElementById("dateRange").addEventListener("change", function(event) {
        let selectedValue = parseInt(event.target.value, 10);
        let numModels = parseInt(document.getElementById("numModels").value, 10);
        fetchAndPlotData(modelsList.slice(0, numModels), selectedValue);
    });


    function fetchAndPlotData(selectedModels) {
        let dates;
        const dataFetchPromises = selectedModels.map(model => {
            dates = Array.from({ length: dateRange.value }, (_, i) => {
                const d = new Date();
                d.setDate(d.getDate() - i);
                return d.toISOString().split('T')[0]; // 'YYYY-MM-DD'
            }).reverse();


            return Promise.all(dates.map(date =>
                fetch(`./average-price`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ modelName: model.modelName, date: date })
                }).then(response => response.json())
            ));
        });
        Promise.all(dataFetchPromises).then(prices => {
            const datasets = selectedModels.map((model, index) => ({
                label: model.modelName,
                data: prices[index].map(obj => obj.averagePrice),
                borderColor: getLineColor(model.benchmark), // Assuming the API returns a field called 'averagePrice'
                tension: 0.3
            }));

            if (priceHistoryChart) {
                priceHistoryChart.destroy(); // Clear previous chart
            }
            priceHistoryChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: datasets
                },

            });
        });
    }

    function getLineColor(benchmark) {
        const scale = (benchmark - 0) / (400 - 0); // Replace 0 and 100 with min and max benchmarks
        const red = Math.floor(scale * 255);
        const green = 255 - red;
        return `rgb(${red}, ${green}, 0)`;
    }
});
