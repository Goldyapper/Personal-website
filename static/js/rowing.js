function renderRowingChart(dates, avg_times) {
    const ctx = document.getElementById('rowingChart').getContext('2d');

    const majorYStep = 5;
    const minorYStep = majorYStep/2;

    const rawMax = Math.max(...avg_times) + minorYStep;
    const rawMin = Math.min(...avg_times) - minorYStep;
    const minY = Math.floor(rawMin / minorYStep) * minorYStep;
    const maxY = Math.ceil(rawMax / minorYStep) * minorYStep;

    const firstDateLinePlugin = {
        id: 'firstDateLine',
        afterDraw: chart => {
            const ctx = chart.ctx;
            const xAxis = chart.scales.x;
            const yAxis = chart.scales.y;

            const x = xAxis.getPixelForTick(0); // first tick (first date)
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, yAxis.top);
            ctx.lineTo(x, yAxis.bottom);
            ctx.lineWidth = 1;
            ctx.strokeStyle = '#000000'; // solid black
            ctx.stroke();
            ctx.restore();
        }
    };


    // Generate all Y ticks (major + minor)
    const yTicks = [];
    for (let v = minY; v <= maxY; v += minorYStep) {
        yTicks.push({
            value: v,
            major: v % majorYStep === 0
        });
    }

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Avg 500m Time (s)',
                data: avg_times,
                borderColor: '#b22222',
                fill: false
            }]
        },
        options: {
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
                        color: context => context.tick && context.tick.major
                            ? 'rgba(0, 0, 0, 0.5)'     // major horizontal line
                            : 'rgba(0, 0, 0, 0.1)',    // minor horizontal line (lighter, still visible)
                        drawTicks: true,
                        tickLength: 5
                    }
                },
                x: {
                    ticks: { autoSkip: false },
                    grid: {
                        color: 'rgba(128, 0, 0, 0.5)', // faint vertical grid lines
                        drawTicks: true,
                        tickLength: 5,
                    }
                }
            },
            plugins: {
                legend: { display: true, labels: { color: '#222222' } }
            }
        },
        plugins: [firstDateLinePlugin]
    });
}