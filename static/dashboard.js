
const usernameElement = document.getElementById('username');
const logoutBtn = document.getElementById('logoutBtn');

async function fetchUser() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const data = await response.json();
            usernameElement.textContent = `Welcome, ${data.username}`;
        } else {
            window.location.href = '/login';
        }
    } catch (err) {
        console.error('Error fetching user:', err);
        window.location.href = '/login';
    }
}

logoutBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (err) {
        console.error('Error logging out:', err);
    }
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard-stats');
        if (!response.ok) {
            throw new Error('Failed to load dashboard stats');
        }
        
        const data = await response.json();
        
        document.getElementById('totalChecks').textContent = data.total;
        document.getElementById('realCount').textContent = data.real_count;
        document.getElementById('fakeCount').textContent = data.fake_count;
        
        renderChart(data.real_count, data.fake_count);
        renderRecentDetections(data.recent);
    } catch (err) {
        console.error('Error loading dashboard stats:', err);
    }
}

function renderChart(realCount, fakeCount) {
    const canvas = document.getElementById('statsChart');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 400;
    canvas.height = 200;
    
    const total = realCount + fakeCount;
    if (total === 0) {
        ctx.fillStyle = '#666';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    const barWidth = 80;
    const maxHeight = 150;
    const maxValue = Math.max(realCount, fakeCount);
    
    const realHeight = (realCount / maxValue) * maxHeight;
    const fakeHeight = (fakeCount / maxValue) * maxHeight;
    
    ctx.fillStyle = '#4CAF50';
    ctx.fillRect(100, maxHeight - realHeight + 30, barWidth, realHeight);
    
    ctx.fillStyle = '#f44336';
    ctx.fillRect(220, maxHeight - fakeHeight + 30, barWidth, fakeHeight);
    
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('REAL', 140, maxHeight + 50);
    ctx.fillText('FAKE', 260, maxHeight + 50);
    
    ctx.fillText(realCount.toString(), 140, maxHeight - realHeight + 20);
    ctx.fillText(fakeCount.toString(), 260, maxHeight - fakeHeight + 20);
}

function renderRecentDetections(recent) {
    const container = document.getElementById('recentDetections');
    
    if (recent.length === 0) {
        container.innerHTML = '<p class="no-data">No recent detections</p>';
        return;
    }
    
    container.innerHTML = recent.map(item => `
        <div class="recent-card">
            <img src="data:image/jpeg;base64,${item.image_data}" alt="Currency" class="recent-image">
            <div class="recent-info">
                <div class="recent-result ${item.result.toLowerCase()}">${item.result}</div>
                <div class="recent-confidence">${item.confidence}% confidence</div>
                <div class="recent-time">${new Date(item.timestamp).toLocaleString()}</div>
            </div>
        </div>
    `).join('');
}

fetchUser();
loadDashboardStats();
