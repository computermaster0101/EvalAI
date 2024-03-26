var socket = io.connect()
const sendButton = document.getElementById('send-btn')
const resetButton = document.getElementById('reset-btn')
const chatClaude = document.getElementById('chat-messages1')
const chatGemini = document.getElementById('chat-messages2')
const chatOpenai = document.getElementById('chat-messages3')
const messageInput = document.getElementById('message-input');
const tempInput = document.getElementById('temp')
const topPInput = document.getElementById('top_p')
const maxTokenInput = document.getElementById('max_token')
const systemPromptInput = document.getElementById('paragraphInput')

// Function to add a message to the chat interfaces
function addMessage(sender, message, className) {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<p><strong>${sender}:</strong> ${message}</p>`;
    if (className) {
        messageElement.classList.add(className);
    }
    if (sender === 'You' || sender === 'Echo' || sender === 'Server') {
        const chatClaudeMessage = messageElement.cloneNode(true);
        const chatGeminiMessage = messageElement.cloneNode(true);
        const chatOpenaiMessage = messageElement.cloneNode(true);

        chatClaude.appendChild(chatClaudeMessage);
        chatGemini.appendChild(chatGeminiMessage);
        chatOpenai.appendChild(chatOpenaiMessage);
        
        // Scroll to bottom for each chat box
        chatClaude.scrollTop = chatClaude.scrollHeight;
        chatGemini.scrollTop = chatGemini.scrollHeight;
        chatOpenai.scrollTop = chatOpenai.scrollHeight;

    } else if (sender === 'OpenAI') {
        const chatOpenaiMessage = messageElement.cloneNode(true);
        chatOpenai.appendChild(chatOpenaiMessage);
        chatOpenai.scrollTop = chatOpenai.scrollHeight;
    } else if (sender === 'Claude') {
        const chatClaudeMessage = messageElement.cloneNode(true);
        chatClaude.appendChild(chatClaudeMessage);
        chatClaude.scrollTop = chatClaude.scrollHeight;
    } else if (sender === 'Gemini') {
        const chatGeminiMessage = messageElement.cloneNode(true);
        chatGemini.appendChild(chatGeminiMessage);
        chatGemini.scrollTop = chatGemini.scrollHeight;
    }
}


// Function to handle sending a message
function sendMessage() {
    const message = messageInput.value.trim();
    const temp = tempInput.value;
    const top_p = topPInput.value;
    const max_token = maxTokenInput.value;
    const system_prompt = systemPromptInput.value;

    if (message !== '') {
        addMessage('You', message);
        messageInput.value = '';
        socket.emit('request', {message: message, temp: temp, top_p: top_p, max_tokens: max_token, system_prompt: system_prompt});
    }
}

// Function to clear chat messages
function resetChats() {
    chatClaude.innerHTML = "<strong>Claude:</strong> Hello! "; // Clear chat messages
    chatGemini.innerHTML = "<strong>Gemini:</strong> Hello! "; // Clear chat messages
    chatOpenai.innerHTML = "<strong>OpenAI:</strong> Hello! "; // Clear chat messages
    socket.emit('reset')
}

// Listen for the thinking and reply responses from the backend
socket.on('thinking', function(response){
    addMessage('Server', `${response.response} <span class="spinner"></span>`, 'thinking-message');
});

socket.on('reply', function(response){
    // Remove the thinking message
    removeThinkingMessage(response.llm);
    // Display the response in the chat interface
    addMessage(response.llm, response.response);
});

// Function to remove the thinking message
function removeThinkingMessage(llm) {
    if (llm === 'Claude') {
        const thinkingMessagesClaude = chatClaude.getElementsByClassName('thinking-message');
        while (thinkingMessagesClaude.length > 0) {
            thinkingMessagesClaude[0].remove();
        }
    } else if (llm === 'Gemini') {
        const thinkingMessagesGemini = chatGemini.getElementsByClassName('thinking-message');
        while (thinkingMessagesGemini.length > 0) {
            thinkingMessagesGemini[0].remove();
        }
    } else if (llm === 'OpenAI') {
        const thinkingMessagesOpenAI = chatOpenai.getElementsByClassName('thinking-message');
        while (thinkingMessagesOpenAI.length > 0) {
            thinkingMessagesOpenAI[0].remove();
        }
    }
}

  

function openPrompt() {
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
}

function hidePopup() {
    var paragraph = document.getElementById('paragraphInput').value;
    // Do something with the entered paragraph
    console.log(paragraph); // Example: Log it to console

    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
}

sendButton.addEventListener('click',sendMessage)
resetButton.addEventListener('click', resetChats)
messageInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      sendMessage();
    }
  });