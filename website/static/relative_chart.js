document.addEventListener("DOMContentLoaded", function() {
    
    const background_plugin = {
        id: 'custom_canvas_background_color',
        beforeDraw: (chart) => {
            const {ctx} = chart;
            var chartArea = chart.chartArea
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = '#D4E5F0';
            //ctx.fillRect(0, 0, chart.width, chart.height);
            ctx.fillRect(chartArea.left, chartArea.top, chartArea.right - chartArea.left, chartArea.bottom - chartArea.top);
            ctx.restore();
        }
    };

    abs_max = 0;
    abs_min = 0;
    relative_data.datasets.forEach((array) => {
        array.data.forEach((val) => {
            if(val > abs_max) abs_max = Math.ceil(val)
            if(val < abs_min) abs_min = Math.floor(val)
        })
    })

    const config = {
        type: 'line',
        data: relative_data,
        //plugins: [background_plugin],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: legend_config,
                title: {
                    display: true,
                    text: ['Percentage change in value per color for all cars', 'on Autotrader in ' + year_selection],
                    font: {
                        size: 25,
                        family: "Poppins",
                        weight: 'normal'
                    },
                    color: '#6C99B7'

                }
            },
            scales:{
                y: {
                    min: Math.floor(abs_min*1.5/5)*5,
                    max: Math.ceil(abs_max*1.5/5)*5,
                    title: {
                        display: true,
                        text: 'Percentage Change (%)',
                        font: {
                            size: 16,
                            family: "Poppins",
                            weight: 'normal'
                        },
                        color: '#6C99B7'
                    },
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        color: '#6C99B7',
                        font: {
                            family: 'Poppins'
                        }
                    },
                    grid: {
                        //borderColor: '#6C99B7'
                    }
                },
                xAxes: {
                    title: xtitle_config,
                    ticks: xticks_config,
                    grid: {
                        //borderColor: '#6C99B7'
                    }                        
                }
            },
            elements: {
                point: {
                    radius: 0
                },
                line: {
                    borderWidth: 2,
                    cubicInterpolationMode: 'default',
                    borderJoinStyle: 'round',
                    borderCapStyle: 'round',
                    tension: 0.3
                }
            }
        }
    };

    function adapt_to_screen_size(lineChart) {
        if (window.innerWidth < 1200) {
            lineChart.options.scales.xAxes.ticks.maxRotation = 45
            lineChart.options.scales.xAxes.ticks.minRotation = 45
            lineChart.options.scales.y.title.display = false
        } else if (window.innerWidth > 1200) {
            lineChart.options.scales.xAxes.ticks.maxRotation = 0
            lineChart.options.scales.xAxes.ticks.minRotation = 0
            lineChart.options.scales.y.title.display = true
        }
    }

    window.addEventListener('load', function() {
        var ctx = document.getElementById("myChart2").getContext("2d");
        var lineChart = new Chart(ctx, config);
        adapt_to_screen_size(lineChart)
        window.addEventListener('resize', (event) => {
            adapt_to_screen_size(lineChart)
        })
    })

});