// TerraMind AI Sustainability Coach Chat Interface (Supabase-connected)
(function() {
    const chatContainer = document.querySelector('.overflow-y-auto');
    const messageInput = document.querySelector('footer input[type="text"]');
    const sendButton = document.querySelector('footer button.bg-primary');
    const quickActions = document.querySelectorAll('footer .flex-wrap button');
    
    if (!chatContainer || !messageInput || !sendButton) return;

    // Helper: Scroll to bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Helper: Format timestamp to hh:mm AM/PM
    function formatTime(timestampStr) {
        try {
            const date = timestampStr ? new Date(timestampStr) : new Date();
            let hours = date.getHours();
            let minutes = date.getMinutes();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            minutes = minutes < 10 ? '0' + minutes : minutes;
            return `${hours}:${minutes} ${ampm}`;
        } catch(e) {
            return "Just Now";
        }
    }

    // Append a user message to the chat
    function defUserMsg(text, timestamp = null) {
        const timeStr = formatTime(timestamp);
        const msgDiv = document.createElement('div');
        msgDiv.className = "flex flex-col items-end gap-2 ml-auto max-w-[85%]";
        msgDiv.innerHTML = `
            <div class="p-4 rounded-2xl rounded-tr-none bg-primary/10 border border-primary/20">
                <p class="text-body-md text-on-surface leading-relaxed">${text}</p>
            </div>
            <span class="text-[10px] text-on-surface-variant mr-1">YOU • ${timeStr}</span>
        `;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    // Append an AI coach message to the chat
    function defAICoachMsg(text, timestamp = null) {
        const timeStr = formatTime(timestamp);
        const msgDiv = document.createElement('div');
        msgDiv.className = "flex flex-col items-start gap-2 max-w-[85%]";
        
        msgDiv.innerHTML = `
            <div class="p-4 rounded-2xl rounded-tl-none bg-surface-glass border border-primary/30 shadow-[0_0_15px_rgba(66,225,137,0.1)]">
                <p class="text-body-md text-on-surface leading-relaxed">${text}</p>
            </div>
            <span class="text-[10px] text-on-surface-variant ml-1">COACH TERRA • ${timeStr}</span>
        `;
        chatContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    // Show typing state
    let typingIndicator = null;
    function showTypingIndicator() {
        if (typingIndicator) return;
        
        typingIndicator = document.createElement('div');
        typingIndicator.className = "flex flex-col items-start gap-2 max-w-[85%] animate-pulse";
        typingIndicator.innerHTML = `
            <div class="p-4 rounded-2xl rounded-tl-none bg-surface-glass border border-primary/20">
                <p class="text-body-md text-primary font-bold">Coach Terra is thinking...</p>
            </div>
        `;
        chatContainer.appendChild(typingIndicator);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        if (typingIndicator) {
            chatContainer.removeChild(typingIndicator);
            typingIndicator = null;
        }
    }

    // Load Chat History from Database
    function loadChatHistory() {
        fetch('/api/aicoach/chat')
            .then(res => res.json())
            .then(messages => {
                if (messages.length > 0) {
                    // Clear static elements
                    chatContainer.innerHTML = '';
                    messages.forEach(msg => {
                        if (msg.sender === 'user') {
                            defUserMsg(msg.message, msg.created_at);
                        } else {
                            defAICoachMsg(msg.message, msg.created_at);
                        }
                    });
                }
            })
            .catch(err => console.warn("Failed to load chat history:", err));
    }

    // Send user message and get dynamic AI response
    function sendChatMessage(text) {
        defUserMsg(text);
        showTypingIndicator();
        
        fetch('/api/aicoach/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(res => res.json())
        .then(data => {
            removeTypingIndicator();
            if (data.reply) {
                defAICoachMsg(data.reply);
            }
        })
        .catch(err => {
            console.error("AI Coach connection error:", err);
            removeTypingIndicator();
            defAICoachMsg("I'm having trouble connecting to the TerraMind cloud database right now. Let's try again in a bit.");
        });
    }

    // Send handlers
    function handleSend() {
        const text = messageInput.value.trim();
        if (!text) return;
        
        messageInput.value = "";
        sendChatMessage(text);
    }

    sendButton.addEventListener('click', handleSend);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Quick Action button listeners
    quickActions.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.textContent.trim();
            sendChatMessage(text);
        });
    });

    // Load history and scroll
    loadChatHistory();
    scrollToBottom();
})();
