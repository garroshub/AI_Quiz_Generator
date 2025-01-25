import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from datetime import datetime

def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def read_text_file(file):
    return file.getvalue().decode('utf-8')

def generate_quiz(content, num_questions, additional_prompt=""):
    prompt = f"""Based on the following content, generate {num_questions} multiple choice questions. 
    For each question, follow this EXACT format:
    [
        {{
            "question": "What is...",
            "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
            "correct_answer": "A",
            "explanation": "This is correct because..."
        }},
        // more questions...
    ]
    
    Requirements:
    1. Return ONLY the JSON array, no other text
    2. Each question must have exactly 4 options
    3. Options must be prefixed with A), B), C), D)
    4. correct_answer must be just the letter (A, B, C, or D)
    5. Make questions clear and specific
    6. Provide detailed explanations
    
    Additional instructions: {additional_prompt}
    
    Content: {content[:5000]}"""  # Limit content length to avoid token limits

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response text
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Try to parse the JSON
        try:
            questions = eval(response_text)  # First try eval
        except:
            try:
                import json
                questions = json.loads(response_text)  # Then try json.loads
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse quiz response. Please try again.")
                return None
        
        # Validate the questions format
        if not isinstance(questions, list):
            st.error("Invalid response format. Please try again.")
            return None
            
        for q in questions:
            if not all(k in q for k in ['question', 'options', 'correct_answer', 'explanation']):
                st.error("Missing required fields in questions. Please try again.")
                return None
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                st.error("Each question must have exactly 4 options. Please try again.")
                return None
            if q['correct_answer'] not in ['A', 'B', 'C', 'D']:
                st.error("Invalid correct answer format. Please try again.")
                return None
        
        return questions
        
    except Exception as e:
        st.error(f"Failed to generate quiz: {str(e)}")
        return None

def main():
    # Initialize session states
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'question_states' not in st.session_state:
        st.session_state.question_states = {}
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 1
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'total_score' not in st.session_state:
        st.session_state.total_score = {'correct': 0, 'total': 0}
    if 'show_next' not in st.session_state:
        st.session_state.show_next = False
    if 'show_final_score' not in st.session_state:
        st.session_state.show_final_score = False
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'review_mode' not in st.session_state:
        st.session_state.review_mode = False
    if 'saved_quizzes' not in st.session_state:
        st.session_state.saved_quizzes = {}
    if 'viewing_saved_quiz' not in st.session_state:
        st.session_state.viewing_saved_quiz = None

    def save_current_quiz(quiz_name):
        # 保存当前测验的所有信息
        st.session_state.saved_quizzes[quiz_name] = {
            'quiz_data': st.session_state.quiz_data,
            'question_states': st.session_state.question_states,
            'total_score': st.session_state.total_score,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return_to_start()

    def next_question():
        if st.session_state.current_question < len(st.session_state.quiz_data):
            st.session_state.current_question += 1
            # 如果下一题已经回答过，保持show_next为True
            if st.session_state.current_question in st.session_state.question_states:
                st.session_state.show_next = True
            else:
                st.session_state.show_next = False
        else:
            st.session_state.show_final_score = True

    def prev_question():
        if st.session_state.current_question > 1:
            st.session_state.current_question -= 1
            # 如果前一题已经回答过，设置show_next为True
            if st.session_state.current_question in st.session_state.question_states:
                st.session_state.show_next = True

    def load_saved_quiz(quiz_name):
        # 加载保存的测验
        saved_quiz = st.session_state.saved_quizzes[quiz_name]
        st.session_state.quiz_data = saved_quiz['quiz_data']
        st.session_state.question_states = saved_quiz['question_states']
        st.session_state.total_score = saved_quiz['total_score']
        st.session_state.current_question = 1
        st.session_state.quiz_started = True
        st.session_state.review_mode = True
        st.session_state.viewing_saved_quiz = quiz_name
        st.session_state.show_final_score = False

    def return_to_start():
        st.session_state.quiz_started = False
        st.session_state.quiz_data = None
        st.session_state.question_states = {}
        st.session_state.current_question = 1
        st.session_state.total_score = {'correct': 0, 'total': 0}
        st.session_state.show_next = False
        st.session_state.show_final_score = False
        st.session_state.review_mode = False
        st.session_state.viewing_saved_quiz = None
        # 不清除API密钥和已保存的测验
        # st.session_state.api_key = None

    def start_review():
        st.session_state.review_mode = True
        st.session_state.current_question = 1
        st.session_state.show_final_score = False

    # Quiz generation page
    if not st.session_state.quiz_started:
        st.title("AI Quiz Generator")
        
        # 显示已保存的测验列表
        if st.session_state.saved_quizzes:
            st.write("📚 Saved Quizzes")
            for quiz_name, quiz_data in st.session_state.saved_quizzes.items():
                score = quiz_data['total_score']
                percentage = (score['correct'] / score['total']) * 100
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{quiz_name}** ({quiz_data['timestamp']})")
                with col2:
                    st.write(f"Score: {percentage:.1f}%")
                with col3:
                    if st.button("View", key=f"view_{quiz_name}"):
                        load_saved_quiz(quiz_name)
                        st.experimental_rerun()
            
            st.write("---")  # 分隔线
        
        # API Key input section (只在未设置时显示)
        if not st.session_state.api_key:
            with st.expander("⚙️ API Settings", expanded=True):
                st.markdown("""
                ### Google Gemini API Key Required
                1. Get your free API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
                2. Enter the key below to start using the quiz generator
                
                Note: Your API key is stored only in your browser session and is never saved on our servers.
                """)
                api_key = st.text_input("Enter your Google Gemini API Key:", type="password", key="api_key_input")
                if api_key:
                    try:
                        genai.configure(api_key=api_key)
                        global model
                        model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                        st.session_state.api_key = api_key
                        st.success("✅ API Key configured successfully!")
                    except Exception as e:
                        st.error("❌ Invalid API Key. Please check and try again.")
                        st.session_state.api_key = None
        else:
            # 如果已经设置了API密钥，直接配置
            genai.configure(api_key=st.session_state.api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
                    
        if st.session_state.api_key:
            st.write("Upload a document (PDF, DOCX, or TXT) and specify how many questions you want to generate.")
            
            uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
            num_questions = st.number_input("Number of questions to generate", min_value=1, max_value=50, value=5)
            
            difficulty = st.selectbox(
                "Select difficulty level",
                ["Easy", "Medium", "Hard"],
                help="Easy: Basic concepts and definitions\nMedium: Applied knowledge and understanding\nHard: Complex scenarios and deep analysis"
            )
            
            additional_prompt = st.text_area(
                "Additional Instructions (Optional)", 
                placeholder="Enter any additional instructions for the AI, e.g., 'Focus on specific topics'",
                help="You can provide additional guidance to customize how the AI generates questions."
            )
            
            if uploaded_file is not None:
                with st.spinner("Reading file..."):
                    file_type = uploaded_file.name.split('.')[-1].lower()
                    if file_type == 'pdf':
                        content = read_pdf(uploaded_file)
                    elif file_type == 'docx':
                        content = read_docx(uploaded_file)
                    else:  # txt
                        content = read_text_file(uploaded_file)
                        
                if st.button("Generate Quiz", type="primary"):
                    with st.spinner("Generating quiz questions..."):
                        difficulty_prompt = f"\nGenerate {difficulty.lower()} difficulty questions. "
                        if difficulty == "Easy":
                            difficulty_prompt += "Focus on basic concepts, definitions, and straightforward applications. "
                        elif difficulty == "Medium":
                            difficulty_prompt += "Include questions that require understanding and application of concepts. "
                        else:  # Hard
                            difficulty_prompt += "Create complex questions that require deep understanding, analysis, and integration of multiple concepts. "
                        
                        full_prompt = difficulty_prompt + (additional_prompt if additional_prompt else "")
                        st.session_state.quiz_data = generate_quiz(content, num_questions, full_prompt)
                        if st.session_state.quiz_data:
                            st.session_state.question_states = {}
                            st.session_state.current_question = 1
                            st.session_state.quiz_started = True
                            st.session_state.total_score = {'correct': 0, 'total': 0}
                            st.experimental_rerun()
        else:
            st.info("👆 Please configure your API Key in the settings above to start using the quiz generator.")

    # Quiz taking or review page
    else:
        if st.session_state.show_final_score and not st.session_state.review_mode:
            st.title("🎉 Quiz Complete!")
            
            # 显示分数和百分比
            score = st.session_state.total_score
            correct = score['correct']
            total = score['total']
            percentage = (correct / total) * 100
            
            # 使用大号文字显示分数
            st.markdown(f"<h2 style='text-align: center'>Your Score: {correct}/{total}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center'>Percentage: {percentage:.1f}%</h3>", unsafe_allow_html=True)
            
            # 根据得分显示不同的评价
            if percentage >= 90:
                st.success("🌟 Outstanding! You've mastered this material!")
            elif percentage >= 70:
                st.success("👏 Great job! You have a good understanding!")
            elif percentage >= 50:
                st.info("📚 Good effort! Keep learning to improve!")
            else:
                st.info("💪 Keep practicing! You'll get better!")
            
            # 添加一些空间
            st.write("")
            st.write("")
            
            # Save Quiz 选项
            with st.expander("💾 Save This Quiz"):
                quiz_name = st.text_input("Enter a name for this quiz:", 
                    value=f"Quiz {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                if st.button("Save Quiz", type="primary"):
                    if quiz_name in st.session_state.saved_quizzes:
                        st.error("A quiz with this name already exists. Please choose a different name.")
                    else:
                        save_current_quiz(quiz_name)
                        st.success("Quiz saved successfully!")
                        st.experimental_rerun()
            
            st.write("")  # 添加空间
            
            # 选项按钮
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Review Questions", type="secondary", use_container_width=True):
                    start_review()
                    st.experimental_rerun()
            with col2:
                if st.button("🏠 Return to Start", type="primary", use_container_width=True):
                    return_to_start()
                    st.experimental_rerun()
        else:
            # Display current question
            total_questions = len(st.session_state.quiz_data)
            st.title("Quiz")
            st.progress(st.session_state.current_question / total_questions)
            
            current_q = st.session_state.current_question
            question = st.session_state.quiz_data[current_q - 1]
            
            st.write(f"Question {current_q} of {total_questions}")
            st.write(question['question'])
            
            # In review mode, show the answer that was previously selected
            previous_answer = st.session_state.question_states.get(current_q, {}).get('selected_answer', None)
            
            for i, option in enumerate(question['options']):
                if st.session_state.review_mode:
                    # In review mode, use radio button but disable it
                    st.radio(
                        "Select your answer:",
                        [option],
                        key=f"q{current_q}_option{i}",
                        disabled=True,
                        index=0 if previous_answer == chr(65 + i) else None
                    )
                else:
                    # In quiz mode, use radio button normally
                    if st.radio(
                        "Select your answer:",
                        [option],
                        key=f"q{current_q}_option{i}",
                        index=None
                    ):
                        selected_answer = chr(65 + i)  # Convert 0,1,2,3 to A,B,C,D
                        
                        if current_q not in st.session_state.question_states:
                            st.session_state.question_states[current_q] = {
                                'selected_answer': selected_answer,
                                'is_correct': selected_answer == question['correct_answer']
                            }
                            
                            if selected_answer == question['correct_answer']:
                                st.session_state.total_score['correct'] += 1
                            st.session_state.total_score['total'] += 1
                            
                            st.session_state.show_next = True
            
            # Show result after answer is selected
            if current_q in st.session_state.question_states or st.session_state.review_mode:
                selected = st.session_state.question_states[current_q]['selected_answer']
                correct = question['correct_answer']
                
                if selected == correct:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. Correct answer: {correct}")
                
                st.info("Explanation: " + question['explanation'])
            
            # Navigation buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.session_state.current_question > 1:
                    if st.button("Previous Question"):
                        prev_question()
                        st.experimental_rerun()
            
            with col2:
                if st.session_state.viewing_saved_quiz:
                    st.write(f"Viewing: {st.session_state.viewing_saved_quiz}")
                    # 添加Next按钮，如果不是最后一题
                    if st.session_state.current_question < len(st.session_state.quiz_data):
                        if st.button("Next Question"):
                            next_question()
                            st.experimental_rerun()
                else:
                    # 如果是最后一题且已回答，显示Finish按钮
                    if (st.session_state.current_question == len(st.session_state.quiz_data) and 
                        current_q in st.session_state.question_states):
                        if st.button("Finish Quiz", type="primary"):
                            st.session_state.show_final_score = True
                            st.experimental_rerun()
                    # 否则显示Next按钮（如果可以的话）
                    else:
                        can_show_next = (
                            st.session_state.review_mode or 
                            (current_q in st.session_state.question_states and 
                            st.session_state.current_question < len(st.session_state.quiz_data))
                        )
                        if can_show_next:
                            if st.button("Next Question"):
                                next_question()
                                st.experimental_rerun()
            
            with col3:
                if st.button("Return to Start"):
                    return_to_start()
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
