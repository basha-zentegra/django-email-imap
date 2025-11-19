from imap_tools import MailBox
from django.http import JsonResponse

from django.shortcuts import render, redirect
from imap_tools import MailBox, AND

MY_EMAIL = ''
MY_APP_PASSWORD = ''

def inbox_page(request):
    return render(request, "inbox.html")

def login(request):
    global MY_EMAIL, MY_APP_PASSWORD
    if request.method == "POST":
        MY_EMAIL =request.POST.get("email") 
        MY_APP_PASSWORD = request.POST.get("pass")
        print(MY_EMAIL,MY_APP_PASSWORD)
        return redirect('home')
    else:
        return render(request, "login.html")

def get_emails(request):
    page = int(request.GET.get("page", 1))
    limit = 10
    start = (page - 1) * limit
    end = start + limit

    print(MY_EMAIL, MY_APP_PASSWORD,"<---INSIDE THE EMAIL FETCH API--->")

    with MailBox('imap.gmail.com').login(MY_EMAIL, MY_APP_PASSWORD, 'INBOX') as mailbox:

        # 1️⃣ Get all UIDs (old versions return oldest → newest)
        all_uids = mailbox.uids()

        # 2️⃣ Reverse manually to make newest first
        all_uids = list(reversed(all_uids))

        # 3️⃣ Slice for pagination
        page_uids = all_uids[start:end]

        messages = []

        if page_uids:
            # 4️⃣ Fetch specific UIDs
            for msg in mailbox.fetch(AND(uid=page_uids)):
                messages.append({
                    "subject": msg.subject,
                    "from": msg.from_,
                    "date": msg.date_str,
                    "text": msg.text
                })

    return JsonResponse(list(reversed(messages)), safe=False)


