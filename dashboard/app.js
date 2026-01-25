
async function updateDashboard() {
    try {
        const response = await fetch('data.json?t=' + new Date().getTime());
        const data = await response.json();

        // Update Metadata
        const lastUpdated = new Date(data.last_updated);
        document.getElementById('update-time').innerText = lastUpdated.toLocaleTimeString();

        const signals = data.symbols.filter(s => s.status === 'SIGNAL');
        const candidates = data.symbols.filter(s => s.status === 'CANDIDATE');

        document.getElementById('total-count').innerText = data.symbols.length;
        document.getElementById('signal-count').innerText = signals.length;
        document.getElementById('candidate-count').innerText = candidates.length;

        // Update Table
        const tbody = document.getElementById('signal-body');
        tbody.innerHTML = '';

        data.symbols.forEach(item => {
            const tr = document.createElement('tr');

            // Symbol
            const tdSym = document.createElement('td');
            tdSym.innerHTML = `<span class="symbol-name">${item.symbol}</span>`;
            tr.appendChild(tdSym);

            // Price
            const tdPrice = document.createElement('td');
            tdPrice.innerText = item.price.toFixed(2);
            tr.appendChild(tdPrice);

            // VWAP Dist
            const tdVwap = document.createElement('td');
            const vwapDist = ((item.price - item.vwap) / item.vwap * 100).toFixed(2);
            tdVwap.innerText = vwapDist + '%';
            tdVwap.className = vwapDist > 0 ? 'positive' : 'negative';
            tr.appendChild(tdVwap);

            // HOD Dist
            const tdHod = document.createElement('td');
            tdHod.innerText = item.hod_dist.toFixed(2) + '%';
            tdHod.className = item.hod_dist <= 0.5 ? 'positive' : (item.hod_dist <= 1.0 ? 'warning-val' : '');
            tr.appendChild(tdHod);

            // Rel Vol
            const tdVol = document.createElement('td');
            tdVol.innerText = item.rel_vol.toFixed(1) + 'x';
            tdVol.className = item.rel_vol >= 2.0 ? 'positive' : (item.rel_vol >= 1.5 ? 'warning-val' : '');
            tr.appendChild(tdVol);

            // Today's Signals
            const tdCount = document.createElement('td');
            if (item.signals_count > 0) {
                tdCount.innerHTML = `<span class="status-badge status-signal">${item.signals_count}</span> <small>${item.last_signal_time}</small>`;
            } else {
                tdCount.innerText = '-';
            }
            tr.appendChild(tdCount);

            // Score
            const tdScore = document.createElement('td');
            tdScore.innerHTML = `
                <div class="score-bar-bg"><div class="score-bar-inner" style="width: ${item.score}%"></div></div>
                <span>${item.score}</span>
            `;
            tr.appendChild(tdScore);

            // Status
            const tdStatus = document.createElement('td');
            const badgeClass = item.status === 'SIGNAL' ? 'status-signal' : (item.status === 'CANDIDATE' ? 'status-candidate' : 'status-monitoring');
            tdStatus.innerHTML = `<span class="status-badge ${badgeClass}">${item.status}</span>`;
            tr.appendChild(tdStatus);

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error('Error fetching dashboard data:', err);
    }
}

// Initial load
updateDashboard();

// Refresh every 30 seconds
setInterval(updateDashboard, 30000);
