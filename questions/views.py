from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from .models import *
from django.http import  JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from accounts.decorators import artist_required

# Create your views here.
def index(request):

  return render(request, "questions/index.html")

@login_required
def create(request):
    form = QuestionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        temp = form.save(commit=False)
        temp.user = request.user
        temp.save()
        return redirect("questions:index")
    context = {
        "form": form,
    }
    return render(request, "questions/create.html", context)

@login_required
def myquestion(request):

    # 문의 pk를 추적할 수 있도록, 첫번째 문의는 댓글작성이 되나
    # 두번째 문의부터 댓글작성이 안되는 현상 발생.
    my_questions = Question.objects.filter(user_id=request.user.pk)
    context = {
      "questions": my_questions,
    }

    return render(request, "questions/myquestion.html", context)

@login_required
def adminqna(request):
    if str(request.user.username) == str(get_user_model().objects.get(username="admin")):
        my_questions = Question.objects.filter(admin=0)

        context = {
          "questions": my_questions,
        }

        return render(request, "questions/adminqna.html", context)
    else:
        return redirect("accounts:login")

@login_required
def comment_create(request, question_pk):
    question_comment = get_object_or_404(Question, pk=question_pk)
    if request.user.is_authenticated:
        commentForm = CommentForm(request.POST)
        if commentForm.is_valid():
            comment = commentForm.save(commit=False)
            comment.question = question_comment
            comment.user = request.user
            comment.save()
            if comment.user.test:
                name = comment.user.creater_name
            elif comment.user.creater_name:
                name = comment.user.creater_name
            elif comment.user.username:
                name = comment.user.username
            context = {
              'content': comment.content,
              'userName': name,
              'created_at': comment.created_at
            }
            print(context)
        return JsonResponse(context)
    else:
        return redirect("accounts:login")