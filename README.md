# AI Quiz Generator

An intelligent quiz generation application that creates custom quizzes from your documents using Google's Gemini AI.

![AI Quiz Generator Demo](demo.gif)

## Features

- 📚 Support for multiple document formats (PDF, DOCX, TXT)
- 🎯 Three difficulty levels (Easy, Medium, Hard)
- 🔄 Interactive question-by-question navigation
- ✅ Immediate feedback and explanations
- 📊 Detailed score tracking and final results
- 🎨 Clean and modern user interface

## Getting Started

### Prerequisites
- Get your free Google Gemini API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
- Python 3.8 or higher

### Installation

1. Clone the repository:
```bash
git clone https://github.com/garroshub/AI_Quiz.git
cd AI_Quiz
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

## How to Use

1. **Configure API**:
   - Get your free API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
   - Enter your API key in the settings section of the app

2. **Upload Document**: 
   - Click "Browse files" or drag and drop your document
   - Supports PDF, DOCX, and TXT formats
   - Maximum file size: 200MB

3. **Configure Quiz**:
   - Set the number of questions (1-50)
   - Choose difficulty level (Easy/Medium/Hard)
   - Add optional instructions for specific focus areas

4. **Take Quiz**:
   - Answer questions one by one
   - Get immediate feedback after each answer
   - View explanations for correct answers
   - Track your progress with the progress bar

5. **Review Results**:
   - See your final score and percentage
   - Option to review all answers
   - Start a new quiz at any time

## Difficulty Levels

- **Easy**: Basic concepts and definitions
- **Medium**: Applied knowledge and understanding
- **Hard**: Complex scenarios and deep analysis

## Requirements

- Python 3.8+
- Streamlit
- Google Gemini AI API
- PyPDF2 (for PDF files)
- python-docx (for DOCX files)

## Security Note

⚠️ Never commit your API key or expose it. 

## Contributing

Feel free to open issues or submit pull requests for any improvements you'd like to suggest.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://deepmind.google/technologies/gemini/)
