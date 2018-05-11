from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Page, Category


def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]

	context_dict = {}
	context_dict['categories'] = category_list
	context_dict['pages'] = page_list
	
	return render(request, 'rango/index.html', context_dict)

def about(request):
	return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
	context_dict = {}
	try:
		#if category is not found then it retunrs DoesNotExist exception
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)

		context_dict['category'] = category
		context_dict['pages'] = pages

		# increasing views of category
		category.views += 1
	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None

	return render(request,'rango/category.html', context_dict)



