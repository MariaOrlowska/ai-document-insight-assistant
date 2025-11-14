import os
import json
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
from openai import AzureOpenAI

# create client once
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def generate_summary(text: str, language: str = "en") -> str:
    """
    Generate an advanced, exam-focused summary for AI-102 using official Azure documentation as reference.
    language="en" forces English output.
    """
    system = (
        "You are an expert Microsoft AI-102 exam tutor. "
        "You create concise, highly focused summaries for exam preparation. "
        "You know the AI-102 exam objectives in detail and are familiar with Azure AI services, best practices, "
        "architecture patterns, and design principles. "
        "You reference official Azure documentation when relevant."
    )

    user_prompt = (
        f"Summarize the following content in {'English' if language=='en' else language} "
        "with a strong focus on topics that appear in the Microsoft AI-102 exam. "
        "Your summary should include:\n"
        "1. Key concepts and definitions relevant to AI-102.\n"
        "2. Important Azure AI services and their use cases.\n"
        "3. Recommended design patterns, best practices, and architecture tips.\n"
        "4. Typical exam scenarios or question types.\n"
        "5. References to official Azure documentation where appropriate.\n\n"
        "Output format:\n"
        "- Bullet points (10-15) or short paragraphs (max 8).\n"
        "- Use clear, concise, study-friendly language.\n"
        "- Do NOT add commentary, opinions, or filler text.\n\n"
        f"Content to summarize:\n{text}"
    )

    resp = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2000,
        temperature=0.8,
    )
    try:
        return resp.choices[0].message.content.strip()
    except Exception:
        return getattr(resp, "content", str(resp)).strip()

def translate_to_polish(text: str) -> str:
    prompt = f"Translate the following text into Polish:\n\n{text}"
    resp = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.6,
    )
    return resp.choices[0].message.content.strip()

def generate_quiz(text: str, num_questions=25) -> list:
    """Generate quiz as list of question dicts with structure: {question, options, correct_answer}"""
    prompt = f"Generate {num_questions} test questions from the text below in JSON format (a list of objects with the following fields: question, options (a list of 4 strings), correct_answer). Return ONLY valid JSON, no markdown, no extra text:\n\n{text}"
    
    resp = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.2,
    )
    quiz_text = resp.choices[0].message.content.strip()
    
    print(f"DEBUG generate_quiz raw response (first 500 chars):\n{quiz_text[:500]}\n")
    
    # Parse JSON from response
    try:
        # Extract JSON from markdown code block if present
        if "```json" in quiz_text:
            quiz_text = quiz_text.split("```json")[1].split("```")[0].strip()
        elif "```" in quiz_text:
            quiz_text = quiz_text.split("```")[1].split("```")[0].strip()
        
        print(f"DEBUG after extraction (first 500 chars):\n{quiz_text[:500]}\n")
        
        quiz_data = json.loads(quiz_text)
        
        # ensure it's a list
        if isinstance(quiz_data, dict) and "questions" in quiz_data:
            result = quiz_data["questions"]
        elif isinstance(quiz_data, list):
            result = quiz_data
        else:
            print(f"DEBUG: Unexpected structure type: {type(quiz_data)}")
            result = []
        
        print(f"DEBUG: Successfully parsed {len(result)} questions")
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response:\n{quiz_text}\n")
        return []
