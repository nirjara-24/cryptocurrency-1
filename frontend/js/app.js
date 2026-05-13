const API_BASE_URL = 'http://localhost:5000/api';

class DashboardApp {
    constructor() {
        this.data = {
            historical: [],
            indicators: [],
            forecasts: {},
            stats: {},
            sentiment: []
        };
        this.currentView = 'dashboard';
        this.currentDays = 90;
        this.currentSymbol = 'BTC-USD';
        this.symbolMap = {
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum',
            'SOL-USD': 'Solana',
            'BNB-USD': 'Binance Coin',
            'XRP-USD': 'Ripple',
            'ADA-USD': 'Cardano',
            'DOGE-USD': 'Dogecoin',
            'DOT-USD': 'Polkadot',
            'MATIC-USD': 'Polygon',
            'LINK-USD': 'Chainlink'
        };
        this.isLoading = false;

        this.init();
    }

    async init() {
        console.log('App initialization (v2)...');
        this.setupEventListeners();
        this.applyStoredTheme();
        await this.loadAllData();
        this.updateUI();
    }

    applyStoredTheme() {
        const stored = localStorage.getItem('cryptoTheme');
        if (stored === 'light') {
            document.body.classList.add('light-mode');
            const btn = document.querySelector('.theme-toggle i');
            if (btn) { btn.className = 'fas fa-sun'; }
            if (window.charts) window.charts.theme = 'light';
        }
    }

    toggleTheme() {
        const isLight = document.body.classList.toggle('light-mode');
        const icon = document.querySelector('.theme-toggle i');
        if (isLight) {
            if (icon) icon.className = 'fas fa-sun';
            localStorage.setItem('cryptoTheme', 'light');
            window.charts.theme = 'light';
        } else {
            if (icon) icon.className = 'fas fa-moon';
            localStorage.setItem('cryptoTheme', 'dark');
            window.charts.theme = 'dark';
        }
        // Re-render all charts with the new theme
        const name = this.getFriendlyName();
        window.charts.renderAll(this.data, name, this.getActiveIndicators());
    }

    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', () => this.refreshData());

        document.querySelector('.theme-toggle').addEventListener('click', () => this.toggleTheme());

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                this.switchView(view);

                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            });
        });

        document.querySelectorAll('.range-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentDays = parseInt(e.target.dataset.days);
                this.loadAllData();
            });
        });

        document.querySelectorAll('.indicator-toggle').forEach(chk => {
            chk.addEventListener('change', () => {
                const name = this.getFriendlyName();
                window.charts.updateFullChart(this.data, name, this.getActiveIndicators());
            });
        });

        document.querySelectorAll('.chart-type-toggles .type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const group = e.target.closest('.toggle-group');
                const target = group.dataset.target;
                const type = e.target.dataset.type;

                // Update UI
                group.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');

                // Update ChartManager state
                window.charts.chartTypes[target] = type;

                // Re-render specific chart
                this.refreshSpecificChart(target);
            });
        });

        const assetSelect = document.getElementById('asset-select');
        assetSelect.addEventListener('change', (e) => {
            this.handleAssetChange(e.target.value);
        });
    }

    async handleAssetChange(symbol) {
        if (!symbol) return;
        console.log(`Switching asset to: ${symbol}`);
        this.currentSymbol = symbol;
        this.updateAllTitles();
        this.showLoading(true);
        try {
            await this.loadAllData();
        } catch (error) {
            console.error('Asset switch error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    getFriendlyName() {
        return this.symbolMap[this.currentSymbol] || this.currentSymbol;
    }

    updateAllTitles() {
        const name = this.getFriendlyName();
        const titleEl = document.getElementById('analysis-title');
        if (titleEl) titleEl.innerText = `${name} (${this.currentSymbol}) Price Analysis`;
        const techTitleEl = document.getElementById('technical-analysis-title');
        if (techTitleEl) techTitleEl.innerText = `${name} Technical Analysis`;
        ['ARIMA', 'Prophet', 'LSTM'].forEach(model => {
            const headerEl = document.getElementById(`${model.toLowerCase()}-header`);
            if (headerEl) headerEl.innerText = `${name} ${model} Forecast`;
        });
        const sentDistTitle = document.getElementById('sentiment-dist-title');
        if (sentDistTitle) sentDistTitle.innerText = `${name} Sentiment Distribution`;
        const sentHistTitle = document.getElementById('sentiment-hist-title');
        if (sentHistTitle) sentHistTitle.innerText = `${name} Sentiment Score History`;
    }

    getActiveIndicators() {
        const indicators = [];
        document.querySelectorAll('.indicator-toggle:checked').forEach(chk => {
            indicators.push(chk.dataset.indicator);
        });
        return indicators;
    }

    switchView(viewId) {
        this.currentView = viewId;
        document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
        const targetView = document.getElementById(`view-${viewId}`);
        if (targetView) targetView.classList.remove('hidden');
        this.updateAllTitles();
        const name = this.getFriendlyName();
        window.charts.renderAll(this.data, name, this.getActiveIndicators());
    }

    showLoading(show) {
        this.isLoading = show;
        document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
    }

    async loadAllData() {
        this.showLoading(true);
        try {
            const symbolParam = `&symbol=${this.currentSymbol}`;
            const [historical, indicators, stats, arima, prophet, lstm, sentiment] = await Promise.all([
                this.fetchData(`/historical-data?days=${this.currentDays}${symbolParam}`),
                this.fetchData(`/indicators?days=${this.currentDays}${symbolParam}`),
                this.fetchData(`/statistics?symbol=${this.currentSymbol}`),
                this.fetchData(`/forecasts?model=ARIMA${symbolParam}`),
                this.fetchData(`/forecasts?model=Prophet${symbolParam}`),
                this.fetchData(`/forecasts?model=LSTM${symbolParam}`),
                this.fetchData(`/sentiment?days=90${symbolParam}`)
            ]);

            this.data = {
                historical,
                indicators,
                stats,
                forecasts: { ARIMA: arima, Prophet: prophet, LSTM: lstm },
                sentiment
            };

            const name = this.getFriendlyName();
            window.charts.renderAll(this.data, name, this.getActiveIndicators());
            this.updateStatsUI();
            this.updateRefreshTime();
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        } finally {
            this.showLoading(false);
        }
    }

    async fetchData(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) throw new Error(`API error: ${response.statusText}`);
        return await response.json();
    }

    async refreshData() {
        await this.loadAllData();
    }

    updateRefreshTime() {
        const el = document.getElementById('last-refresh-time');
        if (!el) return;
        const now = new Date();
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        el.textContent = `${h}:${m}:${s}`;
    }

    refreshSpecificChart(target) {
        const name = this.getFriendlyName();
        if (target === 'main') {
            window.charts.renderMainPriceChart(this.data.historical, name, this.data.forecasts);
        } else if (target === 'full') {
            window.charts.updateFullChart(this.data, name, this.getActiveIndicators());
        } else if (target === 'comparison') {
            window.charts.renderComparisonChart(this.data.historical, name, this.data.forecasts);
        }
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    updateStatsUI() {
        const stats = this.data.stats;
        this.updateAllTitles();
        if (!stats.latest_price) return;
        document.getElementById('price-val').innerText = this.formatCurrency(stats.latest_price);
        const changeVal = document.getElementById('price-change-val');
        const change = stats.change_24h.toFixed(2);
        changeVal.innerText = `${change > 0 ? '+' : ''}${change}%`;
        changeVal.className = `trend ${change >= 0 ? 'up' : 'down'}`;
        document.getElementById('high-52w-val').innerText = this.formatCurrency(stats.high_52w);
        document.getElementById('low-52w-val').innerText = this.formatCurrency(stats.low_52w);
        const vol = stats.avg_volume / 1e9;
        document.getElementById('volume-val').innerText = `${vol.toFixed(1)}B`;

        ['ARIMA', 'Prophet', 'LSTM'].forEach(model => {
            const forecast = this.data.forecasts[model] || [];
            const miniEl = document.getElementById(`${model.toLowerCase()}-pred-mini`);
            const mainEl = document.getElementById(`${model.toLowerCase()}-pred-main`);
            if (forecast.length > 0) {
                const latestPred = forecast[forecast.length - 1].predicted_price;
                const formatted = this.formatCurrency(latestPred);
                if (miniEl) miniEl.innerText = formatted;
                if (mainEl) mainEl.innerText = formatted;
            } else {
                if (miniEl) miniEl.innerText = "Training...";
                if (mainEl) mainEl.innerText = "Model Training...";
            }
        });

        if (this.data.sentiment.length > 0) {
            const latest = this.data.sentiment[0];
            const scoreEl = document.getElementById('sentiment-score-main');
            if (scoreEl) scoreEl.innerText = `Score: ${latest.score}`;
            const labelEl = document.getElementById('sentiment-label-main');
            if (labelEl) {
                labelEl.innerText = latest.sentiment_label;
                labelEl.style.color = latest.sentiment_label === 'Bullish' ? 'var(--accent-green)' :
                    latest.sentiment_label === 'Bearish' ? 'var(--accent-red)' : 'var(--accent-blue)';
            }
        }
    }

    updateUI() { }
}

document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
});
