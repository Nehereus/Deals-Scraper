async function getModelList() {
    const response = await fetch('./modelsList');
    return response.json();
}
document.addEventListener('DOMContentLoaded', async function () {
    const ctx = document.getElementById('priceHistoryChart').getContext('2d');
    let priceHistoryChart;
    const modelsList = await getModelList();
    fetchAndPlotData(modelsList.slice(0, 5), 7);

    document.getElementById("numModels").addEventListener("change", function (event) {
        let selectedValue = parseInt(event.target.value, 10);
        fetchAndPlotData(modelsList.slice(0, selectedValue), 7); // Use local variable, default to last 7 days
    });

    document.getElementById("dateRange").addEventListener("change", function (event) {
        let selectedValue = parseInt(event.target.value, 10);
        let numModels = parseInt(document.getElementById("numModels").value, 10);
        fetchAndPlotData(modelsList.slice(0, numModels), selectedValue);
    });


    function fetchAndPlotData(selectedModels) {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - dateRange.value);

        const formattedStartDate = startDate.toISOString().split('T')[0]; // 'YYYY-MM-DD'
        const formattedEndDate = endDate.toISOString().split('T')[0]; // 'YYYY-MM-DD'

        const dataFetchPromises = selectedModels.map(model =>
            fetch(`./average-price`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    modelName: model.modelName,
                    startDate: formattedStartDate,
                    endDate: formattedEndDate,
                    condition:"Used"
                })
            })
                .then(response => response.json())
                .then(data => {
                    // Process data to fill missing dates with the last available price
                    const filledData = {};
                    let lastAvailablePrice;
                    for (let date = new Date(formattedStartDate); date <= new Date(formattedEndDate); date.setDate(date.getDate() + 1)) {
                        const dateString = date.toISOString().split('T')[0];
                        if (data[dateString] !== undefined) {
                            lastAvailablePrice = data[dateString];
                        }
                        filledData[dateString] = lastAvailablePrice === undefined ? null : lastAvailablePrice;
                    }
                    return filledData;
                })
        );

        Promise.all(dataFetchPromises).then(pricesByModel => {
            const datasets = selectedModels.map((model, index) => {
                const prices = pricesByModel[index];
                const data = Object.keys(prices).map(date => prices[date]);
                return {
                    label: model.modelName,
                    data: data,
                    borderColor: getLineColor(model.benchmark),
                    tension: 0.4
                };
            });

            const labels = Object.keys(pricesByModel[0]);

            if (priceHistoryChart) {
                priceHistoryChart.destroy(); // Clear previous chart
            }
            priceHistoryChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
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
