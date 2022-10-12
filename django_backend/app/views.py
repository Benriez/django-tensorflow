from django.shortcuts import render, redirect


def index(request):
    if "next" in request.POST:
        anrede = request.POST.get("anrede")
        vorname = request.POST.get("vorname")
        nachname = request.POST.get("nachname")
        email_addresse = request.POST.get("email-addresse")
        geburtsdatum = request.POST.get("geburtsdatum")
        strasse = request.POST.get("strasse")
        plz = request.POST.get("plz")
        ort = request.POST.get("ort")
        iban = request.POST.get('iban')

        request.session["anrede"] = anrede
        request.session["vorname"] = vorname
        request.session["nachname"] = nachname
        request.session["strasse"] = strasse
        request.session["plz"] = plz
        request.session["ort"] = ort
        request.session["email"] = email_addresse
        request.session["geburtsdatum"] = geburtsdatum
        request.session["iban"] = iban

        # get BIC
        # get bank name
        return redirect("summary")

    return render(request, 'index.html')

  
def summary(request):
    # validate user data exists before accepting else -> redirect index
    return render(request, 'summary.html')