from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from core import postNotification
from core.apireader import validateKey, refreshKeyInfo
from core.models import UserProfile, ApiKey, Character
from core import views


def landing(request):
    context = {}
    return render(request, 'cof_home.html', context)

def register(request):
    if False:
        return views.register(request)
    ctx = {}
    error = None
    recruiterGrp, created = Group.objects.get_or_create(name='Recruiter')
    if request.method == "POST":
        if request.POST.get("action") == "addkey":
            if request.POST.get("keyID") and request.POST.get("vCode"):
                if int(request.POST.get("keyID")) > settings.MIN_API_ID:
                    charlist, error = validateKey(request.POST.get("keyID"), request.POST.get("vCode"))
                    if not error:
                        if request.session.get("characters"):
                            request.session["characters"].extend(charlist)
                            request.session.modified = True
                        else:
                            request.session["characters"] = charlist
                        if request.session.get("apis"):
                            request.session["apis"].append({"id": request.POST.get("keyID"), "vCode": request.POST.get("vCode")})
                            request.session.modified = True
                        else:
                            request.session["apis"] = [{"id": request.POST.get("keyID"), "vCode": request.POST.get("vCode")}]
                else:
                    error = "Please do not re-use old API keys"
        elif request.POST.get("action") == "done":
            if request.session.get("characters"):
                charlist = request.session.get("characters")
                mainChar = request.POST.get("mainChar")

                if mainChar and mainChar != "0":
                    mainChar = charlist[int(mainChar)-1]
                    newUser = User(username=slugify(mainChar["charName"]))
                    from django.db import IntegrityError
                    try:
                        newUser.save()
                    except IntegrityError as e:
                        return redirect("core:evesso")

                    newProfile = UserProfile.objects.get_or_create(user=newUser)[0]
                    try:
                        newProfile.save()
                    except:
                        pass
                    for api in request.session["apis"]:
                        try:
                            newKey = ApiKey.objects.get(keyID=api["id"], deleted=True)
                            newKey.deleted = False
                            newKey.vCode = api["vCode"]
                            newKey.profile = newProfile
                        except:
                            newKey = ApiKey(keyID = api["id"], vCode=api["vCode"], profile=newProfile)
                        newKey.save()
                        refreshKeyInfo(newKey, full=False)
                    newProfile.mainChar = Character.objects.get(charID=mainChar["charID"])
                    try:
                        newProfile.save()
                    except:
                        pass
                    postNotification(target=newUser, text="You have created your account", cssClass="success")
                    postNotification(target=recruiterGrp, text="<a href='"+reverse('core:playerProfile', kwargs={"profileName": slugify(newProfile)})+"'>"+unicode(newProfile)+"</a> created an account.", cssClass="info")
                    return redirect("core:evesso")
                else:
                    error = "Please Select your main Character (click it)"
            else:
                error = "Please add API Keys to all of your accounts"


    if (request.session.get("characters")):
        ctx["characters"] = request.session.get("characters")
    ctx["error"] = error
    return render(request, 'cof_register.html', ctx)