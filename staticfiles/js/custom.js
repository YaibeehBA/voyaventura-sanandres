document.addEventListener('DOMContentLoaded', function() {
    // Obtener y parsear los datos del dashboard
    var dashboardDataElement = document.getElementById('dashboard-data');
    var dashboardData = JSON.parse(dashboardDataElement.textContent);

    // Gráfica de líneas
    var lineChartOptions = {
        series: [{
            name: 'Alojamientos',
            data: dashboardData.datos_alojamientos
        }, {
            name: 'Guías',
            data: dashboardData.datos_guias
        }, {
            name: 'Total',
            data: dashboardData.datos_total
        }],
        chart: {
            height: 350,
            type: 'line',
            zoom: { enabled: false }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'straight' },
        grid: {
            row: {
                colors: ['#f3f3f3', 'transparent'],
                opacity: 0.5
            },
        },
        xaxis: {
            categories: dashboardData.meses,
        }
    };
    var lineChart = new ApexCharts(document.querySelector("#lineChart"), lineChartOptions);
    lineChart.render();

    // Gráfica circular
    var pieChartOptions = {
        series: [dashboardData.total_alojamientos_pagados, dashboardData.total_guias_pagados],
        chart: {
            width: 350,
            type: 'pie',
        },
        labels: ['Alojamientos', 'Guías'],
        responsive: [{
            breakpoint: 480,
            options: {
                chart: { width: 200 },
                legend: { position: 'bottom' }
            }
        }]
    };
    var pieChart = new ApexCharts(document.querySelector("#pieChart"), pieChartOptions);
    pieChart.render();

    // Gráfica de barras horizontal
    var barChartOptions = {
        series: [{
            data: [
                dashboardData.total_alojamientos_pagados,
                dashboardData.total_guias_pagados
            ]
        }],
        chart: {
            type: 'bar',
            height: 120
        },
        plotOptions: {
            bar: {
                horizontal: true,
                distributed: true
            }
        },
        dataLabels: { enabled: false },
        xaxis: {
            categories: ['Alojamientos', 'Guías']
        }
    };

    var barChart = new ApexCharts(document.querySelector("#barChart"), barChartOptions);
    barChart.render();
});
