## 🚀 New Features (2025)

### 🌐 Global Smart Device Control (MQTT)
- **Control ESP32 and other IoT devices from anywhere using MQTT.**
- **Public broker support:** Out-of-the-box integration with broker.hivemq.com (no account required for testing).
- **Frontend Smart Devices Panel:** Modern UI panel to add, configure, and control devices (LED on/off, more coming soon).
- **Backend MQTT API:** `/control-device` endpoint lets you send commands to any device/topic via MQTT.
- **ESP32 Sample Code:** Provided for instant device integration—just flash and go!
- **Cloud-to-Home Ready:** Works even when backend is deployed (no need for port forwarding or local IPs).
- **Robust error handling and debug output** for device and network troubleshooting.

### 🛠️ Recent Improvements
- **Unique MQTT client IDs** for all ESP32 connections (prevents disconnect loops).
- **Automatic topic and broker sync** between backend, frontend, and device code.
- **Frontend LED control buttons** for instant device testing.
- **Step-by-step troubleshooting and diagnostics** included in code and docs.

# 🎤 Voice AI Agent - Murf AI Challenge

<div align="center">
  <img src="https://img.shields.io/badge/Voice-AI%20Agent-purple?style=for-the-badge&logo=microphone" alt="Voice AI Agent">
  <img src="https://img.shields.io/badge/Python-Flask-blue?style=for-the-badge&logo=python" alt="Python Flask">
  <img src="https://img.shields.io/badge/AI-Powered-green?style=for-the-badge&logo=openai" alt="AI Powered">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge" alt="Production Ready">
</div>

## 🌟 Project Overview

A **modern, intelligent voice-powered conversational AI agent** that enables natural speech interactions with advanced AI technology. Built as part of the **30 Days of AI Voice Agents Challenge by Murf AI**, this project showcases the seamless integration of Speech-to-Text, Large Language Models, and Text-to-Speech technologies.

### ✨ What Makes This Special

- 🎯 **Single-Button Interface**: Intuitive one-tap recording with visual feedback
- 🧠 **Memory-Enabled Conversations**: Persistent chat sessions with conversation history
- 🎨 **Modern Glass-Morphism UI**: Beautiful, responsive design with smooth animations
- 🔄 **Real-Time Processing**: Live audio streaming with immediate AI responses
- 🛡️ **Production-Ready**: Comprehensive error handling and fallback mechanisms
- 📱 **Cross-Platform**: Works seamlessly on desktop and mobile devices

---

## 🏗️ Architecture & Technologies

### 🔧 **Backend Stack**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AssemblyAI    │    │   Google Gemini │    │     Murf AI     │
│ Speech-to-Text  │───▶│  Large Language │───▶│ Text-to-Speech  │
│                 │    │     Model       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
              ┌─────────────────────────────────────┐
              │           Flask Server              │
              │  • Session Management              │
              │  • Error Handling                  │
              │  • Audio Processing                │
              │  • API Orchestration               │
              └─────────────────────────────────────┘
```

- **🐍 Python Flask**: Lightweight web framework for API orchestration
- **🎯 AssemblyAI**: High-accuracy speech-to-text conversion
- **🧠 Google Gemini 2.5 Flash**: Advanced conversational AI model
- **🎵 Murf AI**: Professional-grade text-to-speech synthesis
- **💾 In-Memory Storage**: Fast session management and chat history

### 🎨 **Frontend Stack**
- **⚡ Vanilla JavaScript**: Lightweight, fast, no framework dependencies
- **🎨 Tailwind CSS**: Utility-first CSS framework for rapid styling
- **🌈 CSS Animations**: Custom keyframes for engaging user interactions
- **📱 Responsive Design**: Mobile-first approach with glass-morphism effects

---

## 🚀 Features
### 🏠 **Smart Devices & IoT**
- **Add, configure, and control smart devices (e.g., ESP32) from the web UI**
- **Global device control via MQTT** (no local network required)
- **Works with public brokers and cloud deployments**
- **Sample ESP32 code included** for instant setup


### 🎙️ **Voice Interaction**
- **One-Touch Recording**: Single button for start/stop with visual feedback
- **Real-Time Audio Processing**: Instant capture and streaming
- **Auto-Play Responses**: Seamless conversation flow
- **Visual Recording Indicators**: Animated pulse rings and color changes

### 🧠 **AI Intelligence**
- **Conversational Memory**: Maintains context across conversation turns
- **Natural Language Understanding**: Powered by Google Gemini 2.5 Flash
- **Contextual Responses**: AI remembers previous exchanges
- **Intelligent Error Recovery**: Graceful handling of API failures

### 💻 **User Experience**
- **Glass-Morphism Design**: Modern frosted glass aesthetic
- **Smooth Animations**: Floating elements and pulse effects
- **Toast Notifications**: Real-time feedback for user actions
- **Session Persistence**: Conversations saved with unique session IDs
- **Mobile Optimized**: Touch-friendly interface for all devices

### 🛡️ **Production Features**
- **Comprehensive Error Handling**: Fallback responses for all failure scenarios
- **API Health Monitoring**: Real-time service status indicators
- **Session Management**: Persistent chat history with cleanup
- **Graceful Degradation**: Continues functioning even with partial API failures

---

## 📋 Prerequisites

Before running the application, ensure you have:

- **Python 3.8+** installed
- **pip** package manager
- **Virtual environment** (recommended)
- **API Keys** for the following services:
  - 🎯 **AssemblyAI** - Speech-to-Text
  - 🧠 **Google Gemini** - Language Model
  - 🎵 **Murf AI** - Text-to-Speech

---

## ⚙️ Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone <your-repository-url>
cd voice-ai-agent
```

### 2️⃣ **Create Virtual Environment**
```bash
# Windows
python -m venv flask_env
flask_env\Scripts\activate

# macOS/Linux
python -m venv flask_env
source flask_env/bin/activate
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Environment Configuration**
Create a `.env` file in the root directory:

```env
# 🎯 AssemblyAI Configuration
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here

# 🧠 Google Gemini Configuration  
GEMINI_API_KEY=your_gemini_api_key_here

# 🎵 Murf AI Configuration
MURF_API_KEY=your_murf_api_key_here

# 🔧 Flask Configuration (Optional)
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5️⃣ **Obtain API Keys**

#### 🎯 **AssemblyAI Setup**
1. Visit [AssemblyAI Console](https://app.assemblyai.com/)
2. Sign up/Login to your account
3. Navigate to **API Keys** section
4. Copy your API key to `.env` file

#### 🧠 **Google Gemini Setup**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing
3. Generate an API key for Gemini
4. Add key to `.env` file

#### 🎵 **Murf AI Setup**
1. Visit [Murf AI Platform](https://murf.ai/)
2. Sign up for an account
3. Navigate to API section
4. Generate your API key
5. Add to `.env` file

---

## 🚀 Running the Application

### **Start the Flask Server**
```bash
# Ensure virtual environment is activated
flask_env\Scripts\activate  # Windows
source flask_env/bin/activate  # macOS/Linux

# Run the application
python app.py
```

### **Access the Application**
- 🌐 **Web Interface**: http://127.0.0.1:5000
- 📊 **Health Check**: http://127.0.0.1:5000/health
- 🔧 **API Documentation**: http://127.0.0.1:5000/api

### **Using the Voice Agent**
1. **🎤 Press the Record Button** - Large purple button with microphone icon
2. **🗣️ Speak Your Message** - Watch the animated pulse rings while recording
3. **⏹️ Tap to Stop** - Button changes to red with stop icon
4. **🤖 Receive AI Response** - Audio plays automatically with visual feedback
5. **🔄 Continue Conversation** - Tap record button for follow-up questions

---

## 📡 API Endpoints

### **Chat Endpoints**
```http
POST /agent/chat/<session_id>
Content-Type: multipart/form-data

# Send audio file for processing
# Returns: transcription, AI response, and audio URL
```

### **Session Management**
```http
GET /agent/sessions
# List all active chat sessions

GET /agent/session/<session_id>/history  
# Get conversation history for session

DELETE /agent/session/<session_id>
# Clear/delete a chat session
```

### **Health & Status**
```http
GET /health
# Check API service status

GET /admin/error-status
# View error simulation settings
```

---

## 🏗️ Project Structure

```
voice-ai-agent/
├── 📄 app.py                 # Main Flask application
├── 📋 requirements.txt       # Python dependencies
├── 🌐 templates/
│   └── 📄 index.html        # Frontend interface
├── 📁 static/               # Static assets
│   ├── 🖼️ images/
│   └── 🎵 audio/
├── 🐍 flask_env/            # Virtual environment
├── ⚙️ .env                  # Environment variables
└── 📚 README.md             # Project documentation
```

---

## 🔧 Advanced Configuration

### **Error Simulation (Testing)**
For testing error handling, use the admin endpoints:

```bash
# Simulate AssemblyAI failure
curl -X POST http://127.0.0.1:5000/admin/simulate-errors \
  -H "Content-Type: application/json" \
  -d '{"assemblyai": true}'

# Clear all error simulations
curl -X POST http://127.0.0.1:5000/admin/simulate-errors \
  -H "Content-Type: application/json" \
  -d '{"assemblyai": false, "gemini": false, "murf": false}'
```

### **Session Customization**
Sessions are automatically created with unique IDs:
- Format: `session_<timestamp>_<random_string>`
- Stored in memory with conversation history
- Automatic cleanup on server restart

---

## 🚨 Troubleshooting

### **Common Issues**

#### ❌ **Microphone Access Denied**
```
Solution: Enable microphone permissions in browser settings
Chrome: Settings → Privacy & Security → Site Settings → Microphone
```

#### ❌ **API Key Errors**
```
Error: "API key not found" or "Authentication failed"
Solution: 
1. Verify .env file exists in root directory
2. Check API key format and validity
3. Restart Flask server after updating .env
```

#### ❌ **Audio Playback Issues**
```
Error: Audio not playing automatically
Solution: 
1. Check browser autoplay policies
2. Interact with page before first recording
3. Enable audio in browser settings
```

#### ❌ **Network Connectivity**
```
Error: "Connection error" or timeouts
Solution:
1. Check internet connection
2. Verify API endpoints are accessible
3. Review firewall/proxy settings
```

---

## 🎯 Performance Optimization

### **Recommended Settings**
- **Audio Quality**: 16kHz, 16-bit for optimal STT accuracy
- **Session Limits**: Monitor memory usage for long conversations
- **API Timeouts**: 30-second timeout for reliable responses
- **Concurrent Users**: Flask development server handles ~10 concurrent users

### **Production Deployment**
For production use, consider:
- **WSGI Server**: Use Gunicorn or uWSGI instead of Flask dev server
- **Database**: Replace in-memory storage with Redis/PostgreSQL
- **Load Balancing**: Implement for high-traffic scenarios
- **HTTPS**: SSL certificates for secure audio transmission

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **💾 Commit changes** (`git commit -m 'Add amazing feature'`)
4. **📤 Push to branch** (`git push origin feature/amazing-feature`)
5. **🔄 Open a Pull Request**

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Murf AI** - For the inspiring 30 Days Voice Agents Challenge
- **AssemblyAI** - Excellent speech-to-text API with high accuracy
- **Google** - Powerful Gemini AI models for natural conversations
- **Tailwind CSS** - Beautiful utility-first CSS framework
- **Flask Community** - Lightweight and flexible web framework

---

## 📞 Support & Contact

- **🐛 Issues**: Open a GitHub issue for bugs or feature requests
- **💬 Discussions**: Use GitHub Discussions for questions
- **📧 Email**: [your-email@example.com]
- **🐦 Twitter**: [@your-twitter-handle]

---

<div align="center">
  <p><strong>Built with ❤️ for the Murf AI Voice Agents Challenge</strong></p>
  <p><em>Creating the future of human-AI voice interaction</em></p>
</div>
