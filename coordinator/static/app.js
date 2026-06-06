document.addEventListener('DOMContentLoaded', () => {
    const btnStandard = document.getElementById('btn-standard');
    const btnSemi = document.getElementById('btn-semi');
    const btnDemoPrune = document.getElementById('btn-demo-prune');
    
    // Standard elements
    const stdBytes = document.getElementById('std-bytes');
    const stdTime = document.getElementById('std-time');
    
    // Semi elements
    const semiBytes = document.getElementById('semi-bytes');
    const semiTime = document.getElementById('semi-time');
    
    // Comparison
    const compBandwidth = document.getElementById('comp-bandwidth');
    const compSpeed = document.getElementById('comp-speed');
    
    // Results
    const totalResultsBadge = document.getElementById('total-results-badge');
    const resultsBody = document.getElementById('results-body');

    let metrics = {
        standard: null,
        semi: null
    };

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function formatTime(seconds) {
        return seconds.toFixed(3) + ' s';
    }

    function updateComparison() {
        if (metrics.standard && metrics.semi) {
            const bytesSaved = metrics.standard.bytesTransferred - metrics.semi.bytesTransferred;
            const reduction = (bytesSaved / metrics.standard.bytesTransferred) * 100;
            compBandwidth.textContent = `${reduction.toFixed(2)}% (${formatBytes(bytesSaved)})`;

            const speedup = metrics.standard.executionTime / metrics.semi.executionTime;
            compSpeed.textContent = `${speedup.toFixed(2)}x faster`;
        }
    }

    function renderTable(results, totalCount) {
        totalResultsBadge.textContent = `${totalCount} Results Found`;
        resultsBody.innerHTML = '';
        
        if (!results || results.length === 0) {
            resultsBody.innerHTML = '<tr><td colspan="5" class="empty-state">No results found.</td></tr>';
            return;
        }

        results.forEach(emp => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${emp.EmpID}</td>
                <td>${emp.Name}</td>
                <td>${emp.Department}</td>
                <td>${emp.Email}</td>
                <td>$${emp.Salary.toLocaleString()}</td>
            `;
            resultsBody.appendChild(tr);
        });
    }

    async function runQuery(type) {
        const isStandard = type === 'standard';
        const isDemo = type === 'demo';
        const btn = isStandard ? btnStandard : (isDemo ? btnDemoPrune : btnSemi);
        const bytesEl = isStandard ? stdBytes : semiBytes;
        const timeEl = isStandard ? stdTime : semiTime;
        let url = isStandard ? '/api/run-standard' : '/api/run-semi-join';
        if (isDemo) url = '/api/run-semi-join-demo?prefix=EMP09';

        // Set Loading state
        const originalText = btn.textContent;
        btn.innerHTML = '<span class="loader"></span> Running...';
        btnStandard.disabled = true;
        btnSemi.disabled = true;
        if(btnDemoPrune) btnDemoPrune.disabled = true;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (data.error) {
                alert("Error: " + data.error);
                return;
            }

            // Update metrics
            if (isStandard) {
                metrics.standard = data.metrics;
            } else {
                metrics.semi = data.metrics;
            }

            bytesEl.textContent = formatBytes(data.metrics.bytesTransferred);
            timeEl.textContent = formatTime(data.metrics.executionTime);

            renderTrace(data.trace);
            renderCostAnalysis(data.cost_analysis);
            renderTable(data.results, data.metrics.resultCount);
            updateComparison();

        } catch (err) {
            alert("An error occurred: " + err.message);
        } finally {
            // Restore state
            btn.innerHTML = originalText;
            btnStandard.disabled = false;
            btnSemi.disabled = false;
            if(btnDemoPrune) btnDemoPrune.disabled = false;
        }
    }

    function renderTrace(trace) {
        const container = document.getElementById('trace-container');
        container.innerHTML = '';
        trace.forEach(item => {
            const step = document.createElement('div');
            const typeClass = item.type ? `trace-step--${item.type}` : '';
            step.className = `trace-step ${typeClass}`;
            step.innerHTML = `
                <div class="step-num">${item.step}</div>
                <div class="step-content">
                    <p>${item.desc}</p>
                    <div class="step-meta">
                        <span>Site: ${item.site}</span> | <span>Cost: ${item.cost}</span>
                    </div>
                </div>
            `;
            container.appendChild(step);
        });
    }

    function renderCostAnalysis(analysis) {
        const container = document.getElementById('cost-container');
        container.innerHTML = `
            <div class="formula-box">${analysis.formula}</div>
            <div class="cost-calculation">
                <p><strong>Parameters:</strong></p>
                <ul>
                    <li>C_msg (Latency): ${analysis.c_msg} ms</li>
                    <li>C_tr (Bandwidth): ${analysis.c_tr} ms/byte</li>
                    <li>#msgs (Messages): ${analysis.msgs}</li>
                    <li>#bytes (Total): ${analysis.bytes.toLocaleString()} bytes</li>
                </ul>
                <hr style="margin: 1rem 0; opacity: 0.1;">
                <p style="color: #60a5fa; font-weight: 600;">
                    Comm Cost = (${analysis.c_msg} * ${analysis.msgs}) + (${analysis.c_tr} * ${analysis.bytes.toLocaleString()})
                </p>
                <p style="font-size: 1.1rem; margin-top: 0.5rem;">
                    = <span style="color: #10b981;">${analysis.calculated_comm_cost.toFixed(2)} ms</span>
                </p>
            </div>
        `;
    }

    btnStandard.addEventListener('click', () => runQuery('standard'));
    btnSemi.addEventListener('click', () => runQuery('semi'));
    if(btnDemoPrune) btnDemoPrune.addEventListener('click', () => runQuery('demo'));
});
