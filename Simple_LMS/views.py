import collections
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect
from .utils import extract_text_from_pdf, generate_feedback_with_gpt
from .models import Solution, Homework
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from .utils import extract_text_from_pdf, generate_quiz_with_gpt, parse_quiz_content  # Import the function
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .utils import generate_feedback_with_gpt
from django.shortcuts import redirect
from .models import *
from django.http import HttpResponse
from .models import Note
from .utils import extract_text_from_pdf, generate_quiz_with_gpt



def generate_quiz_view(request, note_id):
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        return HttpResponse('Note not found.', status=404)

    try:
        pdf_path = note.file.path
        text = extract_text_from_pdf(pdf_path)
        quiz_raw_content = generate_quiz_with_gpt(text)
        quiz_content = parse_quiz_content(quiz_raw_content)

        if quiz_content is None:
            raise ValueError("Failed to parse the quiz content.")

        return render(request, 'quiz_template.html', {'quiz_content': quiz_content})
    except Exception as e:
        # If 'quiz_raw_content' hasn't been defined due to an earlier error, handle it.
        if 'quiz_raw_content' not in locals():
            quiz_raw_content = "No content. An error occurred during content generation."

        print(f"Error parsing quiz content: {e}")
        print(f"Raw content: {quiz_raw_content}")
        return HttpResponse('Failed to parse the quiz content.', status=500)
# Homepage
class HomePageView(TemplateView):
    template_name = 'index.html'

def check_answer(question_text, user_answer):
    # This is a placeholder function. You need to implement the logic to check
    # if 'user_answer' is correct for 'question_text' and return the correct answer text.
    correct_answer_text = "The correct answer"  # Fetch the correct answer based on your application logic
    is_correct = user_answer == correct_answer_text
    return is_correct, correct_answer_text


def is_correct_answer(question_id, user_answer):
    # Implement logic to determine if the user's answer is correct
    # Return a tuple (bool, str) indicating if the answer is correct and the correct answer text
    return True, "Correct answer text"


def submit_quiz_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', [])
            feedback_list = []
            score = 0
            total_questions = len(answers)

            for answer in answers:
                question_id = answer.get('questionId')
                user_answer = answer.get('answer')
                correct, correct_answer = is_correct_answer(question_id, user_answer)

                if correct:
                    score += 1
                    feedback_text = f"Correct! {generate_feedback_with_gpt('Good job!')}"
                else:
                    feedback_text = f"Incorrect! The correct answer was '{correct_answer}'. {generate_feedback_with_gpt('Please review your materials.')}"
                
                feedback_list.append({
                    'questionId': question_id,
                    'feedback': feedback_text
                })

            score_percentage = (score / total_questions) * 100 if total_questions else 0

            return JsonResponse({
                'feedback': feedback_list,
                'score': score_percentage,
                'message': f'You scored {score}/{total_questions} ({score_percentage}%)'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
# Login
class LoginPageView(TemplateView):
    template_name = 'login.html'

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.filter(email=email)
        if not user:
            messages.warning(request, 'Username and passowrd does not match')
            print('User does not exist')
            return render(request, self.template_name)

        username = user[0].username
        if (authenticate(request, username=username, password=password)):
            login(request, authenticate(request, username=username, password=password))
            messages.success(request, 'Login successful')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Username and passowrd does not match')
            return render(request, self.template_name)


@login_required
def upload_solution_view(request):
    if request.method == 'POST':
        # Assuming you have a form with 'homework_id' and the file field 'solution'
        homework_id = request.POST.get('homework_id')
        file = request.FILES.get('solution')
        homework = Homework.objects.get(id=homework_id)  # Get the homework instance

        # Save the file (Django handles the file storage)
        file_path = default_storage.save(file.name, file)
        full_file_path = default_storage.path(file_path)

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(full_file_path)

        # Generate feedback using GPT
# Inside your views.py, update the function call to:
        feedback = generate_feedback_with_gpt(extracted_text)


        # Create and save the solution instance with the feedback
        solution = Solution(
            student=request.user,
            course=homework.course,
            home_work=homework,
            file=file_path,  # Adjust based on your model fields
            gpt_feedback=feedback
        )
        solution.save()

        # Redirect to a confirmation page, showing feedback or back to homework list
        messages.success(request, 'Solution uploaded successfully. Feedback has been generated.')
        return redirect('homeworks_list')  # Adjust the redirect as per your URL configuration

# Logout
def logout_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'You are not logged in')
        return redirect('login')
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('/')


# Register
class RegisterPageView(TemplateView):
    template_name = 'register.html'

    def post(self, request):
        username = request.POST.get('studentid')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')

        if (password != confirm_password):
            messages.warning(request, 'Password and confirm password does not match')
            return render(request, self.template_name)

        user = User.objects.filter(username=username)
        if user:
            messages.warning(request, 'Student Id already exists')
            return render(request, self.template_name)

        user = User.objects.filter(email=email)
        if user:
            messages.warning(request, 'Email already exists')
            return render(request, self.template_name)

        user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname,
                                        last_name=lastname)
        user.save()
        messages.success(request, 'Registration successful')
        return redirect('login')


# Dashboard
class DashboardPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'dashboard.html'

    def get(self, request):
        notifications = Notification.objects\
                                    .select_related('course')\
                                    .filter(course__enrolls__student=request.user, is_active=True)\
                                    .order_by('-id')[0:5]
        homeworks = Homework.objects.prefetch_related('course')\
                                    .filter(course__enrolls__student=request.user, is_active=True)\
                                    .order_by('-id')[0:5]
        return render(request, self.template_name, {'notifications': notifications, 'homeworks': homeworks})


class CoursesPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'courses.html'
    
    def get(self, request):
        enrolls = Enrollment.objects.prefetch_related('course')\
                                    .filter(student=request.user)\
                                    .order_by('-id')
        return render(request, self.template_name, {'enrolls': enrolls})

class SolutionUpload(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        user = request.user
        homework_id = request.POST.get('homework_id')
        user_solution = request.FILES.get('solution')

        if not homework_id or not user_solution:
            messages.error(request, 'Homework ID or solution file is missing.')
            return redirect(reverse('homeworks'))

        try:
            homework = Homework.objects.get(id=homework_id)
        except Homework.DoesNotExist:
            messages.error(request, 'Invalid homework ID.')
            return redirect(reverse('homeworks'))

        # Save the uploaded file temporarily
        temp_file_path = user_solution.temporary_file_path() if hasattr(user_solution, 'temporary_file_path') else None
        if not temp_file_path:
            # If the file is small and doesn't have a temporary file, save it manually
            temp_file_name = default_storage.save(user_solution.name, ContentFile(user_solution.read()))
            temp_file_path = default_storage.path(temp_file_name)
        
        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(temp_file_path)
        
        if not extracted_text.strip():
            messages.error(request, "The document is empty or text couldn't be extracted.")
            return redirect(reverse('homeworks'))

        # Generate feedback using GPT
# Inside your views.py, update the function call to:
        feedback = generate_feedback_with_gpt(extracted_text)

        # Create and save the solution instance with the feedback
        solution = Solution(
            student=user,
            home_work=homework,
            course=homework.course,
            file=user_solution,  # Save the actual uploaded file
            gpt_feedback=feedback
        )
        solution.save()

        # Clean up if a temporary file was manually saved
        if 'temp_file_name' in locals():
            default_storage.delete(temp_file_name)

        messages.success(request, 'Solution uploaded successfully. Feedback has been generated.')
        return redirect(reverse('homeworks'))

class NotificationsPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'notifications.html'

    def get(self, request):
        notifications = Notification.objects\
                                    .select_related('course')\
                                    .filter(course__enrolls__student=request.user, is_active=True)\
                                    .order_by('-id')
        return render(request, self.template_name, {'notifications': notifications})


class VideosPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'videos.html'

    def get(self, request):
        videos = Video.objects.prefetch_related('course')\
                              .filter(course__enrolls__student=request.user)\
                              .order_by('-id')
        return render(request, self.template_name, {'videos': videos})
    

def ai_assistant(request):
    return render(request, 'aiassistant.html')


class HomeworksPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'homeworks.html'

    def get(self, request):
        homeworks = Homework.objects.prefetch_related('course')\
                                    .filter(course__enrolls__student=request.user)\
                                    .order_by('-id')
        student_solutions = Solution.objects.prefetch_related('home_work')\
                                    .filter(student=request.user)\
                                    .order_by('-id')
        homework_and_solution = collections.namedtuple('HomeworkAndSolution', ['homework', 'studentsolution'])
        homeworks_and_solutions = []
        for homework in homeworks:
            for solution in student_solutions:
                if solution.home_work == homework:
                    homeworks_and_solutions.append(homework_and_solution(homework, solution))
                    break
            else:
                homeworks_and_solutions.append(homework_and_solution(homework, None))

        return render(request, self.template_name, {"homeworks_and_solutions": homeworks_and_solutions})


class NotesPageView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'notes.html'

    def get(self, request):
        notes = Note.objects.prefetch_related('course')\
                            .filter(course__enrolls__student=request.user)\
                            .order_by('-id')
        return render(request, self.template_name, {'notes': notes})
