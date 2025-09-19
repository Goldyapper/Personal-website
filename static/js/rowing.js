function renderRowingChart(dates, avg_times) {
    const ctx = document.getElementById('rowingChart').getContext('2d');

    const majorYStep = 5;
    const minorYStep = majorYStep / 2;

    const rawMax = Math.max(...avg_times) + minorYStep;
    const rawMin = Math.min(...avg_times) - minorYStep;
    const minY = Math.floor(rawMin / minorYStep) * minorYStep;
    const maxY = Math.ceil(rawMax / minorYStep) * minorYStep;

    const scatterData = dates.map((dateStr, i) => ({
        x: luxon.DateTime.fromISO(dateStr, { zone: 'local' }).toJSDate(),
        y: avg_times[i]
    }));

    // Linear regression plugin
    const linearRegressionPlugin = {
        id: 'linearRegression',
        afterDraw: chart => {
            const ctx = chart.ctx;
            const xScale = chart.scales.x;
            const yScale = chart.scales.y;
            const data = chart.data.datasets[0].data;
            if (data.length < 2) return;

            const xVals = data.map(d => new Date(d.x).getTime());
            const yVals = data.map(d => d.y);
            const n = xVals.length;

            const sumX = xVals.reduce((a,b) => a+b, 0);
            const sumY = yVals.reduce((a,b) => a+b, 0);
            const sumXY = xVals.reduce((a,b,i) => a + b*yVals[i], 0);
            const sumXX = xVals.reduce((a,b) => a + b*b, 0);

            const slope = (n*sumXY - sumX*sumY) / (n*sumXX - sumX*sumX);
            const intercept = (sumY - slope*sumX) / n;

            const xMin = Math.min(...xVals);
            const xMax = Math.max(...xVals);

            ctx.save();
            ctx.beginPath();
            ctx.moveTo(xScale.getPixelForValue(xMin), yScale.getPixelForValue(slope*xMin + intercept));
            ctx.lineTo(xScale.getPixelForValue(xMax), yScale.getPixelForValue(slope*xMax + intercept));
            ctx.strokeStyle = 'rgba(60, 0, 255, 0.75)';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.stroke();
            ctx.restore();
        }
    };

    // First-date vertical line plugin
    const Blackborderplugin = {
        id: 'firstDateLine',
        afterDatasetsDraw: chart => {
            const dataset = chart.data.datasets[0].data;
            if (!dataset || dataset.length === 0) return;

            const ctx = chart.ctx;
            const { top, bottom, left, right } = chart.chartArea;

            ctx.beginPath();
            ctx.moveTo(left, bottom);
            ctx.lineTo(right, bottom);
            ctx.moveTo(left, top);
            ctx.lineTo(left, bottom);
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.restore();
        }
    };

    // Y-axis ticks
    const yTicks = [];
    for (let v = minY; v <= maxY; v += minorYStep) {
        yTicks.push({ value: v, major: v % majorYStep === 0 });
    }

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Avg 500m speed',
                data: scatterData,
                borderColor: '#b22222',
                backgroundColor: '#b22222',
                fill: false,
                showLine: true, 
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    min: minY,
                    max: maxY,
                    afterBuildTicks: axis => { axis.ticks = yTicks; },
                    ticks: {
                        callback: tick => tick % majorYStep === 0 ? tick : '',
                        autoSkip: false,
                        color: '#222222'
                    },
                    grid: {
                        color: context => context.tick && context.tick.major ? 'rgba(0,0,0,0.5)' : 'rgba(0,0,0,0.1)',
                        drawTicks: true,
                        tickLength: 5
                    }
                },
                x: {
                    type: 'time',
                    time: { unit: 'day', tooltipFormat: 'dd-MM-yyyy' },
                    ticks: {
                        autoSkip: false,
                        callback: value => {
                            const d = new Date(value);
                            const year = d.getFullYear();
                            const month = String(d.getMonth() + 1).padStart(2, '0'); // months 0-11
                            const day = String(d.getDate()).padStart(2, '0');
                            return `${year}-${month}-${day}`;
                        }
                    },
                    grid: {
                        color: 'rgba(26,0,128,0.5)',
                        drawTicks: true,
                        tickLength: 5
                    }
                }
            },
            plugins: {
                legend: { display: true, labels: { color: '#222222' } }
            }
        },
        plugins: [Blackborderplugin, linearRegressionPlugin]
    });
}