# utils.py
import fitz  # PyMuPDF
import openai
from django.conf import settings
import logging
logger = logging.getLogger(__name__)
import re

from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from io import BytesIO

def save_feedback_as_pdf(solution, feedback_text):
    # Generate PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, feedback_text)  # Simplistic text insertion
    p.showPage()
    p.save()

    # Save PDF to a Django File Field
    file_content = ContentFile(buffer.getvalue())
    solution.gpt_feedback_file.save("feedback.pdf", file_content)




def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def generate_feedback_with_gpt(student_work):
    openai.api_key = settings.OPENAI_API_KEY

    # Craft a detailed and creative prompt for generating feedback and a score
    detailed_prompt = f"""
    You are an experienced educator tasked with providing detailed, constructive feedback on a student's assignment. Please review the student's work provided below and offer comprehensive feedback. Your feedback should highlight the strengths of the assignment, identify areas for improvement, and suggest specific steps the student can take to enhance their understanding and work quality. Additionally, please provide a preliminary score out of 100, considering the assignment's content, clarity, creativity, and adherence to the topic. The goal is to encourage the student's learning and growth.

    Here is the student's assignment:

    "{student_work}"

    Based on your expertise, please provide your detailed feedback and a preliminary score below:
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": detailed_prompt},
            ]
        )
        # Assuming the response structure aligns with what you need; adjust as necessary
        feedback = response.choices[0].message['content']
        return feedback
    except Exception as e:
        # Log more detailed error information, if available
        print(f"OpenAI API request failed: {str(e)}")
        return "Feedback generation failed due to an error."
    
logger = logging.getLogger(__name__)

def generate_quiz_with_gpt(text):
    openai.api_key = settings.OPENAI_API_KEY

    model = "gpt-3.5-turbo"  # GPT-4 Turbo preview model

    prompt = f"""
    Create a series of multiple-choice questions based on the following text. Each question should have four options (A, B, C, D), with one correct answer.

    Text:
    "{text}"

    Generate the quiz questions and answers below:
    """

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        quiz_content = response.choices[0].message['content'].strip()
        return quiz_content
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e}", exc_info=True)
        return f"Quiz generation failed due to an error. Details: {str(e)}"
def parse_quiz_content(raw_content):
    quiz_content = []
    questions = raw_content.strip().split('\n\n')  # Split by double newlines

    for question in questions:
        parts = question.split('\n')
        if not parts or "What" not in parts[0]:  # This checks if it's a question
            continue

        question_text = parts[0].strip()
        options = []
        correct_answer = None

        # Parse options and correct answer
        for part in parts[1:]:
            match = re.match(r'([ABCD])\.\s*(.*)', part)
            if match:
                option_letter, option_text = match.groups()
                options.append({'text': option_text, 'is_correct': False})
            if part.startswith('Answer:'):
                correct_answer = part.split()[-1].strip()

        # Mark the correct option
        if correct_answer:
            for option in options:
                if correct_answer in option['text']:
                    option['is_correct'] = True

        quiz_content.append({
            'question': question_text,
            'options': options,
        })

    return quiz_content