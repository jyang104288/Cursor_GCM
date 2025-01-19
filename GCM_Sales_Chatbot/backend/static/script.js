document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const suggestedQuestions = document.getElementById('suggested-questions');

    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to add loading animation
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading';
        loadingDiv.innerHTML = `
            <div></div>
            <div></div>
            <div></div>
            <div></div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return loadingDiv;
    }

    // Function to load suggested questions
    async function loadSuggestedQuestions() {
        try {
            const response = await fetch('/api/suggested-questions');
            const data = await response.json();

            if (data.status === 'success') {
                suggestedQuestions.innerHTML = ''; // Clear loading message
                
                // Add each question as a clickable button
                data.questions.forEach(question => {
                    const questionButton = document.createElement('button');
                    questionButton.className = 'w-full text-left p-2 rounded hover:bg-blue-50 transition-colors text-sm text-gray-700';
                    questionButton.textContent = question;
                    
                    // Add click handler to send the question
                    questionButton.addEventListener('click', () => {
                        userInput.value = question;
                        chatForm.dispatchEvent(new Event('submit'));
                    });
                    
                    suggestedQuestions.appendChild(questionButton);
                });
            } else {
                suggestedQuestions.innerHTML = '<div class="text-red-500">Failed to load suggested questions</div>';
            }
        } catch (error) {
            console.error('Error loading suggested questions:', error);
            suggestedQuestions.innerHTML = '<div class="text-red-500">Failed to load suggested questions</div>';
        }
    }

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Clear input
        userInput.value = '';

        // Add user message to chat
        addMessage(message, true);

        // Add loading indicator
        const loadingIndicator = addLoadingIndicator();

        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();

            // Remove loading indicator
            loadingIndicator.remove();

            if (data.status === 'success') {
                // Add bot response to chat
                addMessage(data.response);
            } else {
                // Add error message
                addMessage('Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            // Remove loading indicator
            loadingIndicator.remove();
            
            // Add error message
            addMessage('Sorry, I encountered an error. Please try again.');
            console.error('Error:', error);
        }
    });

    // Add initial greeting
    addMessage('Hello! I\'m your GCM Sales Assistant. How can I help you today?');

    // Load suggested questions
    loadSuggestedQuestions();
}); 