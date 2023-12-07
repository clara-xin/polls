# https://techincent.com/explained-django-inline-formset-factory-with-example/
# used this tutorial to add create new poll feature

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView, ListView, CreateView
from django.shortcuts import redirect
from django.urls import reverse



from .models import Choice, Question

from .forms import QuestionForm, ChoiceForm, PollFormSet

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_question_list'] = Question.objects.filter(
            pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
        return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_question_list'] = Question.objects.filter(
            pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
        return context


class AddPollView(generic.CreateView):
    form_class = QuestionForm
    template_name = "polls/add.html"
    def get_context_data(self, **kwargs):
        context = super(AddPollView, self).get_context_data(**kwargs)
        context['poll_formset'] = PollFormSet()
        context['latest_question_list'] = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
        return context
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        poll_formset = PollFormSet(self.request.POST)
        if form.is_valid() and poll_formset.is_valid():
            return self.form_valid(form, poll_formset)
        else:
            return self.form_invalid(form, poll_formset)
    def form_valid(self, form, poll_formset):
        self.object = form.save(commit=False)
        self.object.save()
        # saving Poll Instances
        polls_created = poll_formset.save(commit=False)
        for each in polls_created:
            each.question = self.object
            each.save()
        return redirect(reverse("polls:index"))
    def form_invalid(self, form, poll_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  poll_formset=poll_formset
                                  )
        )


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))