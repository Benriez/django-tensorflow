from datetime import datetime
from django.shortcuts import render, redirect


def index(request):
    if "next" in request.POST:
        anrede = request.POST.get("anrede")
        vorname = request.POST.get("vorname")
        nachname = request.POST.get("nachname")
        email_addresse = request.POST.get("email-addresse")
        
        str_geburtsdatum = request.POST.get("geburtsdatum")
        list_geburtsdatum = list(str_geburtsdatum.split("-"))
        list_geburtsdatum.reverse()
        format_geburtsdatum =""
        for l in list_geburtsdatum:  
            format_geburtsdatum += l +'.' 
        
        format_geburtsdatum = format_geburtsdatum[:-1]


        strasse = request.POST.get("strasse")
        print('strasse: ', strasse)
        hausnr = request.POST.get('hausnr')
        plz = request.POST.get("plz")
        ort = request.POST.get("ort")
        iban = request.POST.get('iban')
        bic = request.POST.get('bic')
        bankname = request.POST.get('bankname')

        request.session["anrede"] = anrede
        request.session["vorname"] = vorname
        request.session["nachname"] = nachname
        request.session["strasse"] = strasse
        request.session["hausnr"] = hausnr
        request.session["plz"] = plz
        request.session["ort"] = ort
        request.session["email"] = email_addresse
        request.session["geburtsdatum"] = format_geburtsdatum
        request.session["iban"] = iban
        request.session["bic"] = bic
        request.session["bankname"] = bankname


        # get BIC
        # get bank name
        return redirect("summary")

    return render(request, 'index.html')

  
def summary(request):
    # validate user data exists before accepting else -> redirect index
    return render(request, 'summary.html')