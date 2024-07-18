from calc.models import Rations
import django_filters 

class RationFilter(django_filters.FilterSet):


    class Meta:
        model = Rations
       # fields = ['pet_name','pet_info','ration_name']
        fields = {
            'pet_info': ['exact'],
            'ration_name': ['contains'],
            'ration_comment': ['contains'],
            'pet_name': ['contains'],
        }