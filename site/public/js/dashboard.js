// TerraMind Dashboard Charts Engine (Supabase-connected)
(function() {
    // Apply Chart.js global font settings if loaded
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = 'Outfit, sans-serif';
        Chart.defaults.color = '#bbcbbc'; // on-surface-variant
    }

    // Elements
    const scoreText = document.querySelector('.gauge-circle + text, section.md\\:col-span-4 .text-display-lg');
    const scoreCircle = document.querySelector('.gauge-circle');
    const totalEmissionsText = document.querySelector('section.md\\:col-span-4 .text-headline-md');

    // Fetch dashboard summary data from the API
    fetch('/api/dashboard/summary')
        .then(res => res.json())
        .then(data => {
            const user = data.user;
            const latestLog = data.latest_log;
            const history = data.history;

            // 1. Update Carbon Score Gauge
            if (scoreText) {
                scoreText.textContent = user.carbon_score;
            }
            if (scoreCircle) {
                // Calculate dashoffset: Circumference is 251.2
                const offset = 251.2 * (1 - user.carbon_score / 100);
                scoreCircle.style.strokeDashoffset = offset.toFixed(2);
            }

            // Update Total Emissions Text in Donut Card
            const totalTextContainer = document.querySelector('section.md\\:col-span-4 p.text-headline-md');
            if (totalTextContainer) {
                totalTextContainer.innerHTML = `${latestLog.total_emissions.toFixed(1)} <span class="text-label-md font-normal text-on-surface-variant">Tonnes CO2e</span>`;
            }

            // Update Category Listings next to Donut
            const listItems = document.querySelectorAll('section.md\\:col-span-4 ul.space-y-xs li span.text-on-surface');
            if (listItems.length >= 3) {
                const total = latestLog.total_emissions || 1.0;
                const pt = ((latestLog.transport_emissions / total) * 100).toFixed(0);
                const pe = ((latestLog.energy_emissions / total) * 100).toFixed(0);
                const pd = ((latestLog.diet_emissions / total) * 100).toFixed(0);
                
                listItems[0].textContent = `${pt}%`;
                listItems[1].textContent = `${pe}%`;
                listItems[2].textContent = `${pd}%`;
            }

            // 2. Initialize Emissions Donut Chart
            const donutCtx = document.getElementById('emissions-donut-chart');
            if (donutCtx && typeof Chart !== 'undefined') {
                new Chart(donutCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Transportation', 'Electricity', 'Food Habits', 'Flights', 'Waste'],
                        datasets: [{
                            data: [
                                latestLog.transport_emissions,
                                latestLog.energy_emissions,
                                latestLog.diet_emissions,
                                1.5, // flights static
                                0.4  // waste static
                            ],
                            backgroundColor: [
                                '#00C26E', // Emerald Green
                                '#4DAFFF', // Sky Blue
                                '#B7FF4A', // Eco Lime
                                '#FFD54A', // Solar Yellow
                                '#0D4F8C'  // Deep Ocean Blue
                            ],
                            borderWidth: 2,
                            borderColor: '#0e150f',
                            hoverOffset: 12
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false // Hidden since HTML list acts as legend
                            },
                            tooltip: {
                                backgroundColor: 'rgba(13, 23, 42, 0.95)',
                                titleColor: '#65fea3',
                                bodyColor: '#dce5db',
                                borderColor: 'rgba(255, 255, 255, 0.1)',
                                borderWidth: 1,
                                padding: 12,
                                boxPadding: 8,
                                cornerRadius: 8,
                                callbacks: {
                                    label: function(context) {
                                        const sum = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const pct = ((context.raw / sum) * 100).toFixed(0);
                                        return ` ${context.label}: ${pct}% (${context.raw.toFixed(1)} tCO2e)`;
                                    }
                                }
                            }
                        },
                        cutout: '70%',
                        layout: {
                            padding: 5
                        }
                    }
                });
            }

            // 3. Initialize Weekly Trends Line Chart
            const lineCtx = document.getElementById('trends-line-chart');
            if (lineCtx && typeof Chart !== 'undefined') {
                const gradient = lineCtx.getContext('2d').createLinearGradient(0, 0, 0, 200);
                gradient.addColorStop(0, 'rgba(77, 175, 255, 0.25)');
                gradient.addColorStop(1, 'rgba(77, 175, 255, 0.0)');

                // Get labels (dates) and data points from history
                const sortedHistory = history.slice(-6); // Last 6 logs
                const labels = sortedHistory.map(log => {
                    try {
                        const parts = log.date.split('-');
                        return `${parts[1]}/${parts[2]}`; // MM/DD
                    } catch(e) {
                        return log.date;
                    }
                });
                const trendData = sortedHistory.map(log => log.total_emissions);

                // Fallback standard points if history is empty
                const displayLabels = labels.length > 0 ? labels : ['W1', 'W2', 'W3', 'W4', 'W5', 'W6'];
                const displayData = trendData.length > 0 ? trendData : [5.5, 4.7, 4.2, 2.9, 2.6, 2.6];

                new Chart(lineCtx, {
                    type: 'line',
                    data: {
                        labels: displayLabels,
                        datasets: [{
                            label: 'Weekly Footprint',
                            data: displayData,
                            borderColor: '#4DAFFF',
                            borderWidth: 3,
                            pointBackgroundColor: '#4DAFFF',
                            pointHoverRadius: 6,
                            pointRadius: 4,
                            fill: true,
                            backgroundColor: gradient,
                            tension: 0.35
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: { font: { size: 11 } }
                            },
                            y: {
                                grid: { color: 'rgba(255, 255, 255, 0.04)' },
                                ticks: {
                                    font: { size: 11 },
                                    callback: function(value) { return value + 't'; }
                                }
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: 'rgba(13, 23, 42, 0.95)',
                                titleColor: '#4DAFFF',
                                bodyColor: '#dce5db',
                                borderColor: 'rgba(255, 255, 255, 0.1)',
                                borderWidth: 1,
                                padding: 12,
                                cornerRadius: 8,
                                callbacks: {
                                    label: function(context) {
                                        return ` Footprint: ${context.raw} tCO2e`;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        })
        .catch(err => console.error("Error loading dashboard data:", err));
})();
