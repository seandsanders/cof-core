from django.shortcuts import redirect, render


def landing(request):
	context = {}
	if request.user.is_authenticated():
		return redirect("core:dashboard")
	return render(request, 'cof_home.html', context)