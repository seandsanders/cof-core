from django.shortcuts import redirect, render


def landing(request):
	context = {}
	return render(request, 'cof_home.html', context)