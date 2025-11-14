# AI Document Insight Assistant

## 📘 Description
Final project for the **Level UP – Academy of Advanced ICT Skills for Women – AI Path** course.

 The application analyses documents (for example PDF, DOCX), generates summaries, translates summaries into Polish, and creates interactive quizzes based on the content.

---

## 🧠 Features
- Text extraction from documents using **Azure Document Intelligence**
- Summarisation and translation by **Azure OpenAI**
- Generation of quizzes based on the content
- Interactive web interface (Gradio)

---

## ⚙️ Installation

### 1️⃣ Cloning the project
```bash
git clone https://github.com/MariaOrlowska/ai-document-insight-assistant.git
cd ai-document-insight-assistant
```

###  Create & activate virtual environment (recommended)

Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (cmd):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation run:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```


### 2️⃣ Installing dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Setting environment variables in the .env file
```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
AZURE_DOCUMENT_INTELLIGENCE_KEY="<your-key>"
AZURE_OPENAI_ENDPOINT="https://<your-resource>.openai.azure.com/"
AZURE_OPENAI_KEY="<your-key>"
AZURE_OPENAI_DEPLOYMENT="<your-deployment-name>" 
```

---
## ▶️ Execution
```bash
python demo_gradio.py
```
Open your browser and navigate to the address shown in the console (e.g. `http://127.0.0.1:7860`).

---

## 📂 Project structure


```
ai-document-insight-assistant/
├── sources/                          
├── .env                              
├── .env.example                      
├── .gitignore                        
├── analysis_results/                 
├── config.py                         
├── document_intelligence_utils.py    
├── openai_utils.py                   
├── demo_gradio.py                    
├── requirements.txt                  
└── README.md                         
```

### File Descriptions

- **sources/** - Contains sample documents (PDF, DOCX files) used for testing and demonstration
- **.env** - Stores sensitive Azure credentials (endpoint URLs and API keys). **Never commit to git**
- **.env.example** - Template showing required environment variables without actual values
- **.gitignore** - Specifies files/folders to exclude from git (secrets, cache, virtual environments)
- **analysis_results/** - Auto-generated folder storing analysis outputs per document (timestamp-based subfolders)
- **config.py** - Loads and validates Azure credentials from .env file
- **document_intelligence_utils.py** - Extracts text from PDF/DOCX using Azure Document Intelligence API
- **openai_utils.py** - Generates summaries, Polish translations, and quizzes via Azure OpenAI API
- **demo_gradio.py** - Main entry point; provides interactive web UI (Gradio) for document analysis (run this to start the app)
- **requirements.txt** - Lists all Python packages needed (`pip install -r requirements.txt`)
- **README.md** - Project documentation and setup instructions




---

## 👨‍💻 Author
Final project: AI Document Insight Assistant 
 **Level UP course – Academy of Advanced ICT Skills for Women. AI Path**

Author: **Maria Orłowska**
