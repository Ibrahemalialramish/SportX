// --- Elements ---
const chatWindow = document.getElementById('chat-window');
const typingIndicator = document.getElementById('typing-indicator');
const userInput = document.getElementById('user-input');
const body = document.body;
const themeIcon = document.getElementById('theme-icon');
const audio = document.getElementById('whistle-sound');

// --- Config ---
// ملاحظة: إذا كان ملف HTML يفتح من نفس السيرفر، يمكنك استخدام مسار نسبي "/chat"
const API_URL = "/chat"; 

// --- Theme Management ---
const savedTheme = localStorage.getItem('theme') || 'dark';
setTheme(savedTheme);

function toggleTheme() {
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (!themeIcon) return; // تأكد من وجود العنصر لتجنب الأخطاء
    
    if (theme === 'dark') {
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    } else {
        themeIcon.classList.replace('fa-sun', 'fa-moon');
    }
}

// --- Interaction Logic ---
// الاستماع لمفتاح Enter
userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessageFromInput();
    }
});

function sendMessageFromInput() {
    const text = userInput.value.trim();
    if (text) {
        sendMessage(text);
        userInput.value = '';
    }
}

function sendQuickMessage(msg) {
    sendMessage(msg);
}

// --- Core Async Messaging ---
async function sendMessage(text) {
    // 1. إضافة رسالة المستخدم للواجهة
    appendMessage(text, 'user-msg');
    
    // 2. إظهار مؤشر الكتابة
    showTyping(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error('Network Error');

        const data = await response.json();
        
        // 3. إخفاء مؤشر الكتابة
        showTyping(false);

        // 4. إضافة رد البوت
        // قمنا بتحسين استلام الرد ليتوافق مع مفتاح "response" في FastAPI
        const botReply = data.response || "عذراً، لم أستطع فهم ذلك.";
        appendMessage(botReply, 'bot-msg');

        // 5. تشغيل صوت الصافرة
        if (audio) {
            audio.currentTime = 0;
            audio.play().catch(e => console.warn("Sound blocked by browser:", e));
        }

    } catch (error) {
        console.error("Fetch Error:", error);
        showTyping(false);
        appendMessage("⚠️ فشل الاتصال بسبورتكس. تأكد من تشغيل ملف main.py", 'bot-msg');
    }
}

// --- UI Helpers ---
function appendMessage(text, className) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', className);
    
    // تحسين عرض النص: تحويل النجوم (Markdown) إلى Bold وحماية النص
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // تحويل **نص** إلى عريض
        .replace(/\n/g, '<br>'); // تحويل السطور الجديدة
        
    msgDiv.innerHTML = formattedText;
    
    // إدخال الرسالة قبل مؤشر الكتابة مباشرة
    chatWindow.insertBefore(msgDiv, typingIndicator);
    
    // التمرير التلقائي للأسفل
    scrollToBottom();
}

function showTyping(show) {
    if (!typingIndicator) return;
    typingIndicator.style.display = show ? 'flex' : 'none';
    if (show) scrollToBottom();
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}