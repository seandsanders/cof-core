import json
from urllib import urlencode
from urllib2 import urlopen, Request as urlrequest
import urllib2
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from base64 import b64encode as base64
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
                        return redirect("evesso")

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
                    return redirect("evesso")
                else:
                    error = "Please Select your main Character (click it)"
            else:
                error = "Please add API Keys to all of your accounts"


    if (request.session.get("characters")):
        ctx["characters"] = request.session.get("characters")
    ctx["error"] = error
    return render(request, 'cof_register.html', ctx)


def about(request):
    ctx = {}
    return render(request, 'cof_about.html', ctx)


def ssologin(request):
    code = request.GET.get('code', None)

    clientid = settings.SSO_CLIENT_ID
    clientkey = settings.SSO_SECRET_KEY
    authorization = base64(clientid+":"+clientkey)
    redirect_url = settings.SSO_CALLBACK_URL


    if not code:
        base = "https://login.eveonline.com/oauth/authorize/?response_type=code"
        url = base + "&redirect_uri=" + redirect_url + "&client_id=" + clientid + "&scope="

        return redirect(url)
    else:
        data = {"grant_type": "authorization_code", "code": code}
        headers = {"Authorization": authorization}

        data = urlencode(data)
        rq = urlrequest("https://login.eveonline.com/oauth/token", data, headers)

        try:
            result = urlopen(rq)
            result = json.loads(result.read())
        except urllib2.HTTPError, e:
            r = e.read()
            return render(request, 'cof_register.html', {"error": "Your Login Token is invalid or expired. Please try again."})

        headers = {"Authorization": "Bearer " + result["access_token"], "Host": "login.eveonline.com"}

        rq = urlrequest("https://login.eveonline.com/oauth/verify", headers=headers)
        result = urlopen(rq)
        result = result.read()

        result = json.loads(result)

        if not result["CharacterID"]:
            return render(request, 'cof_register.html', {"error": "Cannot get a valid answer from CCP. Please try again."})

        try:
            char = Character.objects.get(charID=result["CharacterID"])
            char.profile.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, char.profile.user)
            token = request.session.get('appToken', False)
            if token:
                return redirect("applications:apply", token=token)
            return redirect("core:dashboard")
        except:
            return render(request, 'cof_register.html', {"error": "The selected Character is not in our Database. Please register using the link below."})