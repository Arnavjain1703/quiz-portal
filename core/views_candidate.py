from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.views import generic, View
from . import forms
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render_to_response
from .models import Candidate, Instruction, Category, Test, Question
from .models import Candidate
from core.models import Category, Question, Instruction, Test, SelectedAnswer
import json
import itertools
from django.http import JsonResponse, Http404
import os
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
import datetime
from xhtml2pdf import pisa


def random_question(n, can_id, ques_id):
    a = [x for x in range(1, n + 1)]
    a = list(itertools.permutations(a))
    l = len(a)
    return a[can_id % l][ques_id % n]


class QuestionByCategory(generic.DetailView):
    template_name = 'candidate/question_by_category.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.has_key("email"):
            return redirect('signup')
        return super(QuestionByCategory, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        category_name = kwargs["category_name"]
        context_dict = {'category_name': category_name}

        try:
            category = Category.objects.get(category=category_name)
            total_question = Question.objects.filter(category=category).count()
            email = request.session["email"]
            id = kwargs["id"]

            if id not in range(1, total_question + 1):
                return redirect(reverse('category', kwargs={"category_name": category_name,
                                                            "id": 1}))
            candidate_id = Candidate.objects.get(email=email).id
            which_question = random_question(total_question, int(candidate_id), id)
            question = Question.objects.filter(category=category)[which_question - 1]
            context_dict["which_question"] = which_question
            context_dict['question'] = question
            context_dict["question_id"] = question.id
            context_dict['category'] = category
            context_dict["all_category"] = Category.objects.all()
            total_question_dict = []
            for i in range(1, total_question+1):
                total_question_dict.append(i)
            context_dict['total_question_dict'] = total_question_dict
        except Category.DoesNotExist:
            pass
        return render(self.request, self.template_name, context_dict)


class InstructionView(generic.ListView):
    template_name ='candidate/instructions.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.has_key("email"):
            return redirect('signup')
        return super(InstructionView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        instruction = Instruction.objects.all()
        category = Category.objects.all()[0]
        return render(request, self.template_name, {'instruction': instruction,
                                                    'category': category})


class CandidateRegistration(generic.ListView):
    form_class = forms.CandidateRegistration
    template_name ='candidate/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.has_key("email"):
            return redirect('home')
        return super(CandidateRegistration, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            print(name, email)
            candidate = Candidate.objects.get(name=name, email=email)
            if candidate:
                self.request.session['email'] = email
                self.request.session['name'] = name
                return redirect('home')
        return render(self.request, self.template_name, {'form': form})


class UserAnswerView(generic.ListView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            email = request.session["email"]
            candidate = Candidate.objects.get(email=email)
            option_number = request.GET["option_number"]
            question_id = request.GET["question_id"]
            question = Question.objects.get(id=int(question_id))
            try:
                object = SelectedAnswer.objects.get(email=candidate,
                                                    question_text=question
                                                    )
                object.selected_choice = int(option_number)
                object.save()
            except:
                object = SelectedAnswer.objects.create(email=candidate,
                                                    question_text=question,
                                                    selected_choice=int(option_number)
                                                       )
            data = {
                "candidate_answer": object.selected_choice
            }
            return JsonResponse(data)
        else:
            raise Http404


class DefaultOption(generic.ListView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            email = request.session["email"]
            candidate = Candidate.objects.get(email=email)

            question_id = request.GET["question_id"]
            question = Question.objects.get(id=int(question_id))
            candidate_answer = -1
            try:
                object = SelectedAnswer.objects.get(email=candidate,
                                                    question_text=question
                                                    )
                candidate_answer = object.selected_choice
            except:
                pass
            data = {
                "candidate_answer": candidate_answer
            }
            return JsonResponse(data)
        else:
            raise Http404





def logout(request):
    try:
        del request.session['email']
        del request.session['name']
    except:
        pass
    return redirect('signup')