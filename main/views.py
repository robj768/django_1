import urllib
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.http import HttpResponse, HttpResponseRedirect
from main.models import Category, Page
from main.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
# Create your views here.

def category(request, category_name_url):
	#Request our context from the request passed to us.
	context = RequestContext(request)

	# Change underscores in the category name to spaces.
	# URLs don't handle spaces well, so we encode them as underscores.
	# We can then simply replace the underscores with spaces again to get the name.
	category_name = category_name_url.replace('_', ' ')

	# Create a context dictionary which we can pass to the template rendering engine.
	# We start by containing the name of the category passed by the user.
	context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

	try:
		# Can we find a category with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(name = category_name)

		# Retrieve all of the associated pages.
		# Note that filter returns >= 1 model instance
		pages = Page.objects.filter(category = category)

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	return render_to_response('main/category.html', context_dict, context)



def main(request):
	# Testing cookies through webbrowser
	request.session.set_test_cookie()

	#Request the context of the request.
	#The context contains information such as the client's machine details, for example.
	context = RequestContext(request)

	#Construct a dictionary to pass to the template engine as its context.
	#Note the key boldmessage is the same as {{ boldmessage }} in the template!
	context_list = Category.objects.order_by('-name')[:8]
	context_dict = {'categories': context_list}

	# We loop through each category returned, and create a URL attribute.
	# This attribute stores an encoded URL (e.g. spaces replaced with underscores).
	for category in context_list:
		category.url = category.name.replace(' ', '_')

	# Obtain our Response object early so we can add cookie information.
	response = render_to_response('main/main.html', context_dict, context)

	# Get the number of visits to the site. 
	# We use the COOKIES.get() function to obtain the visits cookie.
	# If the cookie exists, the value returned is casted to an integer.
	# If the cookie doesn't exist, we default to zero and cast that.
	visits = int(request.COOKIES.get('visits', '0'))

	# Does the cookie last_visit exist?
	if 'last_visit' in request.COOKIES:
		last_visit = request.COOKIES['last_visit']
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		if(datetime.now() - last_visit_time).days > 0:
			response.set_cookie('visits', visits + 1)
			response.set_cookie('last_visit', datetime.now())
	else:
		response.set_cookie('last_visit', datetime.now())


	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits', 0)

		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

	#Return a rendered response to send to the client.
	return response


def contact(request):
	return HttpResponse('contact us <a href="/main/">main</a>')


def add_category(request):
	# Get the context from the request.
	context = RequestContext(request)

	# HTTP POST? documentation = 
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save it in the database
			form.save(commit = True)

			# Now call the index() view.
			# The user will be shown the homepage.
			return main(request)
		else:
			# The supplied form contained errors, print them in the console
			print (form.errors)
	else:
		# If the request is not a POST, display the form to enter details.
		form = CategoryForm()

	# Bad form (or form details), no form supplied
	# Render the form with error messages (if any).
	return render_to_response('main/add_category.html', {'form': form}, context)



def add_page(request, category_name_url):
	context = RequestContext(request)

	#category_name = decode_url(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			# This time we cannot commit straight away.
			# Not all fields are automatically populated!
			page = form.save(commit=False)

			# Retrieve the associated Category object so we can add it.
			# Wrap the code in a try block - check if the category actually exists!
			try:
				cat = Category.objects.get(name=category_name)
				page.category = cat
			except Category.DoesNotExist:
				# If we get here, the category does not exist.
				# Go back and render the add category form as a way of saying the category does not exist.
				return render_to_response('main/add_category.html', {}, context)

			# Also, create a default value for the number of views.
			page.views = 0

			# With this, we can then save our new model instance.
			page.save()

			# Now that the page is saved, display the category instead.
			return category(request, category_name_url)
		else:
			print (form.errors)
	else:
		form = PageForm()

	return render_to_response( 'main/add_page.html',
			{'category_name_url': category_name_url,
			 'form': form}, context)


def register(request):
	# Proving that test_cookie in browser is working through condition request
	#if request.session.test_cookie_worked():
	#	print ('>>> TEST COOKIE WORKED!')
	#	request.session.delete_test_cookie()
	#else:
	#	print('FAILED TEST!')

	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data = request.POST)
		profile_form = UserProfileForm(data = request.POST)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves, we set commit=False.
			# This delays saving the model until we're ready to avoid integrity problems.
			profile = profile_form.save(commit = False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance.
			profile.save()

			# Updating registered variable
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to the user.
		else:
			print(user_form.errors, profile_form.errors)

	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	return render(request,
		'main/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
			#  We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
			#  because the request.POST.get('<variable>') returns None, if the value does not exist,
			#  while the request.POST['<variable>'] will raise key error exception
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username = username, password = password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user
		# with matching credentials was found.
		if user:
			# Is the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/main/')
			else:
				return HttpResponse('Your Mapper acount is disabled.')
		else:
			print('Invalid login details: {0}, {1}'.format(username, password))
			return HttpResponse('Invalid login details supplied')

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the
		# blank dictionary object...
		return render(request, 'main/login.html', {})

@login_required
def restricted(request):
	return HttpResponse('Since you´re logged in, you can see this text!')


@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/main/')

@login_required
def like_category(request):

	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']

	likes = 0
	if cat_id:
		cat = Category.objects.get(id = int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes = likes
			cat.save()

	return HttpResponse(likes)



def get_category_list(max_results = 0, starts_with = ''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith = starts_with)

	if cat_list and max_results > 0:
		if cat_list.count() > max_results:
			cat_list = cat_list[: max_results]

	return cat_list


def suggest_category(request):
	cat_list = []
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']

	cat_list = get_category_list(8, starts_with)

	return render(request, "main/cats.html", {"cat_list": cat_list})


@login_required
def auto_add_page(request):
	cat_id = None
	url = None
	title = None
	context_dict = {}
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		url = request.GET['url']
		title = request.GET['title']
		if cat_id:
			category = Category.objects.get(id=int(cat_id))
			p = Page.objects.get_or_create(category=category, title=title, url=url)

			pages = Page.objects.filter(category=category).order_by('-views')

			# Adds our results list to the template context under name pages.
			context_dict['pages'] = pages

	return render(request, 'main/page_list.html', context_dict)









