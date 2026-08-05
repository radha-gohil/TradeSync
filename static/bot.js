let prompt = document.querySelector("#prompt"); // Ensure input has id="prompt"
let chatContainer = document.querySelector(".chat-container");
let imageBtn = document.querySelector("#image");
let imageInput = document.querySelector("#image input");

let sendButton = document.querySelector("#sendButton"); // Ensure button has id="sendButton"

const API_KEY= ""
const API_URL = ``;

let user = {
    message: null,
    file: {
        mime_type: null,
        data: null
    }
};

// Function to fetch AI response
async function generateResponse(aiChatBox) {
    let text = aiChatBox.querySelector(".ai-chat-area");
    let parts = [{ text: user.message }];

    if (user.file.data) {
        parts.push({ inline_data: user.file });
    }

    let requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contents: [{ parts: parts }] })
    };

    try {
        let response = await fetch(API_URL, requestOptions);
        let data = await response.json();

        if (data.candidates && data.candidates.length > 0) {
            let apiResponse = data.candidates[0].content.parts[0].text.trim();
            
            // Formatting AI Response
            let formattedResponse = apiResponse
                .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>") // Convert **bold** to <b>
                .replace(/\n/g, "<br>") // Preserve line breaks
                .replace(/\*/g, "• "); // Convert *bullets* to list format

            text.innerHTML = formattedResponse;
        } else {
            text.innerHTML = "Error: No response from AI.";
        }
    } catch (error) {
        console.error(error);
        text.innerHTML = "Error: Unable to generate response.";
    } finally {
        scrollToBottom(); // Ensure chat scrolls down after response
        user.file = { mime_type: null, data: null }; // Reset file after sending
    }
}

// Function to create chat message boxes
function createChatBox(html, classes) {
    let div = document.createElement("div");
    div.innerHTML = html;
    div.classList.add(classes);
    return div;
}

// Function to handle user input and AI response
function handleChatResponse(message) {
    if (!message && !user.file.data) return; // Prevent empty messages
    user.message = message;

    let userHtml = `
    <div class="user-chat-box">
        <img src="static/images/human.jpeg" alt="User" id="userImage" width="50">
        <div class="user-chat-area">
            ${user.message ? user.message : ""}
            ${user.file.data ? `<img src="data:${user.file.mime_type};base64,${user.file.data}" class="chooseimg"/>` : ""}
        </div>
    </div>
    `;

    let userChatBox = createChatBox(userHtml, "user-chat-box");
    chatContainer.appendChild(userChatBox);
    scrollToBottom();

    let aiHtml = `
        <div class="ai-chat-box">
            <img src="static/images/bot.jpg" alt="AI" id="aiImage" width="50">
            <div class="ai-chat-area">Thinking...</div>
        </div>
    `;

    let aiChatBox = createChatBox(aiHtml, "ai-chat-box");
    chatContainer.appendChild(aiChatBox);

    setTimeout(() => {
        generateResponse(aiChatBox);
    }, 1000);
}

// Function to ensure chat auto-scrolls down
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Event listener for Enter key to send messages
prompt.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && prompt.value.trim() !== "") {
        handleChatResponse(prompt.value.trim());
        prompt.value = ""; // Clear input after sending
    }
});

// Event listener for send button click
sendButton.addEventListener("click", () => {
    if (prompt.value.trim() !== "") {
        handleChatResponse(prompt.value.trim());
        prompt.value = ""; // Clear input after sending
    }
});

// Event listener for image input
imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (!file) return;

    let reader = new FileReader();
    reader.onload = (e) => {
        let base64string = e.target.result.split(",")[1];
        user.file = {
            mime_type: file.type,
            data: base64string
        };
        handleChatResponse(""); // Trigger AI response after image upload
    };
    reader.readAsDataURL(file);
});

// Open file selection when image button is clicked
imageBtn.addEventListener("click", () => {
    imageInput.click();
});
