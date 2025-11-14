import gradio as gr
import os
import json
from datetime import datetime
from document_intelligence_utils import extract_text_from_doc
from openai_utils import generate_summary, translate_to_polish, generate_quiz
import shutil
import random

# Folder for saving results
OUTPUT_DIR = "analysis_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_document(file):
    """Analyses the document and saves the results to a folder"""
    text = extract_text_from_doc(file.name)
    summary = generate_summary(text, language="en")
    translated = translate_to_polish(summary)
    quiz_list = generate_quiz(summary)
    
    # Wrap quiz_list in a dictionary with the structure {‘questions’: [...]}
    quiz = {"questions": quiz_list if isinstance(quiz_list, list) else []}
    
    # Randomise the options in each question, keeping the correct answer as the value.
    for q in quiz.get("questions", []):
        opts = q.get("options", [])
        correct = q.get("correct_answer")
        if opts and correct is not None:
            # create pairs (option, is_correct) and shuffle
            paired = [(opt, opt == correct) for opt in opts]
            random.shuffle(paired)
            # return to the list of options and update correct_answer (with the value, not the index)
            q["options"] = [p[0] for p in paired]
            # Leave correct_answer as the original correct value (string comparison works with submit_answer).
            q["correct_answer"] = correct
    
    # Create a folder with the date/time 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_folder = os.path.join(OUTPUT_DIR, f"analysis_{timestamp}")
    os.makedirs(result_folder, exist_ok=True)
    
    # Copy the original file
    original_filename = os.path.basename(file.name)
    shutil.copy(file.name, os.path.join(result_folder, original_filename))
    
    # Save the summary + translation in one file
    summary_file = os.path.join(result_folder, "summary_and_translation.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("=== SUMMARY (EN) ===\n\n")
        f.write(summary or "")
        f.write("\n\n=== TRANSLATION (PL) ===\n\n")
        f.write(translated or "")
    
    # Save quiz in JSON
    quiz_file = os.path.join(result_folder, "quiz.json")
    with open(quiz_file, "w", encoding="utf-8") as f:
        json.dump(quiz, f, ensure_ascii=False, indent=2)
    
    return summary, translated, quiz, result_folder, quiz

def check_answer(quiz_data, question_idx, selected_answer):
    """Checks the user's response to a quiz question"""
    if not quiz_data or "questions" not in quiz_data:
        return "The quiz did not load correctly."
    
    questions = quiz_data.get("questions", [])
    if question_idx >= len(questions):
        return "Question not found."
    
    question = questions[question_idx]
    correct = question.get("correct_answer", "")
    
    if selected_answer == correct:
        return f"✅ Correct! Answer: {correct}"
    else:
        return f"❌ Incorrect. Your answer: {selected_answer}. Correct: {correct}"

def update_question(quiz_data, idx):
    """Updates the displayed question after changing the slider"""
    if not quiz_data or "questions" not in quiz_data:
        return "No quiz available", gr.update(choices=[], value=None), ""
    
    questions = quiz_data.get("questions", [])
    idx = int(idx)
    if idx >= len(questions):
        return "Question not found", gr.update(choices=[], value=None), ""
    
    q = questions[idx]
    return q.get("question", ""), gr.update(choices=q.get("options", []), value=None), ""

def init_quiz(quiz_data, idx):
    """Initialises the quiz after the document is submitted"""
    print(f"DEBUG init_quiz: quiz_data type = {type(quiz_data)}, quiz_data = {quiz_data}")
    
    if not quiz_data or "questions" not in quiz_data:
        print("DEBUG: No quiz available!")
        return "No quiz available!", gr.update(choices=[], value=None), ""
    
    questions = quiz_data.get("questions", [])
    print(f"DEBUG: Number of questions = {len(questions)}")
    
    max_idx = len(questions) - 1
    idx = int(idx) if int(idx) <= max_idx else 0
    q = questions[idx]
    
    print(f"DEBUG: Question {idx}: {q.get('question', '')}")
    
    return (
        q.get("question", ""),
        gr.update(choices=q.get("options", []), value=None),
        ""
    )

def analyze(file):
    summary, translated, quiz, folder, quiz_data = process_document(file)
    return summary, translated, folder, quiz_data

def submit_answer(quiz_data, idx, answer):
    return check_answer(quiz_data, int(idx), answer)

# --- Gradio UI ---
with gr.Blocks(title="AI Document Insight Assistant") as app:
    gr.Markdown("# AI Document Insight Assistant")
    gr.Markdown("Analyse documents, receive summaries, translations and quizzes.")
    
    # Hidden state to store quiz data 
    quiz_state = gr.State()
    
    with gr.Tabs():
        # TAB 1: Analiza dokumentu
        with gr.Tab("📄 Document analysis"):
            with gr.Row():
                file_input = gr.File(label="Upload a file (.pdf, .docx, .png, .jpg, .jpeg, .tiff, .bmp)")
                submit_btn = gr.Button("Analyse", variant="primary")
            
            with gr.Row():
                summary_output = gr.Textbox(label="Summary (EN)", lines=10)
                translated_output = gr.Textbox(label="Translation (PL)", lines=10)
            
            result_folder_output = gr.Textbox(label="Folder with results", interactive=False)
            gr.Markdown("The files have been saved in the above folder.")
            
            submit_btn.click(
                analyze,
                inputs=file_input,
                outputs=[summary_output, translated_output, result_folder_output, quiz_state]
            )
        
        # TAB 2: Interactive quiz
        with gr.Tab("🎯 Quiz"):
            with gr.Row():
                start_quiz_btn = gr.Button("🚀 Start the quiz", variant="secondary")
            
            with gr.Row():
                question_idx = gr.Slider(minimum=0, maximum=20, step=1, value=0, label="Question number")
            
            question_text = gr.Textbox(label="Question", interactive=False)
            option_radio = gr.Radio(choices=[], label="Options", interactive=True)
            answer_btn = gr.Button("Check the answer", variant="primary")
            result_text = gr.Textbox(label="Result", interactive=False)
            
            # Przycisk uruchamiający quiz
            start_quiz_btn.click(
                init_quiz,
                inputs=[quiz_state, question_idx],
                outputs=[question_text, option_radio, result_text]
            )
            
            question_idx.change(
                update_question,
                inputs=[quiz_state, question_idx],
                outputs=[question_text, option_radio, result_text]
            )
            
            answer_btn.click(
                submit_answer,
                inputs=[quiz_state, question_idx, option_radio],
                outputs=result_text
            )

if __name__ == "__main__":

    app.launch()