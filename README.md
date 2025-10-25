# AI-Powered Educational Assistant

A sophisticated Streamlit-based AI chatbot application designed to help educators with Asian American Studies curriculum development. The application combines document analysis, knowledge base retrieval, and AI-powered insights to provide comprehensive educational support.

## 🚀 Features

### Core Functionality
- 🤖 **Dual-Path AI Analysis**: Combines state requirements analysis with knowledge base retrieval
- 📄 **Document Processing**: Upload and analyze PDF, DOCX, and TXT files
- 🔍 **RAG (Retrieval-Augmented Generation)**: Search AWS Bedrock Knowledge Base for relevant information
- 💬 **Interactive Chat Interface**: Natural language conversation with AI assistant
- 📚 **Citation System**: Proper attribution and source tracking

### Educational Focus
- 🎓 **Asian American Studies**: Specialized curriculum development support
- 🗺️ **State Requirements**: Analyze state education standards and requirements
- 📊 **Grade Level Support**: Kindergarten through 12th grade filtering
- 🏛️ **Multi-State Support**: All 50 US states included

### User Interface
- 🎨 **Modern UI**: Clean, responsive Streamlit interface
- 📱 **Sidebar Controls**: Easy access to filters and document management
- 📈 **Pipeline Logging**: Real-time execution tracking and progress monitoring
- 🔄 **Session Management**: Persistent chat history and document storage

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS CLI configured (optional but recommended)

### Setup Steps

1. **Clone the repository**:
```bash
git clone <repository-url>
cd sdsu-ai-hackathon-team-1
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the project root with the following variables:

```bash
# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Bedrock Knowledge Base
KNOWLEDGE_BASE_ID=your_knowledge_base_id_here
```

**Required Environment Variables**:
- `AWS_DEFAULT_REGION`: AWS region for Bedrock services (default: us-west-2)
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `KNOWLEDGE_BASE_ID`: ID of your AWS Bedrock Knowledge Base

### AWS Bedrock Setup

1. **Enable Bedrock Models**: Ensure you have access to Claude models in your AWS region
2. **Create Knowledge Base**: Set up a Bedrock Knowledge Base with your educational content
3. **Configure Permissions**: Ensure your AWS credentials have the following permissions:
   - `bedrock:InvokeModel`
   - `bedrock:Retrieve`
   - `bedrock-agent-runtime:Retrieve`

## 🚀 Usage

### Starting the Application

1. **Activate your virtual environment**:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Run the Streamlit application**:
```bash
streamlit run app.py
```

3. **Open your browser** and navigate to `http://localhost:8501`

### How to Use

#### 1. Document Upload
- Use the sidebar to upload PDF, DOCX, or TXT files
- Documents are processed and stored in session state
- View document previews and remove files as needed

#### 2. Set Filters
- **States**: Select relevant US states for geographic filtering
- **Grade Level**: Choose from Kindergarten through 12th grade
- **Subject**: Currently supports English, Social Studies, U.S. History, and World History from AsianAmericanEDU.org!

#### 3. Chat with AI
- Type your questions in the chat input
- The AI will process your query through two parallel paths:
  - **Path 1**: Analyze uploaded documents (state requirements)
  - **Path 2**: Search knowledge base for relevant information
- Receive comprehensive responses with proper citations

#### 4. Review Results
- View pipeline execution logs in the sidebar
- Check citations and source information
- Access metadata debugging information

### Sample Use Cases

- **"What are the California state requirements for Asian American Studies in high school?"**
- **"How can I align my curriculum with Texas education standards?"**
- **"What resources are available for teaching Filipino immigration history?"**
- **"Create a lesson plan for 8th grade Asian American history"**

## 🏗️ Architecture

### Dual-Path Processing

The application uses a sophisticated two-path approach:

1. **State Requirements Path**:
   - Processes uploaded PDF documents
   - Uses Claude-3.5-Sonnet for analysis
   - Provides specific feedback on state requirements

2. **Knowledge Base Path**:
   - Searches AWS Bedrock Knowledge Base
   - Retrieves relevant documents using vector search
   - Processes matches through Claude for contextual responses

### Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: AWS Bedrock (Claude-3.5-Sonnet)
- **Document Processing**: PyPDF, python-docx
- **Cloud Services**: AWS Bedrock Agent Runtime, AWS Bedrock Runtime
- **Language**: Python 3.8+

## 📁 File Structure

```
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # This documentation
├── .env                     # Environment variables (create this)
└── venv/                    # Virtual environment (created during setup)
```

## 🔧 Configuration

### AWS Bedrock Models
The application uses the following Bedrock models:
- `anthropic.claude-3-5-sonnet-20241022-v2:0` for text generation
- Vector search for knowledge base retrieval

### Knowledge Base Configuration
- Retrieves up to 5 relevant documents per query
- Supports metadata extraction for citations
- Handles various document formats and sources

## 🐛 Troubleshooting

### Common Issues

1. **AWS Credentials Error**:
   - Verify your AWS credentials are correctly set
   - Check that your AWS region is supported for Bedrock

2. **Knowledge Base Not Found**:
   - Ensure your `KNOWLEDGE_BASE_ID` is correct
   - Verify the knowledge base is active and accessible

3. **Document Processing Errors**:
   - Check file format compatibility (PDF, DOCX, TXT only)
   - Ensure files are not corrupted or password-protected

4. **Memory Issues**:
   - Large documents may cause memory issues
   - Consider breaking large files into smaller chunks

### Debug Features

The application includes extensive debugging features:
- Metadata inspection for knowledge base documents
- Pipeline execution logging
- Error handling with detailed error messages

## 🔮 Code Review
https://youtu.be/SbU389zmDJ4?si=-B6QhUeI4E_cVQIa

## 📄 License

This project is part of the SDSU AI Hackathon Team 1 submission.

## 🤝 Contributing

This is a hackathon project. Feel free to fork and enhance with additional features!

## 📞 Support

For issues or questions, please refer to the troubleshooting section above or check the AWS Bedrock documentation for service-specific issues.
