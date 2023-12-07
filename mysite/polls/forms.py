from django import forms
from django.forms import inlineformset_factory
from .models import Question, Choice

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('pub_date',)
        # fields = ('question_text',)

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = ('votes',)
        # fields = ('choice_text',)

PollFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=3,)

