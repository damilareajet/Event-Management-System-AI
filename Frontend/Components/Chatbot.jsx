import { useState, useRef, useEffect } from 'react';
import { MdOutlineCancel } from 'react-icons/md';
const BOT_NAME = "Sam";
const PERSON_NAME = "You";

const Chatbot = () => {
const [isVisible, setIsVisible] = useState(false);  
const toggleChat = () => {  
    setIsVisible(!isVisible);  
};

// State to manage chat messages and input value
const [messages, setMessages] = useState([]);
const [inputValue, setInputValue] = useState('');
const messagesEndRef = useRef(null); // Create a ref for the messages end

// Function to scroll to the bottom of messages
const scrollToBottom = () => {
    if (messagesEndRef.current) {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
};

// useEffect to scroll to bottom whenever messages change
useEffect(() => {
    scrollToBottom();
}, [messages]);

// Handles form submission
const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputValue.trim()) return; // Prevent sending empty messages

    // Add user message to chat
    setMessages(prevMessages => [
    ...prevMessages,
    { name: PERSON_NAME, side: 'right', text: inputValue }
    ]);

    // Clear input field
    setInputValue('');

    try {
    // Fetch bot response
    const response = await fetch(`/get?msg=${encodeURIComponent(inputValue)}`);
    const data = await response.text();

    // Add bot response to chat
    setMessages(prevMessages => [
        ...prevMessages,
        { name: BOT_NAME, side: 'left', text: data }
    ]);
    } catch (error) {
    console.error('Error fetching bot response:', error);
    // Handle the error here, e.g., show an error message to the user
    }
};

return (
    <div className="container">
    <div className="chatbox">
        {isVisible && (
        <div className="chatbox__support">
            <header className="chatbox__header">
            <div className="chatbox__image--header">
                <img src="/circled-user-female-skin-type-5--v1.png" alt="Chat Icon"/>
            </div>
            <div className="chatbox__content--header">
                <h4 className="chatbox__heading--header">Chat support</h4>
                <div className='flex space-x-9'>
                <p className="chatbox__description--header">Hi. My name is Sam. How can I help you?</p>  
                <div className="text-white flex justify-center">
                    <MdOutlineCancel className='cursor-pointer' onClick={toggleChat} style={{ fontSize: 36 }}/>    
                </div> 
                </div>
            </div>
            </header>

            <main className="chatbox__messages">
            {messages.map((msg, index) => (
                <div key={index} className={`msg ${msg.side}-msg`}>
                <div className="msg-bubble">
                    <div className="msg-info">
                    <div className="msg-info-name">{msg.name}</div>
                    <div className="msg-info-time">{new Date().toLocaleTimeString()}</div>
                    </div>
                    <div className="msg-text">{msg.text}</div>
                </div>
                </div>
            ))}
            {/* Reference to scroll to the bottom */}
            <div ref={messagesEndRef} />
            </main>

            <form className="chatbox__footer" onSubmit={handleSubmit}>
            <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter your message..."
            />
            <button type="submit" className="send__button">Send</button>
            </form>
        </div>
        )}
        
        <div className="chatbox__button">
        <button onClick={toggleChat}>  
            <img src="/chatbox-icon.svg" className='chatbot_icon' alt="Chatbox Icon"/>  
        </button>  
        </div>
    </div>
    </div>
);
};

export default Chatbot;
