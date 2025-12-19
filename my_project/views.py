from imap_tools import MailBox
from django.http import JsonResponse
from django.shortcuts import render, redirect
from imap_tools import MailBox, AND
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def inbox_page(request):
    return render(request, "inbox.html")


# def get_emails(request):
#     page = int(request.GET.get("page", 1))
#     limit = 10
#     start = (page - 1) * limit
#     end = start + limit

#     MY_EMAIL = request.user.username
#     MY_APP_PASSWORD = request.user.last_name

#     with MailBox('imap.gmail.com').login(MY_EMAIL, MY_APP_PASSWORD, 'INBOX') as mailbox:

#         # 1️⃣ Get all UIDs (old versions return oldest → newest)
#         all_uids = mailbox.uids()

#         # 2️⃣ Reverse manually to make newest first
#         all_uids = list(reversed(all_uids))

#         # 3️⃣ Slice for pagination
#         page_uids = all_uids[start:end]

#         messages = []

#         if page_uids:
#             # 4️⃣ Fetch specific UIDs
#             for msg in mailbox.fetch(AND(uid=page_uids)):
#                 messages.append({
#                     "subject": msg.subject,
#                     "from": msg.from_,
#                     "date": msg.date_str,
#                     "text": msg.text
#                 })

#     return JsonResponse(list(reversed(messages)), safe=False)


# ---------- SIGNUP ----------
def signup_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        last_name = request.POST.get("last_name")

        if User.objects.filter(email=email).exists():
            messages.error(request, "email already taken.")
            return redirect("signup")

        user = User.objects.create_user(username=email,email=email, password=password, last_name = last_name)
        user.save()

         # Automatically log in the user
        login(request, user)

        messages.success(request, "Account created and logged in!")
        return redirect("home")  # redirect to home page
    return render(request, "signup.html")


# ---------- SIGNIN ----------
def signin_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("signin")

    return render(request, "signin.html")


# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    return redirect("signin")

########################################## ALL EMAILS ##############################################

@api_view(["GET"])
@permission_classes([IsAuthenticated])   # JWT Auth required
def get_emails(request):
    try:
        page = int(request.GET.get("page", 1))
        from_email = request.GET.get("from_email")
        limit = 10
        start = (page - 1) * limit
        end = start + limit
        
        MY_EMAIL = request.user.username
        MY_APP_PASSWORD = request.user.last_name  # you asked to keep this
        # TARGET_EMAIL = from_email

        with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD) as mailbox:

            mailbox.folder.set("INBOX")

            if from_email:
                uids = mailbox.uids(AND(from_=from_email))
            else:
                uids = mailbox.uids()

            uids = list(reversed(uids))  # newest first
            page_uids = uids[start:end]

            messages = []
            for msg in mailbox.fetch(AND(uid=page_uids)):
                messages.append({
                    "subject": msg.subject,
                    "from": msg.from_,
                    "date": msg.date_str,
                    "text": msg.text
                })

        return JsonResponse(messages, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    



@api_view(["GET"])
@permission_classes([IsAuthenticated])   # JWT Auth required
def get_sent_emails(request):
    try:
        page = int(request.GET.get("page", 1))
        from_email = request.GET.get("from_email")
        limit = 10
        start = (page - 1) * limit
        end = start + limit
        
        MY_EMAIL = request.user.username
        MY_APP_PASSWORD = request.user.last_name  # you asked to keep this
        # TARGET_EMAIL = from_email

        with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD) as mailbox:

            mailbox.folder.set("[Gmail]/Sent Mail")

            if from_email:
                uids = mailbox.uids(AND(to=from_email))
            else:
                uids = mailbox.uids()

            uids = list(reversed(uids))  # newest first
            page_uids = uids[start:end]

            messages = []
            for msg in mailbox.fetch(AND(uid=page_uids)):
                messages.append({
                    "subject": msg.subject,
                    "from": msg.from_,
                    "to": msg.to,
                    "date": msg.date_str,
                    "text": msg.text
                })
            
            messages = list(reversed(messages))

        return JsonResponse(messages, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

################################----ONLY INBOX----#######################################

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])   # JWT Auth required
# def get_emails(request):
#     try:
#         page = int(request.GET.get("page", 1))
#         from_email = request.GET.get("from_email")   # <-- get sender filter
#         limit = 10
#         start = (page - 1) * limit
#         end = start + limit

#         MY_EMAIL = request.user.username
#         MY_APP_PASSWORD = request.user.last_name  # you asked to keep this
#         # TARGET_EMAIL = "noreply@github.com"

#         with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD, "INBOX") as mailbox:

#             # ---- FILTER FIRST IF EMAIL PROVIDED ----
#             if from_email:
#                 filtered_msgs = list(mailbox.fetch(AND(from_=from_email)))
#             else:
#                 filtered_msgs = list(mailbox.fetch())  # no filter

#             filtered_msgs = list(reversed(filtered_msgs))

#             paginated = filtered_msgs[start:end]

#             messages = []
#             for msg in paginated:
#                 messages.append({
#                     "subject": msg.subject,
#                     "from": msg.from_,
#                     "date": msg.date_str,
#                     "text": msg.text,
#                 })

#         return JsonResponse(messages, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
    
# from imap_tools import MailBox, AND
# from django.http import JsonResponse
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated


#------------------- FETCHING ALL AND THEN DOING PAGINATION -------------

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_emails(request):
#     try:
#         page = int(request.GET.get("page", 1))
#         from_email = request.GET.get("from_email")
#         limit = 10
#         start = (page - 1) * limit
#         end = start + limit

#         MY_EMAIL = request.user.username
#         MY_APP_PASSWORD = request.user.last_name

#         with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD) as mailbox:

#             # --- Fetch inbox ---
#             mailbox.folder.set("INBOX")
#             if from_email:
#                 inbox_msgs = list(mailbox.fetch(AND(from_=from_email)))
#             else:
#                 inbox_msgs = list(mailbox.fetch())

#             # --- Fetch sent mail ---
#             # Gmail sent folder is usually "[Gmail]/Sent Mail"
#             mailbox.folder.set("[Gmail]/Sent Mail")
#             if from_email:
#                 sent_msgs = list(mailbox.fetch(AND(to=from_email)))
#             else:
#                 sent_msgs = list(mailbox.fetch())

#             print("SENT_MESAGES", sent_msgs)


#             # Merge inbox + sent
#             all_msgs = inbox_msgs + sent_msgs
#             print("COUNT OF ALL MESSAGES IT FETCHS",all_msgs.count())

#         # Sort (desc by date)
#         all_msgs = list(reversed(all_msgs))
        

#         # Pagination
#         paginated = all_msgs[start:end]

#         messages = []
#         for msg in paginated:
#             messages.append({
#                 "subject": msg.subject,
#                 "from": msg.from_,
#                 "to": msg.to,
#                 "date": msg.date_str,
#                 "text": msg.text,
#                 "folder": "INBOX" if msg in inbox_msgs else "SENT",
#             })

#         return JsonResponse(messages, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
    

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_emails(request):
#     try:
#         page = int(request.GET.get("page", 1))
#         from_email = request.GET.get("from_email")
#         limit = 10
#         start = (page - 1) * limit
#         end = start + limit

#         MY_EMAIL = request.user.username
#         MY_APP_PASSWORD = request.user.last_name

#         with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD) as mailbox:

#             # --- Fetch inbox ---
#             mailbox.folder.set("INBOX")
#             if from_email:
#                 inbox_msgs = list(mailbox.fetch(AND(from_=from_email)))
#             else:
#                 inbox_msgs = list(mailbox.fetch())

#             # --- Fetch sent mail ---
#             # Gmail sent folder is usually "[Gmail]/Sent Mail"
#             mailbox.folder.set("[Gmail]/Sent Mail")
#             if from_email:
#                 sent_msgs = list(mailbox.fetch(AND(to=from_email)))
#             else:
#                 sent_msgs = list(mailbox.fetch())

#             # Merge inbox + sent
#             all_msgs = inbox_msgs + sent_msgs

#         # Sort (desc by date)
#         all_msgs = list(reversed(all_msgs))
        

#         # Pagination
#         paginated = all_msgs[start:end]

#         messages = []
#         for msg in paginated:
#             messages.append({
#                 "subject": msg.subject,
#                 "from": msg.from_,
#                 "to": msg.to,
#                 "date": msg.date_str,
#                 "text": msg.text,
#                 "folder": "INBOX" if msg in inbox_msgs else "SENT",
#             })

#         return JsonResponse(messages, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

    # GARBAGE 
# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def get_emails(request):
#     try:
#         page = int(request.GET.get("page", 1))
#         from_email = request.GET.get("from_email")
#         limit = 10

#         MY_EMAIL = request.user.username
#         MY_APP_PASSWORD = request.user.last_name

#         def fetch_page(mailbox, folder_name, criteria, page, limit):
#             mailbox.folder.set(folder_name)

#             # IMAP fetch newest → oldest
#             msgs = mailbox.fetch(criteria, reverse=True)

#             # skip first (page-1)*limit messages
#             start = (page - 1) * limit
#             end = start + limit

#             results = []
#             for idx, msg in enumerate(msgs):
#                 if idx < start:
#                     continue
#                 if idx >= end:
#                     break
#                 results.append(msg)

#             return results

#         with MailBox("imap.gmail.com").login(MY_EMAIL, MY_APP_PASSWORD) as mailbox:
#             # INBOX
#             inbox_criteria = AND(from_=from_email) if from_email else AND(all=True)
#             inbox_msgs = fetch_page(mailbox, "INBOX", inbox_criteria, page, limit)

#             # SENT folder
#             sent_criteria = AND(to=from_email) if from_email else AND(all=True)
#             sent_msgs = fetch_page(mailbox, "[Gmail]/Sent Mail", sent_criteria, page, limit)

#         # merge inbox + sent and sort by date
#         all_msgs = sorted(inbox_msgs + sent_msgs, key=lambda x: x.date, reverse=True)

#         messages = []
#         for msg in all_msgs:
#             messages.append({
#                 "subject": msg.subject,
#                 "from": msg.from_,
#                 "to": msg.to,
#                 "date": msg.date_str,
#                 "text": msg.text,
#                 "folder": "INBOX" if msg.folder == "INBOX" else "SENT",
#             })

#         return JsonResponse(messages, safe=False)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



# def sent_emails(request):
#     with MailBox('imap.gmail.com').login('basha.zentegra@gmail.com', 'zhvi irpe vhfl gleo') as mailbox:

#         mailbox.folder.set('[Gmail]/Sent Mail')
#         messages = mailbox.fetch(criteria=AND(to="abdul@zentegra.com"))
#         for i in messages:
#             print(i.subject)

#         return list(messages)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib


# def send_email(request):
#     try:
#         # Extract fields from POST body
#         to_email = "basha.abdulbari@gmail.com"
#         subject = "Vanakkam da mapla"
#         message = "Varta mame durrr"
#         # attachments = request.FILES.getlist("attachments") if "attachments" in request.FILES else []

#         if not to_email:
#             return JsonResponse({"error": "Recipient email 'to' is required"}, status=400)

#         # Auth from user model (same as your IMAP logic)
#         MY_EMAIL = "basha.zentegra@gmail.com"
#         MY_APP_PASSWORD = "zhvi irpe vhfl gleo"  # Gmail App Password

#         # ---- Build Email ----
#         msg = MIMEMultipart()
#         msg["From"] = MY_EMAIL
#         msg["To"] = to_email
#         msg["Subject"] = subject

#         # Body
#         msg.attach(MIMEText(message, "plain"))

#         # ---- Attach files (optional) ----
#         # for file in attachments:
#         #     part = MIMEApplication(file.read(), Name=file.name)
#         #     part["Content-Disposition"] = f'attachment; filename="{file.name}"'
#         #     msg.attach(part)

#         # ---- Send via Gmail SMTP ----
#         with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
#             smtp.starttls()
#             smtp.login(MY_EMAIL, MY_APP_PASSWORD)
#             smtp.send_message(msg)

#         return JsonResponse({"status": "Email sent successfully"})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_email(request):
    try:
        # Extract fields from POST body
        to_email = request.data.get("to")
        cc_emails = request.data.get("cc", "")
        bcc_emails= request.data.get("bcc", "")
        subject = request.data.get("subject", "")
        message = request.data.get("message", "")
        attachments = request.FILES.getlist("attachments") if "attachments" in request.FILES else []

        if not to_email:
            return JsonResponse({"error": "Recipient email 'to' is required"}, status=400)
        
        # Support comma-separated or list-based inputs
        def normalize(recipients):
            if not recipients:
                return []
            if isinstance(recipients, list):
                return recipients
            return [email.strip() for email in recipients.split(",")]
        
        cc_list = normalize(cc_emails)
        bcc_list = normalize(bcc_emails)

        # Auth from user model (same as your IMAP logic)
        MY_EMAIL = request.user.username
        MY_APP_PASSWORD = request.user.last_name  # Gmail App Password

        # ---- Build Email ----
        msg = MIMEMultipart()
        msg["From"] = MY_EMAIL
        msg["To"] = to_email
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject

        # Body
        msg.attach(MIMEText(message, "plain"))

        # ---- Attach files (optional) ----
        for file in attachments:
            part = MIMEApplication(file.read(), Name=file.name)
            part["Content-Disposition"] = f'attachment; filename="{file.name}"'
            msg.attach(part)

        # ---- Send via Gmail SMTP ----
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(MY_EMAIL, MY_APP_PASSWORD)
            smtp.send_message(msg)
            # smtp.sendmail(MY_EMAIL, all_recipients, msg.as_string())

        return JsonResponse({"status": "Email sent successfully"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)