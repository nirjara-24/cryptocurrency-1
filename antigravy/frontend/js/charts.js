class ChartManager {
    constructor() {
        this.charts = {};
        this.chartTypes = {
            main: 'line',
            full: 'line',
            comparison: 'line'
        };
        this.theme = 'dark';
        this.colors = {
            price: '#6366f1',
            arima: '#818cf8',
            prophet: '#06b6d4',
            lstm: '#10b981',
            bullish: '#10b981',
            bearish: '#f43f5e',
            neutral: '#3b82f6',
            border: 'rgba(255, 255, 255, 0.1)',
            text: '#94a3b8'
        };
    }

    get currentForeColor() {
        return this.theme === 'light' ? '#475569' : '#94a3b8';
    }

    get currentBorderColor() {
        return this.theme === 'light' ? 'rgba(0,0,0,0.08)' : 'rgba(255,255,255,0.1)';
    }

    renderAll(data, assetName, activeIndicators = []) {
        console.log(`Rendering all charts for ${assetName}... (v2)`);
        this.renderMainPriceChart(data.historical, assetName, data.forecasts);
        this.renderSentimentChartMini(data.sentiment);

        // Chart Page
        this.updateFullChart(data, assetName, activeIndicators);
        this.renderFullIndicators(data.indicators);

        // Prediction Page
        this.renderModelCharts(data.historical, assetName, data.forecasts);

        // Sentiment Page
        this.renderFullSentiment(data.sentiment);
    }

    // Dashboard: Main Interactive Price Chart
    renderMainPriceChart(historical, assetName, forecasts) {
        const id = 'mainPriceChart';
        const type = this.chartTypes.main;

        let seriesData;
        if (type === 'candle') {
            seriesData = historical.map(d => ({
                x: new Date(d.date).getTime(),
                y: [d.open, d.high, d.low, d.close]
            }));
        } else {
            seriesData = historical.map(d => ({ x: new Date(d.date).getTime(), y: d.close }));
        }

        const options = {
            series: [{ name: `${assetName} Price`, data: seriesData }],
            chart: {
                type: type === 'candle' ? 'candlestick' : 'area',
                height: 350,
                theme: { mode: this.theme },
                background: 'transparent',
                toolbar: { show: true, tools: { zoomin: true, zoomout: true, pan: true, reset: true } },
                zoom: { enabled: true, autoScaleYaxis: true },
                foreColor: this.currentForeColor
            },
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth', width: type === 'candle' ? 1 : 2 },
            fill: {
                type: type === 'candle' ? 'solid' : 'gradient',
                gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 90, 100] }
            },
            colors: [type === 'candle' ? '#00b8d9' : this.colors.price],
            xaxis: { type: 'datetime' },
            yaxis: { labels: { formatter: (v) => '$' + v.toLocaleString() } },
            tooltip: { theme: this.theme, x: { format: 'dd MMM yyyy' } },
            grid: { borderColor: this.currentBorderColor },
            plotOptions: {
                candlestick: {
                    colors: { upward: '#10b981', downward: '#f43f5e' },
                    wick: { useFillColor: true }
                }
            }
        };

        this.updateChartInstance(id, options);
    }

    // Chart Page: Advanced Technical Chart
    updateFullChart(data, assetName, activeIndicators) {
        const id = 'fullPriceChart';
        const historical = data.historical;
        const indicators = data.indicators;
        const type = this.chartTypes.full;

        let mainSeriesData;
        if (type === 'candle') {
            mainSeriesData = historical.map(d => ({
                x: new Date(d.date).getTime(),
                y: [d.open, d.high, d.low, d.close]
            }));
        } else {
            mainSeriesData = historical.map(d => ({ x: new Date(d.date).getTime(), y: d.close }));
        }

        const series = [{
            name: `${assetName} Price`,
            type: type === 'candle' ? 'candlestick' : 'line',
            data: mainSeriesData
        }];

        if (activeIndicators.includes('sma_20')) {
            series.push({
                name: 'SMA 20',
                type: 'line',
                data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.sma_20 }))
            });
        }
        if (activeIndicators.includes('sma_50')) {
            series.push({
                name: 'SMA 50',
                type: 'line',
                data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.sma_50 }))
            });
        }
        if (activeIndicators.includes('bb')) {
            series.push({
                name: 'BB Upper',
                type: 'line',
                data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.bb_upper }))
            });
            series.push({
                name: 'BB Lower',
                type: 'line',
                data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.bb_lower }))
            });
        }

        const options = {
            series: series,
            chart: {
                type: type === 'candle' ? 'candlestick' : 'line',
                height: 450,
                background: 'transparent',
                theme: { mode: this.theme },
                toolbar: { show: true },
                zoom: { enabled: true, type: 'x', autoScaleYaxis: true },
                foreColor: this.currentForeColor
            },
            dataLabels: { enabled: false },
            stroke: {
                width: series.map((s, i) => i === 0 ? (type === 'candle' ? 1 : 3) : 1.5),
                curve: 'smooth'
            },
            colors: [type === 'candle' ? '#00b8d9' : this.colors.price, '#ef4444', '#3b82f6', '#10b981', '#10b981'],
            xaxis: { type: 'datetime' },
            yaxis: { labels: { formatter: (v) => '$' + v.toLocaleString() } },
            tooltip: { x: { format: 'dd MMM yyyy' } },
            grid: { borderColor: this.currentBorderColor },
            plotOptions: {
                candlestick: {
                    colors: { upward: '#10b981', downward: '#f43f5e' },
                    wick: { useFillColor: true }
                }
            }
        };

        this.updateChartInstance(id, options);
    }

    renderFullIndicators(indicators) {
        this.renderRSI('fullRsiChart', indicators);
        this.renderMACD('fullMacdChart', indicators);
    }

    // Prediction Page Charts
    renderModelCharts(historical, assetName, forecasts) {
        // 1. Render Comparison Chart
        this.renderComparisonChart(historical, assetName, forecasts);

        // 2. Render Individual Model Details
        ['ARIMA', 'Prophet', 'LSTM'].forEach(model => {
            const id = `${model.toLowerCase()}Chart`;
            const forecastData = forecasts[model] || [];
            if (forecastData.length === 0) return;

            // Get last 30 days of historical for context
            const historyLimit = 30;
            const historicalContext = historical.slice(-historyLimit);

            const contextData = historicalContext.map(d => ({ x: new Date(d.date).getTime(), y: d.close }));
            const forecastPoints = forecastData.map(d => ({ x: new Date(d.date).getTime(), y: d.predicted_price }));

            // Combine for the main line
            const mainLineData = [...contextData, ...forecastPoints];

            // Confidence Interval Data (Range Area)
            const rangeData = [
                ...historicalContext.map(d => ({ x: new Date(d.date).getTime(), y: [null, null] })),
                ...forecastData.map(d => ({ x: new Date(d.date).getTime(), y: [d.lower_bound, d.upper_bound] }))
            ];

            const options = {
                series: [
                    { name: 'Price/Forecast', type: 'line', data: mainLineData },
                    { name: 'Confidence Interval', type: 'rangeArea', data: rangeData }
                ],
                chart: {
                    type: 'line',
                    height: 300,
                    toolbar: { show: false },
                    background: 'transparent',
                    theme: { mode: this.theme },
                    foreColor: this.currentForeColor,
                    animations: { enabled: true }
                },
                dataLabels: { enabled: false },
                stroke: {
                    curve: 'smooth',
                    width: [3, 0],
                    dashArray: [0, 0]
                },
                colors: [this.getModelColor(model), this.getModelColor(model)],
                fill: {
                    type: ['solid', 'solid'],
                    opacity: [1, 0.15]
                },
                markers: {
                    size: [0, 0],
                    hover: { size: 5 }
                },
                xaxis: {
                    type: 'datetime',
                    tooltip: { enabled: false }
                },
                yaxis: {
                    show: true,
                    labels: {
                        formatter: (v) => '$' + v.toLocaleString(),
                        style: { colors: this.colors.text }
                    }
                },
                grid: {
                    show: true,
                    borderColor: this.colors.border,
                    strokeDashArray: 4
                },
                legend: { show: false },
                tooltip: {
                    theme: this.theme,
                    shared: true,
                    x: { format: 'dd MMM yyyy' },
                    y: {
                        formatter: (v) => v ? '$' + v.toLocaleString() : null
                    }
                },
                annotations: {
                    xaxis: [{
                        x: contextData[contextData.length - 1].x,
                        borderColor: '#94a3b8',
                        label: {
                            style: { color: '#fff', background: '#475569' },
                            text: 'Forecast Start'
                        }
                    }]
                }
            };

            this.updateChartInstance(id, options);
        });
    }

    renderComparisonChart(historical, assetName, forecasts) {
        const id = 'combinedComparisonChart';
        const historyLimit = 60;
        const historicalContext = historical.slice(-historyLimit);
        const type = this.chartTypes.comparison;

        let mainSeriesData;
        if (type === 'candle') {
            mainSeriesData = historicalContext.map(d => ({
                x: new Date(d.date).getTime(),
                y: [d.open, d.high, d.low, d.close]
            }));
        } else {
            mainSeriesData = historicalContext.map(d => ({ x: new Date(d.date).getTime(), y: d.close }));
        }

        const series = [{
            name: 'Historical Price',
            type: type === 'candle' ? 'candlestick' : 'area',
            data: mainSeriesData
        }];

        ['ARIMA', 'Prophet', 'LSTM'].forEach(model => {
            const forecastData = forecasts[model] || [];
            if (forecastData.length > 0) {
                const lastHistory = historicalContext[historicalContext.length - 1];
                const data = [
                    { x: new Date(lastHistory.date).getTime(), y: lastHistory.close },
                    ...forecastData.map(d => ({ x: new Date(d.date).getTime(), y: d.predicted_price }))
                ];
                series.push({
                    name: `${model} Prediction`,
                    type: 'line',
                    data: data
                });
            }
        });

        const options = {
            series: series,
            chart: {
                height: 400,
                type: type === 'candle' ? 'candlestick' : 'line',
                background: 'transparent',
                theme: { mode: this.theme },
                toolbar: { show: true },
                foreColor: this.currentForeColor
            },
            dataLabels: { enabled: false },
            colors: [type === 'candle' ? '#00b8d9' : this.colors.price, '#a855f7', '#3b82f6', '#10b981'],
            stroke: {
                width: [type === 'candle' ? 1 : 2, 3, 3, 3],
                curve: 'smooth',
                dashArray: [0, 5, 5, 5]
            },
            fill: {
                type: [type === 'candle' ? 'solid' : 'gradient', 'solid', 'solid', 'solid'],
                gradient: {
                    shadeIntensity: 1,
                    opacityFrom: 0.3,
                    opacityTo: 0.05,
                    stops: [0, 90, 100]
                }
            },
            xaxis: { type: 'datetime' },
            yaxis: {
                labels: { formatter: (v) => '$' + v.toLocaleString() }
            },
            tooltip: {
                theme: this.theme,
                shared: true,
                x: { format: 'dd MMM yyyy' }
            },
            legend: {
                position: 'bottom',
                horizontalAlign: 'center',
                labels: { colors: this.colors.text },
                markers: { radius: 12 }
            },
            grid: { borderColor: this.colors.border },
            plotOptions: {
                candlestick: {
                    colors: { upward: '#10b981', downward: '#f43f5e' },
                    wick: { useFillColor: true }
                }
            }
        };

        this.updateChartInstance(id, options);
    }

    renderFullSentiment(sentiment) {
        this.renderSentimentDistribution('fullSentimentChart', sentiment);

        const id = 'sentimentHistoryChart';
        const options = {
            series: [{
                name: 'Sentiment Score',
                data: sentiment.map(d => ({ x: new Date(d.date).getTime(), y: d.score }))
            }],
            chart: {
                type: 'area',
                height: 350,
                theme: { mode: this.theme },
                foreColor: this.currentForeColor,
                toolbar: { show: true },
                background: 'transparent'
            },
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth', width: 2 },
            colors: [this.colors.prophet],
            fill: { type: 'gradient', gradient: { opacityFrom: 0.6, opacityTo: 0.1 } },
            xaxis: { type: 'datetime' },
            yaxis: {
                min: -1,
                max: 1,
                labels: { style: { colors: this.colors.text } }
            },
            grid: { borderColor: this.currentBorderColor },
            tooltip: { theme: this.theme }
        };

        this.updateChartInstance(id, options);
    }

    renderSentimentDistribution(id, sentiment) {
        const counts = sentiment.reduce((acc, curr) => {
            acc[curr.sentiment_label] = (acc[curr.sentiment_label] || 0) + 1;
            return acc;
        }, {});

        const options = {
            series: Object.values(counts),
            labels: Object.keys(counts),
            chart: { type: 'donut', height: id.includes('Mini') ? 220 : 350 },
            colors: [this.colors.bullish, this.colors.neutral, this.colors.bearish],
            stroke: { show: false },
            legend: { position: 'bottom', labels: { colors: this.colors.text } },
            plotOptions: { pie: { donut: { size: '75%', labels: { show: !id.includes('Mini'), total: { show: true, color: '#fff' } } } } },
            dataLabels: { enabled: false }
        };

        this.updateChartInstance(id, options);
    }

    renderSentimentChartMini(sentiment) {
        this.renderSentimentDistribution('sentimentChartMini', sentiment);
    }

    renderRSI(id, indicators) {
        const options = {
            series: [{ name: 'RSI', data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.rsi_14 })) }],
            chart: { type: 'line', height: 200, toolbar: { show: false }, background: 'transparent', theme: { mode: this.theme }, foreColor: this.currentForeColor },
            dataLabels: { enabled: false },
            stroke: { width: 1.5 },
            colors: [this.colors.price],
            yaxis: { min: 0, max: 100, tickAmount: 2 },
            xaxis: { type: 'datetime', labels: { show: false } },
            grid: { borderColor: this.currentBorderColor },
            annotations: { y: [{ y: 70, borderColor: '#ef4444' }, { y: 30, borderColor: '#10b981' }] }
        };
        this.updateChartInstance(id, options);
    }

    renderMACD(id, indicators) {
        const options = {
            series: [{
                name: 'MACD Hist',
                data: indicators.map(d => ({ x: new Date(d.date).getTime(), y: d.macd - d.macd_signal }))
            }],
            chart: { type: 'bar', height: 200, toolbar: { show: false }, background: 'transparent', theme: { mode: this.theme }, foreColor: this.currentForeColor },
            colors: [({ value }) => value > 0 ? this.colors.bullish : this.colors.bearish],
            xaxis: { type: 'datetime', labels: { show: false } },
            grid: { borderColor: this.currentBorderColor },
            plotOptions: { bar: { columnWidth: '80%' } },
            dataLabels: { enabled: false }
        };
        this.updateChartInstance(id, options);
    }

    updateChartInstance(id, options) {
        const el = document.getElementById(id);
        if (!el) return;

        if (this.charts[id]) {
            this.charts[id].updateOptions(options, false, true);
            if (options.series) {
                this.charts[id].updateSeries(options.series);
            }
        } else {
            this.charts[id] = new ApexCharts(el, options);
            this.charts[id].render();
        }
    }

    getModelColor(model) {
        const colors = { ARIMA: '#a855f7', Prophet: '#3b82f6', LSTM: '#10b981' };
        return colors[model] || '#f1f5f9';
    }
}

window.charts = new ChartManager();
