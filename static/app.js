// 🔐 Secure LAN Chat - Client-side Logic

let currentMode = 'server';
let eventSource = null;

// Initialize SSE connection
function initEventSource() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('/stream');

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === 'status') {
            updateStatus(data.data);
        } else if (data.type === 'message') {
            addMessage(data.data);
        }
    };

    eventSource.onerror = function (error) {
        console.error('SSE Error:', error);
    };
}

// Mode Selection
function selectMode(mode) {
    currentMode = mode;

    document.getElementById('serverModeBtn').classList.toggle('active', mode === 'server');
    document.getElementById('clientModeBtn').classList.toggle('active', mode === 'client');

    document.getElementById('serverForm').classList.toggle('hidden', mode !== 'server');
    document.getElementById('clientForm').classList.toggle('hidden', mode !== 'client');
}

// Start Server
async function startServer() {
    const port = document.getElementById('serverPort').value;

    const response = await fetch('/api/start_server', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ port: parseInt(port) })
    });

    const result = await response.json();

    if (result.success) {
        document.getElementById('connectionPanel').style.display = 'none';
        initEventSource();
    } else {
        alert('Erreur: ' + result.error);
    }
}

// Connect to Peer
async function connectToPeer() {
    const ip = document.getElementById('peerIp').value.trim();
    const port = document.getElementById('peerPort').value;

    if (!ip) {
        alert('Veuillez entrer une adresse IP');
        return;
    }

    const response = await fetch('/api/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, port: parseInt(port) })
    });

    const result = await response.json();

    if (result.success) {
        document.getElementById('connectionPanel').style.display = 'none';
        initEventSource();
    } else {
        alert('Erreur: ' + result.error);
    }
}

// Update Status
function updateStatus(data) {
    const statusText = document.getElementById('statusText');
    const statusIndicator = document.getElementById('statusIndicator');

    statusText.textContent = data.status;

    // Update indicator
    statusIndicator.classList.remove('secure', 'connecting');

    if (data.is_secure) {
        statusIndicator.classList.add('secure');

        // Show security panel and chat
        document.getElementById('securityPanel').classList.remove('hidden');
        document.getElementById('chatContainer').classList.remove('hidden');
        document.getElementById('disconnectArea').classList.remove('hidden');

        // Update fingerprint
        if (data.fingerprint) {
            document.getElementById('fingerprint').textContent = data.fingerprint;
        }
    } else if (data.status.includes('...')) {
        statusIndicator.classList.add('connecting');
    }
}

// Send Message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();

    if (!text) return;

    const response = await fetch('/api/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });

    const result = await response.json();

    if (result.success) {
        input.value = '';
        input.focus();
    } else {
        alert('Erreur: ' + result.error);
    }
}

// Add Message to UI
function addMessage(msgData) {
    const messagesDiv = document.getElementById('messages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${msgData.from === 'Moi' ? 'own' : 'other'}`;

    messageDiv.innerHTML = `
        <div class="message-header">
            <strong>${msgData.from}</strong>
            <span>${msgData.time}</span>
        </div>
        <div class="message-bubble">${escapeHtml(msgData.text)}</div>
    `;

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Handle Enter Key
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Disconnect
async function disconnect() {
    await fetch('/api/disconnect', { method: 'POST' });

    if (eventSource) {
        eventSource.close();
        eventSource = null;
    }

    // Reset UI - Ensure connection panel is visible
    const connectionPanel = document.getElementById('connectionPanel');
    if (connectionPanel) {
        connectionPanel.style.display = 'block';
        connectionPanel.classList.remove('hidden');
    }

    document.getElementById('securityPanel').classList.add('hidden');
    document.getElementById('chatContainer').classList.add('hidden');
    document.getElementById('disconnectArea').classList.add('hidden');
    document.getElementById('messages').innerHTML = '';

    // Reset status
    document.getElementById('statusText').textContent = 'Non connecté';
    document.getElementById('statusIndicator').classList.remove('secure', 'connecting');
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load initial state on page load
window.addEventListener('load', async () => {
    const response = await fetch('/api/state');
    const state = await response.json();

    if (state.is_secure) {
        // Already connected, restore UI
        updateStatus(state);
        state.messages.forEach(msg => addMessage(msg));
        document.getElementById('connectionPanel').style.display = 'none';
        initEventSource();
    }
});
