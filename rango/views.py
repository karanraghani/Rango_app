from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Page, Category, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime


def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]

	context_dict = {}
	context_dict['categories'] = category_list
	context_dict['pages'] = page_list
	
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	return render(request, 'rango/index.html', context_dict)

def about(request):
	return render(request, 'rango/about.html', {'visits': request.session['visits']})

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

@login_required
def add_category(request):
	form = CategoryForm()

	if request.method == "POST":
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print(form.errors)

	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug= category_name_slug)
	except Category.DoesNotExist:
		category = None

	form = PageForm()

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)

	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	registered = False
	user_form = UserForm()
	profile_form = UserProfileForm()

	if request.method == 'POST':
		user_form = UserForm(request.POST)
		profile_form = UserProfileForm(request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			#saving user info
			user = user_form.save()
			#hashing password
			user.set_password(user.password)
			user.save()

			#saving user profile info
			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True

		else:
			print("User Form Error:"+user_form.errors)
			print("Profile From Error:"+profile_form.errors)

	return render(request, 'rango/register.html', {'user_form': user_form, 
													'profile_form': profile_form,
													'registered': registered})

def login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username,password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))

			else:
				return HttpResponse("Your account has been disabled")

		else:
			print("Invalid Login Details {0},{1}".format(username,password))
			return HttpResponse("Invalid Credentials")

	else:
		return render(request,'rango/login.html', {})

@login_required
def logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

# Helper function 
def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	
	return val

# handling server side cookie
def visitor_cookie_handler(request):
	visits = int(get_server_side_cookie(request, 'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))

	last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')

	if (datetime.now()-last_visit_time).days > 0:
		visits = visits + 1
		request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = last_visit_cookie

	request.session['visits'] = visits

				










