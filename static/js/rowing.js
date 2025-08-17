function renderRowingChart(dates, avg_times) {
    const ctx = document.getElementById('rowingChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Avg 500m Time (s)',
                data: avg_times,
                borderColor: 'red',
                backgroundColor: 'rgba(255,0,0,0.1)',
                yAxisID: 'y1'
            }]
        },
        options: {
            scales: {
                y1: {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Avg 500m Time (s)' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}