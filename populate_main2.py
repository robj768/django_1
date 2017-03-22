import os

def populate_2():
	real_estate_cat = add_cat('Real Estate')

	add_page(cat = real_estate_cat,
		title = 'Zillow',
		url = 'https://www.zillow.com')

	add_page(cat = real_estate_cat,
		title = 'Trulia',
		url = 'https://www.trulia.com')

	add_page(cat = real_estate_cat,
		title = 'VTS',
		url = 'https://www.vts.com')

	# Print out what we have added to the user.
	for c in Category.objects.all():
		for p in Page.objects.filter(category=c):
			print ("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views = 0):
	p = Page.objects.get_or_create(category = cat, title = title, url = url, views = views)[0]
	return p

def add_cat(name):
	c = Category.objects.get_or_create(name = name)[0]
	return c

if __name__ == '__main__':
	print('Starting main population_2 script......')
	import django
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango.settings')
	django.setup()
	from main.models import Category, Page
	populate_2()