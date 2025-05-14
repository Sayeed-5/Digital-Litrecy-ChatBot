document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const chatIcon = document.getElementById('chat-icon');
    const chatWindow = document.getElementById('chat-window');
    const minimizeBtn = document.getElementById('minimize-btn');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');
    const aiToggle = document.getElementById('ai-toggle');
    
    // State variables
    let useAI = false;
    
    // Initialize AI toggle based on server config
    if (aiToggle) {
        // Get the initial state from the data attribute (set by the server)
        const aiEnabledFromServer = aiToggle.getAttribute('data-ai-enabled') === 'true';
        aiToggle.checked = aiEnabledFromServer;
        useAI = aiEnabledFromServer;
    }
    
    // Event Listeners
    chatIcon.addEventListener('click', toggleChatWindow);
    minimizeBtn.addEventListener('click', toggleChatWindow);
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', function() {
            chatInput.value = this.textContent;
            sendMessage();
        });
    });
    
    aiToggle.addEventListener('change', function() {
        useAI = this.checked;
        console.log('AI toggle changed to:', useAI); // Debug log
    });
    
    // Functions
    function toggleChatWindow() {
        if (chatWindow.style.display === 'flex') {
            chatWindow.style.display = 'none';
            chatIcon.style.display = 'flex';
        } else {
            chatWindow.style.display = 'flex';
            chatIcon.style.display = 'none';
        }
    }
    
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addUserMessage(message);
        chatInput.value = '';
        
        // Show loading indicator
        showLoading();
        
        console.log('Sending message with AI:', useAI); // Debug log
        
        // Send to backend
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: message,
                use_ai: useAI
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            removeLoading();
            
            // Add bot response
            addBotMessage(data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            removeLoading();
            addBotMessage('Sorry, I encountered an error. Please try again later.');
        });
    }
    
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user';
        messageElement.innerHTML = `<div class="message-content">${escapeHTML(message)}</div>`;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot';
        
        // Format message with line breaks and lists
        message = formatMessage(message);
        
        messageElement.innerHTML = `<div class="message-content">${message}</div>`;
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    function formatMessage(message) {
        // Convert numbered lists (1. Item) to HTML lists
        message = message.replace(/(\d+\.\s[^\n]+)(?:\n|$)/g, '<li>$1</li>');
        if (message.includes('<li>')) {
            message = '<ol>' + message + '</ol>';
        }
        
        // Convert line breaks to <br>
        message = message.replace(/\n/g, '<br>');
        
        return message;
    }
    
    function showLoading() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'message bot loading';
        loadingElement.id = 'loading-indicator';
        loadingElement.innerHTML = `
            <div class="message-content">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        chatMessages.appendChild(loadingElement);
        scrollToBottom();
    }
    
    function removeLoading() {
        const loadingElement = document.getElementById('loading-indicator');
        if (loadingElement) {
            loadingElement.remove();
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function escapeHTML(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
