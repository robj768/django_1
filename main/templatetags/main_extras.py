from django import template
from main.models import Category

register = template.Library()

@register.inclusion_tag('main/cats.html')
def get_cagtegory_list(cat = None):
	return {'cats' : Category.objects.all(), 'act_act' : cat}


