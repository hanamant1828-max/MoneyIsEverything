
const usernameElement = document.getElementById('username');
const logoutBtn = document.getElementById('logoutBtn');
const historyTableBody = document.getElementById('historyTableBody');
const detailModal = document.getElementById('detailModal');
const closeModal = document.getElementById('closeModal');
const modalBody = document.getElementById('modalBody');

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

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        if (!response.ok) {
            throw new Error('Failed to load history');
        }
        
        const data = await response.json();
        renderHistory(data.history);
    } catch (err) {
        console.error('Error loading history:', err);
        historyTableBody.innerHTML = '<tr><td colspan="6" class="error-cell">Error loading history</td></tr>';
    }
}

function renderHistory(history) {
    if (history.length === 0) {
        historyTableBody.innerHTML = '<tr><td colspan="6" class="no-data-cell">No detection history found</td></tr>';
        return;
    }
    
    historyTableBody.innerHTML = history.map(item => `
        <tr>
            <td>${item.id}</td>
            <td><img src="data:image/jpeg;base64,${item.image_data}" alt="Currency" class="history-thumbnail"></td>
            <td><span class="result-badge ${item.result.toLowerCase()}">${item.result}</span></td>
            <td>${item.confidence}%</td>
            <td>${new Date(item.timestamp).toLocaleString()}</td>
            <td><button class="view-btn" onclick="viewDetails(${item.id})">View Details</button></td>
        </tr>
    `).join('');
}

async function viewDetails(historyId) {
    try {
        const response = await fetch(`/api/history/${historyId}`);
        if (!response.ok) {
            throw new Error('Failed to load details');
        }
        
        const data = await response.json();
        
        modalBody.innerHTML = `
            <div class="detail-content">
                <img src="data:image/jpeg;base64,${data.image_data}" alt="Currency" class="detail-image">
                <div class="detail-info">
                    <p><strong>ID:</strong> ${data.id}</p>
                    <p><strong>Result:</strong> <span class="result-badge ${data.result.toLowerCase()}">${data.result}</span></p>
                    <p><strong>Confidence:</strong> ${data.confidence}%</p>
                    <p><strong>Date & Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                    <div class="detail-explanation">
                        <strong>Analysis:</strong>
                        <pre>${data.explanation}</pre>
                    </div>
                </div>
            </div>
        `;
        
        detailModal.style.display = 'block';
    } catch (err) {
        console.error('Error loading details:', err);
        alert('Failed to load details');
    }
}

closeModal.addEventListener('click', () => {
    detailModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === detailModal) {
        detailModal.style.display = 'none';
    }
});

fetchUser();
loadHistory();
