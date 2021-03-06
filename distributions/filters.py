import itertools

from django.db.models import Q
from django import forms
from .models import Course, Section
import django_filters

class CourseFilter(django_filters.FilterSet):
    class Meta:
        model = Course
        fields = {
            'department': ['icontains'],
            'number': ['contains'],
            'title': ['icontains'],
            'hours': ['exact'],
        }


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = {
            'course__department': ['icontains'],
            'course__number': ['contains'],
            'course__title': ['icontains'],
            'course__hours': ['exact'],
            'instructor': ['icontains'],
            'CRN': ['contains'],
            'average_GPA': ['exact', 'lt', 'gt'],
            'term__semester': ['iexact'],
            'term__year': ['exact'],
        }

class CourseFilterMulti(django_filters.FilterSet):
    multi = django_filters.CharFilter(label='', method='filter_multi', widget=
        forms.TextInput(attrs={'placeholder': 'Search', 
            'style': 'flex-grow:2; border:none;'}))
    search_fields = ['department', 'number', 'title']

    def filter_multi(self, qs, name, value):
        if value:
            q_parts = value.split()
            
            q_totals = Q()
            
            combinatorics = itertools.product([True, False], repeat=len(q_parts) - 1)
            possibilities = []
            for combination in combinatorics:
                i = 0
                one_such_combination = [q_parts[i]]
                for slab in combination:
                    i += 1
                    if not slab: # there is a join
                        one_such_combination[-1] += ' ' + q_parts[i]
                    else:
                        one_such_combination += [q_parts[i]]
                possibilities.append(one_such_combination)

            for p in possibilities:
                list1=self.search_fields
                list2=p
                perms = [zip(x,list2) for x in itertools.permutations(list1,len(list2))]
            
                for perm in perms:
                    q_part = Q()
                    for p in perm:
                        q_part = q_part & Q(**{p[0]+'__icontains': p[1]})
                    q_totals = q_totals | q_part

            qs = qs.filter(q_totals)
            
        return qs
        
    class Meta:
        model = Course
        fields = ['multi']
