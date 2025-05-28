import os
from agents.classifier import ClassifierAgent
from agents.email_agent import EmailAgent
from agents.json_agent import JSONAgent
from agents.pdf_agent import PDFAgent
from memory.memory_store import MemoryStore
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Multi-Format Intake Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
classifier = ClassifierAgent()
email_agent = EmailAgent()
json_agent = JSONAgent()
pdf_agent = PDFAgent()
memory = MemoryStore()

@app.get("/", response_class=HTMLResponse)
async def main_page():
    return '''
    <html>
        <head>
            <title>Smart Document Processing Assistant</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {
                    --primary-color: #4F46E5;
                    --primary-hover: #4338CA;
                    --secondary-color: #10B981;
                    --background-color: #F3F4F6;
                    --surface-color: #FFFFFF;
                    --text-primary: #111827;
                    --text-secondary: #6B7280;
                    --border-color: #E5E7EB;
                    --success-color: #059669;
                    --error-color: #DC2626;
                }

                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Inter', sans-serif;
                    background-color: var(--background-color);
                    color: var(--text-primary);
                    line-height: 1.6;
                    min-height: 100vh;
                }

                .app-container {
                    display: flex;
                    min-height: 100vh;
                }

                .sidebar {
                    width: 320px;
                    background-color: var(--surface-color);
                    border-right: 1px solid var(--border-color);
                    padding: 2rem;
                    height: 100vh;
                    position: fixed;
                    overflow-y: auto;
                }

                .main-content {
                    flex: 1;
                    margin-left: 320px;
                    padding: 2rem 3rem;
                }

                .content-wrapper {
                    max-width: 1200px;
                    margin: 0 auto;
                }

                h1 {
                    font-size: 2rem;
                    font-weight: 700;
                    color: var(--primary-color);
                    margin-bottom: 2rem;
                }

                h2 {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 1rem;
                }

                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 2rem;
                    margin-bottom: 3rem;
                }

                .feature-card {
                    background: var(--surface-color);
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                }

                .feature-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 12px -1px rgba(0, 0, 0, 0.15);
                }

                .feature-icon {
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }

                .feature-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 0.75rem;
                    color: var(--text-primary);
                }

                .feature-description {
                    color: var(--text-secondary);
                    font-size: 1rem;
                }

                .main-sections {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 2rem;
                }

                .upload-section, .text-section {
                    background: var(--surface-color);
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }

                .section-title {
                    display: flex;
                    align-items: center;
                    margin-bottom: 1.5rem;
                }

                .section-title .icon {
                    font-size: 1.5rem;
                    margin-right: 0.75rem;
                }

                input[type="file"] {
                    width: 100%;
                    padding: 1.5rem;
                    border: 2px dashed var(--border-color);
                    border-radius: 8px;
                    margin: 1rem 0;
                    cursor: pointer;
                    transition: border-color 0.3s ease;
                }

                input[type="file"]:hover {
                    border-color: var(--primary-color);
                }

                textarea {
                    width: 100%;
                    padding: 1rem;
                    border: 2px solid var(--border-color);
                    border-radius: 8px;
                    margin: 1rem 0;
                    min-height: 200px;
                    font-family: inherit;
                    font-size: 1rem;
                    resize: vertical;
                    transition: border-color 0.3s ease;
                }

                textarea:focus {
                    outline: none;
                    border-color: var(--primary-color);
                }

                button {
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    padding: 0.875rem 1.75rem;
                    border-radius: 8px;
                    font-weight: 500;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    width: 100%;
                }

                button:hover {
                    background: var(--primary-hover);
                    transform: translateY(-1px);
                }

                .results-box {
                    display: none;
                    background: var(--surface-color);
                    border-radius: 12px;
                    padding: 2rem;
                    margin: 2rem 0;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }

                .results-box.success {
                    border-left: 4px solid var(--success-color);
                }

                .results-box.error {
                    border-left: 4px solid var(--error-color);
                }

                .results-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 1.5rem;
                    padding-bottom: 1rem;
                    border-bottom: 1px solid var(--border-color);
                }

                .results-header h3 {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: var(--text-primary);
                }

                .results-content {
                    font-family: 'Monaco', monospace;
                    font-size: 0.9rem;
                    line-height: 1.6;
                    white-space: pre-wrap;
                    background: var(--background-color);
                    padding: 1.5rem;
                    border-radius: 8px;
                }

                .history-section {
                    margin-top: 2rem;
                }

                .history-box {
                    background: var(--surface-color);
                    border-radius: 12px;
                    overflow: hidden;
                }

                .history-item {
                    padding: 1rem;
                    border-bottom: 1px solid var(--border-color);
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }

                .history-item:hover {
                    background-color: var(--background-color);
                }

                .history-item .title {
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                }

                .history-item .time {
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                }

                .history-item .summary {
                    display: none;
                    margin-top: 1rem;
                    padding: 1rem;
                    background: var(--background-color);
                    border-radius: 8px;
                    font-family: 'Monaco', monospace;
                    font-size: 0.875rem;
                }

                .loading {
                    display: none;
                    text-align: center;
                    padding: 2rem;
                }

                .loading:after {
                    content: "⚙️ Processing...";
                    font-size: 1.2rem;
                    color: var(--text-secondary);
                }

                .scroll-to-results {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    background: var(--secondary-color);
                    color: white;
                    width: 3.5rem;
                    height: 3.5rem;
                    border-radius: 50%;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    cursor: pointer;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                }

                .scroll-to-results:hover {
                    transform: translateY(-2px);
                    background: var(--success-color);
                    box-shadow: 0 6px 8px -1px rgba(0, 0, 0, 0.15);
                }

                /* Responsive Design */
                @media (max-width: 1024px) {
                    .app-container {
                        display: block;
                    }

                    .sidebar {
                        position: static;
                        width: 100%;
                        height: auto;
                        border-right: none;
                        border-bottom: 1px solid var(--border-color);
                        padding: 1.5rem;
                    }

                    .main-content {
                        margin-left: 0;
                        padding: 1.5rem;
                    }

                    .content-wrapper {
                        max-width: 900px;
                    }

                    .feature-grid {
                        grid-template-columns: repeat(3, 1fr);
                        gap: 1.5rem;
                    }

                    .main-sections {
                        grid-template-columns: 1fr 1fr;
                        gap: 1.5rem;
                    }
                }

                @media (max-width: 768px) {
                    .feature-grid {
                        grid-template-columns: repeat(2, 1fr);
                        gap: 1rem;
                    }

                    .main-sections {
                        grid-template-columns: 1fr;
                        gap: 1.5rem;
                    }

                    .feature-card {
                        padding: 1.5rem;
                    }

                    .feature-icon {
                        font-size: 2rem;
                    }

                    h1 {
                        font-size: 1.75rem;
                    }

                    h2 {
                        font-size: 1.25rem;
                    }

                    .upload-section, .text-section {
                        padding: 1.5rem;
                    }
                }

                @media (max-width: 480px) {
                    body {
                        font-size: 14px;
                    }

                    .sidebar {
                        padding: 1rem;
                    }

                    .main-content {
                        padding: 1rem;
                    }

                    .feature-grid {
                        grid-template-columns: 1fr;
                        gap: 1rem;
                    }

                    .feature-card {
                        padding: 1.25rem;
                    }

                    .feature-icon {
                        font-size: 1.75rem;
                        margin-bottom: 0.75rem;
                    }

                    .feature-title {
                        font-size: 1.1rem;
                    }

                    .upload-section, .text-section {
                        padding: 1.25rem;
                    }

                    input[type="file"] {
                        padding: 1rem;
                    }

                    textarea {
                        min-height: 150px;
                    }

                    button {
                        padding: 0.75rem 1.5rem;
                    }

                    .results-box {
                        padding: 1.25rem;
                        margin: 1rem 0;
                    }

                    .results-content {
                        padding: 1rem;
                        font-size: 0.85rem;
                    }

                    .history-item {
                        padding: 0.75rem;
                    }

                    .history-item .title {
                        font-size: 0.9rem;
                    }

                    .history-item .time {
                        font-size: 0.8rem;
                    }

                    .scroll-to-results {
                        width: 3rem;
                        height: 3rem;
                        font-size: 1.25rem;
                        bottom: 1rem;
                        right: 1rem;
                    }
                }

                /* Handle very small screens */
                @media (max-width: 320px) {
                    .sidebar {
                        padding: 0.75rem;
                    }

                    .main-content {
                        padding: 0.75rem;
                    }

                    h1 {
                        font-size: 1.5rem;
                        margin-bottom: 1rem;
                    }

                    .feature-card {
                        padding: 1rem;
                    }

                    .upload-section, .text-section {
                        padding: 1rem;
                    }

                    input[type="file"] {
                        padding: 0.75rem;
                    }

                    button {
                        padding: 0.5rem 1rem;
                    }
                }

                /* Handle landscape orientation on mobile */
                @media (max-width: 900px) and (orientation: landscape) {
                    .sidebar {
                        padding: 1rem;
                    }

                    .feature-grid {
                        grid-template-columns: repeat(3, 1fr);
                        gap: 1rem;
                    }

                    .main-sections {
                        grid-template-columns: 1fr 1fr;
                        gap: 1rem;
                    }

                    textarea {
                        min-height: 120px;
                    }
                }

                /* Handle high-DPI mobile screens */
                @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
                    .feature-card, .upload-section, .text-section, .results-box {
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
                    }

                    input[type="file"], textarea {
                        border-width: 1px;
                    }
                }

                /* Improve touch targets on mobile */
                @media (hover: none) and (pointer: coarse) {
                    button, .history-item, input[type="file"] {
                        min-height: 44px;
                    }

                    .feature-card {
                        transform: none !important;
                    }

                    .scroll-to-results:active {
                        transform: scale(0.95);
                    }
                }
            </style>
        </head>
        <body>
            <div class="app-container">
                <aside class="sidebar">
                    <h1>Document Processing</h1>
                    <div class="history-section">
                        <h2>📊 Processing History</h2>
                        <div id="historyBox" class="history-box"></div>
                    </div>
                </aside>

                <main class="main-content">
                    <div class="content-wrapper">
                        <div class="feature-grid">
                            <div class="feature-card">
                                <div class="feature-icon">📄</div>
                                <div class="feature-title">Multiple Formats</div>
                                <div class="feature-description">Process PDF, JSON, Email, and Text files with ease</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">🔍</div>
                                <div class="feature-title">Smart Analysis</div>
                                <div class="feature-description">Extract key information and classify content automatically</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">📊</div>
                                <div class="feature-title">Organized Results</div>
                                <div class="feature-description">Get clean summaries and structured data instantly</div>
                            </div>
                        </div>

                        <div class="main-sections">
                            <div class="upload-section">
                                <div class="section-title">
                                    <span class="icon">📁</span>
                                    <h2>Upload Document</h2>
                                </div>
                                <p>Drag & drop or select a file to process (PDF, JSON, or text file)</p>
                                <form id="uploadForm">
                                    <input type="file" name="file" required>
                                    <button type="submit">Process Document</button>
                                </form>
                            </div>

                            <div class="text-section">
                                <div class="section-title">
                                    <span class="icon">📝</span>
                                    <h2>Process Text</h2>
                                </div>
                                <p>Paste your email or text content below</p>
                                <form id="textForm">
                                    <textarea name="content" placeholder="Paste email or text content here..."></textarea>
                                    <button type="submit">Process Text</button>
                                </form>
                            </div>
                        </div>

                        <div id="loading" class="loading"></div>
                        
                        <div id="resultsBox" class="results-box">
                            <div class="results-header">
                                <h3>Processing Results</h3>
                            </div>
                            <div id="resultsContent" class="results-content"></div>
                        </div>
                    </div>
                </main>
            </div>

            <button id="scrollToResults" class="scroll-to-results" onclick="scrollToResults()" title="Scroll to Results">⬆️</button>

            <script>
                function formatResults(data) {
                    if (data.status === "error") {
                        return "❌ Error: " + data.message;
                    }

                    let output = [];
                    
                    if (data.summary) {
                        output.push(data.summary.status);
                        output.push("Document Type: " + data.summary.document_type);
                        if (data.classification && data.classification.intent) {
                            output.push("Intent: " + data.classification.intent);
                        }
                        if (data.summary.timestamp) {
                            output.push("Processed: " + data.summary.timestamp);
                        }
                    }

                    if (data.details) {
                        if (data.details.subject) {
                            output.push("\\nSubject: " + data.details.subject);
                        }
                        if (data.details.key_requests && data.details.key_requests.length > 0) {
                            output.push("\\nKey Requests:");
                            data.details.key_requests.forEach(req => {
                                output.push("  • " + req);
                            });
                        }
                        if (data.details.contact_info && data.details.contact_info.length > 0) {
                            output.push("\\nContact Information:");
                            data.details.contact_info.forEach(contact => {
                                output.push("  • " + contact);
                            });
                        }
                    }

                    if (data.metrics) {
                        output.push("\\nMetrics:");
                        Object.entries(data.metrics).forEach(([key, value]) => {
                            output.push("  • " + key + ": " + value);
                        });
                    }

                    if (data.suggested_action) {
                        output.push("\\n" + data.suggested_action);
                    }

                    return output.join("\\n");
                }

                function scrollToResults() {
                    const resultsBox = document.getElementById("resultsBox");
                    resultsBox.scrollIntoView({ behavior: "smooth" });
                }

                function getHistoryTitle(item) {
                    const data = typeof item.extracted_data === 'string' 
                        ? JSON.parse(item.extracted_data) 
                        : item.extracted_data;
                    
                    if (item.input_type.toLowerCase() === 'email') {
                        if (data.details && data.details.subject) {
                            return `📧 ${data.details.subject}`;
                        }
                        return '📧 Email Document';
                    } else if (item.input_type.toLowerCase() === 'pdf') {
                        return `📄 ${item.source_info}`;
                    } else if (item.input_type.toLowerCase() === 'json') {
                        return '🔧 JSON Document';
                    }
                    return `📝 ${item.source_info}`;
                }

                function toggleSummary(itemId) {
                    const summaryElement = document.getElementById(`summary-${itemId}`);
                    const allSummaries = document.querySelectorAll('.summary');
                    
                    // Hide all other summaries
                    allSummaries.forEach(summary => {
                        if (summary.id !== `summary-${itemId}`) {
                            summary.style.display = 'none';
                        }
                    });
                    
                    // Toggle clicked summary
                    if (summaryElement) {
                        summaryElement.style.display = 
                            summaryElement.style.display === 'none' ? 'block' : 'none';
                    }
                }

                async function updateHistory() {
                    try {
                        const response = await fetch("/history");
                        const data = await response.json();
                        const historyBox = document.getElementById("historyBox");
                        
                        if (data.history && data.history.length > 0) {
                            const historyHtml = data.history.map(item => {
                                const extractedData = typeof item.extracted_data === 'string' 
                                    ? JSON.parse(item.extracted_data) 
                                    : item.extracted_data;
                                
                                const title = getHistoryTitle(item);
                                const formattedTime = new Date(item.timestamp).toLocaleString();
                                
                                return `
                                    <div class="history-item" onclick="toggleSummary('${item.id}')">
                                        <div class="title">${title}</div>
                                        <div class="time">${formattedTime}</div>
                                        <div id="summary-${item.id}" class="summary">
${formatResults(extractedData)}
                                        </div>
                                    </div>
                                `;
                            }).join('');
                            
                            historyBox.innerHTML = historyHtml;
                        } else {
                            historyBox.innerHTML = "<p>No processing history yet</p>";
                        }
                    } catch (error) {
                        console.error("Error loading history:", error);
                        historyBox.innerHTML = "<p>❌ Error loading history</p>";
                    }
                }

                async function handleFormSubmit(event, formId, endpoint) {
                    event.preventDefault();
                    
                    const form = document.getElementById(formId);
                    const loading = document.getElementById("loading");
                    const resultsBox = document.getElementById("resultsBox");
                    const resultsContent = document.getElementById("resultsContent");
                    const scrollButton = document.getElementById("scrollToResults");

                    loading.style.display = "block";
                    resultsBox.style.display = "none";
                    scrollButton.style.display = "none";

                    try {
                        const formData = new FormData(form);
                        const response = await fetch(endpoint, {
                            method: "POST",
                            body: formData
                        });
                        
                        const data = await response.json();
                        
                        loading.style.display = "none";
                        resultsBox.style.display = "block";
                        resultsBox.className = "results-box " + (data.status === "error" ? "error" : "success");
                        resultsContent.textContent = formatResults(data);
                        scrollButton.style.display = "block";
                        scrollToResults();
                        
                        // Update history after processing
                        updateHistory();
                    } catch (error) {
                        loading.style.display = "none";
                        resultsBox.style.display = "block";
                        resultsBox.className = "results-box error";
                        resultsContent.textContent = "❌ Error: " + error.message;
                        scrollButton.style.display = "block";
                        scrollToResults();
                    }
                }

                // Add event listeners
                document.getElementById("uploadForm").addEventListener("submit", (e) => handleFormSubmit(e, "uploadForm", "/process-file"));
                document.getElementById("textForm").addEventListener("submit", (e) => handleFormSubmit(e, "textForm", "/process-text"));
                
                // Load initial history
                updateHistory();
            </script>
        </body>
    </html>
    '''

@app.post("/process-file")
async def process_file(file: UploadFile = File(...)):
    """Process uploaded file"""
    try:
        content = await file.read()
        
        # For text-based files, decode content
        if not file.filename.lower().endswith('.pdf'):
            try:
                content_str = content.decode('utf-8')
            except UnicodeDecodeError:
                return JSONResponse({
                    "status": "error",
                    "message": "Invalid file encoding"
                })
        else:
            content_str = "Binary PDF content"
        
        # Step 1: Classify
        classification = classifier.classify_input(content_str, file.filename)
        
        # Step 2: Route to appropriate agent
        if classification["format"].upper() == "JSON":
            extracted_data = json_agent.extract_json_data(content_str)
        elif classification["format"].upper() == "EMAIL":
            extracted_data = email_agent.extract_email_data(content_str)
        elif classification["format"].upper() == "PDF":
            extracted_data = pdf_agent.process_pdf(content)
        else:
            extracted_data = {
                "summary": {
                    "status": "✅ PROCESSED SUCCESSFULLY",
                    "document_type": "TEXT",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "details": {
                    "content_preview": content_str[:200] + "..."
                }
            }
        
        # Step 3: Store in memory
        memory.store_data(
            input_type=classification["format"],
            intent=classification["intent"],
            extracted_data=extracted_data,
            source_info=file.filename
        )
        
        # Add classification info to response
        response_data = {
            "status": "success",
            "classification": classification,
            **extracted_data
        }
        
        return JSONResponse(response_data)
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

@app.post("/process-text")
async def process_text(content: str = Form(...)):
    """Process text content"""
    try:
        # Step 1: Classify
        classification = classifier.classify_input(content)
        
        # Step 2: Route to appropriate agent
        if classification["format"].upper() == "EMAIL":
            extracted_data = email_agent.extract_email_data(content)
        elif classification["format"].upper() == "JSON":
            extracted_data = json_agent.extract_json_data(content)
        else:
            extracted_data = {
                "summary": {
                    "status": "✅ PROCESSED SUCCESSFULLY",
                    "document_type": "TEXT",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "details": {
                    "content_preview": content[:200] + "..."
                }
            }
        
        # Step 3: Store in memory
        memory.store_data(
            input_type=classification["format"],
            intent=classification["intent"],
            extracted_data=extracted_data,
            source_info="Direct text input"
        )
        
        # Add classification info to response
        response_data = {
            "status": "success",
            "classification": classification,
            **extracted_data
        }
        
        return JSONResponse(response_data)
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        })

@app.get("/history")
async def get_history():
    """Get processing history"""
    try:
        history = memory.get_recent_data(20)
        formatted_history = []
        
        for record in history:
            formatted_history.append({
                "id": record[0],
                "input_type": record[1],
                "intent": record[2],
                "extracted_data": json.loads(record[3]),
                "timestamp": record[4],
                "source_info": record[5]
            })
        
        return JSONResponse({"history": formatted_history})
        
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)