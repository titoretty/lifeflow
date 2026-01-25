from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from . models import *
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.http import HttpResponseBadRequest
import re


# Create your views here.
def welcome(request):
    return render(request,'welcome.html')

def index(request):
    notif_count = 0

    if request.session.get('user_id'):
        notif_count = Notification.objects.filter(
            user_id=request.session['user_id'],
            is_read=False
        ).count()

    return render(request, 'index.html', {
            'notif_count': notif_count
    })
def user_register(request):
    return render(request,'user/user_register.html')
def register(request):
    if request.method == 'POST':

        # 🔹 Get form data
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        district = request.POST.get('district')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')

        # ================= BASIC REQUIRED CHECK =================
        if not all([full_name, email, phone, password, cpassword,
                    address, city, district, gender, blood_group]):
            messages.error(request, "All fields are required")
            return render(request, 'user/user_register.html')

        # ================= EMAIL VALIDATION =================
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, "Enter a valid email address")
            return render(request, 'user/user_register.html')

        # ================= PHONE VALIDATION =================
        if not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, "Enter a valid 10-digit mobile number")
            return render(request, 'user/user_register.html')

        # ================= PASSWORD VALIDATION =================
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, 'user/user_register.html')

        if password != cpassword:
            messages.error(request, "Passwords do not match")
            return render(request, 'user/user_register.html')

        # ================= DUPLICATE CHECK =================
        if user_registerdb.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'user/user_register.html')

        if user_registerdb.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered")
            return render(request, 'user/user_register.html')

        # ================= SAVE USER =================
        user_registerdb.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            password=make_password(password),
            address=address,
            city=city,
            district=district,
            gender=gender,
            blood_group=blood_group,
            status=1
        )
        request.session['new_user'] = True

        messages.success(request, "Registration successful! Please login.")
        return redirect('user_login')

    return render(request, 'user/user_register.html')
# def user_login(request):
#     if request.method == "POST":
#         email = request.POST.get("email").strip()
#         password = request.POST.get("password")
#
#         try:
#             user = user_registerdb.objects.get(email=email)
#             if check_password(password, user.password):
#                 # Store user ID in session
#                 request.session['user_id'] = user.id
#                 request.session['user_name'] = user.full_name
#                 return redirect("slogan")  # your page after login
#             else:
#                 messages.error(request, "Invalid password")
#         except user_registerdb.DoesNotExist:
#             messages.error(request, "User not found. Please register.")
#
#     return render(request, "user/user_login.html")

# def user_login(request):
#     if request.method == "POST":
#         email = request.POST.get("email").strip()
#         password = request.POST.get("password")
#
#         try:
#             user = user_registerdb.objects.get(email=email)
#
#             if check_password(password, user.password):
#                 request.session['user_id'] = user.id
#                 request.session['user_name'] = user.full_name
#
#                 # 🔥 CORE LOGIC
#                 if request.session.get('new_user'):
#                     del request.session['new_user']
#                     return redirect("slogan")   # ✅ only first time
#                 else:
#                     return redirect("index")     # ❌ no slogan
#
#             else:
#                 messages.error(request, "Invalid password")
#
#         except user_registerdb.DoesNotExist:
#             messages.error(request, "User not found. Please register.")
#
#     return render(request, "user/user_login.html")
# def user_login(request):
#     if request.method == "POST":
#         email = request.POST.get("email").strip()
#         password = request.POST.get("password")
#
#         try:
#             user = user_registerdb.objects.get(email=email)
#
#             if check_password(password, user.password):
#
#                 request.session.flush()   # 🔥 clear old user FIRST
#
#                 request.session['user_id'] = user.id
#                 request.session['user_name'] = user.full_name
#
#                 if request.session.get('new_user'):
#                     return redirect("slogan")
#                 else:
#                     return redirect("index")
#
#             else:
#                 messages.error(request, "Invalid password")
#
#         except user_registerdb.DoesNotExist:
#             messages.error(request, "User not found. Please register.")
#
#     return render(request, "user/user_login.html")
#
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        password = request.POST.get("password")

        try:
            user = user_registerdb.objects.get(email=email)

            if check_password(password, user.password):

                # ❌ NEVER flush here
                # request.session.flush()

                # clear only login-related keys
                request.session.pop('user_id', None)
                request.session.pop('user_name', None)

                # set session
                request.session['user_id'] = user.id
                request.session['user_name'] = user.full_name

                # ✅ NEW USER LOGIC (WORKS 100%)
                if request.session.get('new_user') is True:
                    request.session.pop('new_user')  # one-time use
                    return redirect("slogan")

                return redirect("index")

            else:
                messages.error(request, "Invalid password")

        except user_registerdb.DoesNotExist:
            messages.error(request, "User not found. Please register.")

    return render(request, "user/user_login.html")

# def slogan(request):
#     return render(request, "user/slogan.html")
def slogan(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first")
        return redirect('user_login')

    try:
        user = user_registerdb.objects.get(id=user_id)
    except user_registerdb.DoesNotExist:
        messages.error(request, "Session invalid. Please login again.")
        return redirect('user_login')

    if request.method == 'POST':
        # Get form data (you can improve this with forms later)
        last_donation = request.POST.get('last_donation_date')
        eligibility = request.POST.get('eligibility') == 'on'  # checkbox example
        weight = request.POST.get('weight') == 'on'
        emergency = request.POST.get('emergency') == 'on'

        # Update fields
        if last_donation:
            user.last_donation_date = last_donation
        user.is_eligible_now = eligibility
        user.weight_above_50kg = weight
        user.ready_for_emergency = emergency

        user.save()

        messages.success(request, "Thank you! Your donation readiness has been saved.")

        return redirect('index')  # ← MOST IMPORTANT CHANGE
        # or: return redirect('/')        # if index is the root url

    # GET → show form
    return render(request, "user/slogan.html", {
        'user': user
    })

def logout_view(request):
    request.session.flush()  # or del request.session['user_id']
    messages.success(request, "You have been logged out.")
    return redirect('welcome')

def about(request):
    return render(request,'about.html')
def header(request):
    return render(request,'header.html')





def hos_register(request):
    if request.method == "POST":
        hospital_name = request.POST.get('hospitalName')
        reg_no = request.POST.get('registrationNumber')
        hospital_type = request.POST.get('hospitalType')
        district = request.POST.get('district')
        address = request.POST.get('address')
        contact = request.POST.get('contactNumber')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        blood_bank = request.POST.get('bloodBankAvailability') == 'on'
        blood_groups = request.POST.getlist('blood_groups')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('hos_register')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        Hospital.objects.create(
            user=user,
            hospital_name=hospital_name,
            registration_number=reg_no,
            hospital_type=hospital_type,
            district=district,
            address=address,
            contact_number=contact,
            email=email,
            blood_bank_available=blood_bank,
            supported_blood_groups=",".join(blood_groups),
            is_approved=False  # 🔒 WAIT ADMIN
        )

        messages.success(
            request,
            "Hospital registered successfully. Await admin approval."
        )
        return redirect('hos_login')

    return render(request, 'hospital/hos_register.html')

# def demo(request):
#     return render(request,'hospital/demo.html')
# def hos_login(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             return redirect('hos_index.css')   # change to dashboard if needed
#         else:
#             messages.error(request, "Invalid username or password")
#
#     return render(request, 'hospital/hos_login.html')
def hos_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            try:
                hospital = Hospital.objects.get(user=user)
            except Hospital.DoesNotExist:
                messages.error(request, "No hospital account found")
                return redirect('hos_login')

            if not hospital.is_approved:
                messages.error(
                    request,
                    "Your hospital is not approved by admin yet."
                )
                return redirect('hos_login')

            login(request, user)
            request.session['hospital_id'] = hospital.id
            return redirect('hos_index')

        messages.error(request, "Invalid username or password")

    return render(request, 'hospital/hos_login.html')
NEARBY_DISTRICTS = {
    "Ernakulam": ["Thrissur", "Idukki", "Alappuzha"],
    "Kollam": ["Alappuzha", "Pathanamthitta", "Thiruvananthapuram"],
    "Thiruvananthapuram": ["Kollam"],
    "Alappuzha": ["Kollam", "Kottayam", "Ernakulam"],
    "Thrissur": ["Ernakulam", "Palakkad"],
    "Kottayam": ["Pathanamthitta", "Alappuzha"],
}
# def donate(request):
#     if not request.session.get('user_id'):
#         return redirect('user_login')
#
#     return render(request, 'user/donate.html')
def donate(request):
    # 🔐 Login check
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(user_registerdb, id=user_id)

    today = now().date()
    can_donate = True
    next_eligible_date = None

    # 🩸 90 DAYS RULE
    if user.last_donation_date:
        next_eligible_date = user.last_donation_date + timedelta(days=90)
        if today < next_eligible_date:
            can_donate = False

    return render(request, 'user/donate.html', {
        'user': user,
        'can_donate': can_donate,
        'next_eligible_date': next_eligible_date
    })
def hospital_list(request):
    if request.method != "POST":
        return redirect('donate')

    method = request.POST.get("method", "").strip().lower()  # 'manual' or 'live'
    district_input = request.POST.get("district", "").strip()  # exact district name

    if not district_input:
        # fallback: show all approved blood banks
        hospitals = Hospital.objects.filter(
            blood_bank_available=True,
            is_approved=True
        ).order_by('district', 'hospital_name')
    else:
        # Only show hospitals in the selected district
        hospitals = Hospital.objects.filter(
            district__iexact=district_input,
            blood_bank_available=True,
            is_approved=True
        ).order_by('hospital_name')

    return render(request, "hospital/hospital_list.html", {
        "hospitals": hospitals,
        "selected_district": district_input,
        "search_method": method
    })
#
# def Donate_blood(request, hospital_id):
#     hospital = get_object_or_404(Hospital, id=hospital_id)
#
#     user_id = request.session.get('user_id')
#     if not user_id:
#         messages.error(request, "Please login first")
#         return redirect('user_login')
#
#     user = get_object_or_404(user_registerdb, id=user_id)
#
#     # 🔥 6 MONTH RULE
#     can_donate = True
#     next_allowed_date = None
#     if user.last_donation_date:
#         next_allowed_date = user.last_donation_date + relativedelta(months=6)
#         if date.today() < next_allowed_date:
#             can_donate = False
#
#     if request.method == "POST":
#         if not can_donate:
#             messages.error(
#                 request,
#                 f"You can donate blood only after {next_allowed_date.strftime('%d-%m-%Y')}"
#             )
#             return redirect('index')
#
#         try:
#             age = int(request.POST.get("age"))
#             weight = int(request.POST.get("weight"))
#         except:
#             messages.error(request, "Invalid input")
#             return redirect('Donate_blood', hospital_id=hospital.id)
#
#         gender = request.POST.get("gender")
#         district = request.POST.get("district")
#         address = request.POST.get("address")
#         medical_condition = request.POST.get("medical_condition")
#         medical_info = request.POST.get("medical_info", "")
#
#         # Minimum weight check
#         if weight < 45:
#             messages.error(request, "Minimum weight required is 45 kg")
#             return redirect('Donate_blood', hospital_id=hospital.id)
#
#         # Save request
#         BloodDonate.objects.create(
#             hospital=hospital,
#             user=user,
#             user_name=user.full_name,
#             email=user.email,
#             phone=user.phone,
#             blood_group=user.blood_group,
#             age=age,
#             gender=gender,
#             weight=weight,
#             district=district,
#             address=address,
#             medical_condition=medical_condition,
#             medical_info=medical_info,
#             status="PENDING"
#         )
#
#         messages.success(
#             request,
#             "Donation request submitted. Hospital will schedule date & time."
#         )
#         return redirect('index')
#
#     # Render template with eligibility info
#     return render(request, "user/Donate_blood.html", {
#         "hospital": hospital,
#         "user": user,
#         "can_donate": can_donate,
#         "next_allowed_date": next_allowed_date
#     })


# Time slots round-robin
TIME_SLOTS = ['Morning', 'Afternoon', 'Evening']

# Function to assign time slot automatically

def assign_time_slot(donation):
    # Assign donation date as today if not set
    if not donation.donation_date:
        donation.donation_date = date.today()

    # Count approved donations on the same day for the hospital
    same_day_count = BloodDonate.objects.filter(
        hospital=donation.hospital,
        donation_date=donation.donation_date,
        status='APPROVED'
    ).count()

    # Assign round-robin time slot
    donation.time_slot = TIME_SLOTS[same_day_count % len(TIME_SLOTS)]
    donation.save()

# Hospital dashboard view
# def donate_request(request):
#     # Check hospital login
#     hospital_id = request.session.get('hospital_id')
#     if not hospital_id:
#         messages.error(request, "Please login first")
#         return redirect('hos_login')
#
#     # Fetch hospital
#     hospital = get_object_or_404(Hospital, id=hospital_id)
#
#     # Fetch pending blood donation requests for this hospital
#     pending_requests = BloodDonate.objects.filter(
#         hospital=hospital,
#         status='PENDING'
#     ).order_by('-created_at')  # latest requests first
#
#     return render(request, 'hospital/donate_request.html', {
#         'hospital': hospital,
#         'pending_requests': pending_requests
#     })
#
#
# # Approve donation request
# def approve_request(request, donation_id):
#     donation = get_object_or_404(BloodDonate, id=donation_id)
#
#     # Only allow if the logged-in hospital matches
#     hospital_id = request.session.get('hospital_id')
#     if donation.hospital.id != hospital_id:
#         messages.error(request, "You cannot approve this request")
#         return redirect('donate_request')
#
#     donation.status = 'APPROVED'
#     assign_time_slot(donation)
#
#     messages.success(
#         request,
#         f"Donation request by {donation.user_name} approved. Time Slot: {donation.time_slot}"
#     )
#     return redirect('donate_request')
#
#
# # Reject donation request
# def reject_request(request, donation_id):
#     donation = get_object_or_404(BloodDonate, id=donation_id)
#
#     # Only allow if the logged-in hospital matches
#     hospital_id = request.session.get('hospital_id')
#     if donation.hospital.id != hospital_id:
#         messages.error(request, "You cannot reject this request")
#         return redirect('donate_request')
#
#     donation.status = 'REJECTED'
#     donation.save()
#
#     messages.warning(
#         request,
#         f"Donation request by {donation.user_name} rejected."
#     )
#     return redirect('donate_request')


TIME_SLOTS = ['Morning', 'Afternoon', 'Evening']

def Donate_blood(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first")
        return redirect('user_login')

    user = get_object_or_404(user_registerdb, id=user_id)

    # 🔥 6 MONTH RULE
    can_donate = True
    next_allowed_date = None
    if user.last_donation_date:
        next_allowed_date = user.last_donation_date + relativedelta(months=6)
        if date.today() < next_allowed_date:
            can_donate = False

    if request.method == "POST":
        if not can_donate:
            messages.error(
                request,
                f"You can donate blood only after {next_allowed_date.strftime('%d-%m-%Y')}"
            )
            return redirect('index')

        try:
            age = int(request.POST.get("age"))
            weight = int(request.POST.get("weight"))
        except:
            messages.error(request, "Invalid input")
            return redirect('Donate_blood', hospital_id=hospital.id)

        gender = request.POST.get("gender")
        district = request.POST.get("district")
        address = request.POST.get("address")
        medical_condition = request.POST.get("medical_condition")
        medical_info = request.POST.get("medical_info", "")

        if weight < 45:
            messages.error(request, "Minimum weight required is 45 kg")
            return redirect('Donate_blood', hospital_id=hospital.id)

        BloodDonate.objects.create(
            hospital=hospital,
            user=user,
            user_name=user.full_name,
            email=user.email,
            phone=user.phone,
            blood_group=user.blood_group,
            age=age,
            gender=gender,
            weight=weight,
            district=district,
            address=address,
            medical_condition=medical_condition,
            medical_info=medical_info,
            status="PENDING"
        )

        messages.success(
            request,
            "Donation request submitted. Hospital will schedule date & time."
        )
        return redirect('index')

    return render(request, "user/Donate_blood.html", {
        "hospital": hospital,
        "user": user,
        "can_donate": can_donate,
        "next_allowed_date": next_allowed_date
    })

# Hospital dashboard view
def donate_request(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login first")
        return redirect('hos_login')

    # Get hospital for logged-in user
    hospital = get_object_or_404(Hospital, user=request.user)

    # Fetch all pending requests for this hospital
    pending_requests = BloodDonate.objects.filter(
        hospital=hospital,
        status='PENDING'
    ).order_by('-created_at')  # optional: newest first

    return render(request, 'hospital/donate_request.html', {
        'hospital': hospital,
        'pending_requests': pending_requests
    })

# Approve request


def hos_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Django login

            # Link logged-in user to Hospital
            try:
                hospital = Hospital.objects.get(user=user)
                request.session['hospital_id'] = hospital.id  # store hospital_id in session
            except Hospital.DoesNotExist:
                messages.error(request, "No hospital account found for this user")
                return redirect('hos_login')

            return redirect('hos_index')  # redirect to dashboard after login
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'hospital/hos_login.html')
def blood_camp(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    if request.method == "POST":
        BloodCamp.objects.create(
            hospital=hospital,
            organizer_name=request.POST.get('organizer_name'),
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            camp_date=request.POST.get('camp_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            location=request.POST.get('location'),
        )

        messages.success(request, "Blood Camp Announcement Posted Successfully")
        return redirect('hospital_dashboard')

    return render(request, 'hospital/blood_camp.html')
def complete_camp(request, camp_id):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    camp = get_object_or_404(BloodCamp, id=camp_id)

    if request.method == "POST":
        camp.status = 'COMPLETED'
        camp.donors_count = request.POST.get('donors_count')
        camp.units_collected = request.POST.get('units_collected')
        camp.save()

        messages.success(request, "Blood Camp marked as Completed")
        return redirect('hospital_dashboard')

    return render(request, 'hospital/complete_camp.html', {'camp': camp})


def user_dashboard(request):
    # All camps ordered by newest first
    camps = BloodCamp.objects.all().order_by('-created_at')

    # Separate upcoming and completed camps
    upcoming = camps.filter(status='UPCOMING')
    completed = camps.filter(status='COMPLETED')

    return render(request, 'user/user_dashboard.html', {
        'camps': camps,
        'upcoming': upcoming,
        'completed': completed
    })


def hospital_dashboard(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    camps = BloodCamp.objects.filter(hospital=hospital)

    return render(request, 'hospital/hospital_dashboard.html', {
        'hospital': hospital,
        'camps': camps   # 🔥 THIS LINE FIXES EVERYTHING
    })
def hos_index(request):
    if not request.user.is_authenticated:
        return redirect('hos_login')

    try:
        hospital = Hospital.objects.get(user=request.user)
        if not hospital.is_approved:
            messages.error(request, "Admin approval required")
            return redirect('hos_login')
    except Hospital.DoesNotExist:
        return redirect('hos_login')

    return render(request, 'hospital/hos_index.html', {
        'hospital': hospital
    })

def hospital_camps(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    upcoming_camps = BloodCamp.objects.filter(
        hospital=hospital, status='UPCOMING'
    )
    completed_camps = BloodCamp.objects.filter(
        hospital=hospital, status='COMPLETED'
    )

    return render(request, 'hospital/see_camps.html', {
        'hospital': hospital,
        'upcoming_camps': upcoming_camps,
        'completed_camps': completed_camps
    })
def complete_camp(request, camp_id):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    camp = get_object_or_404(BloodCamp, id=camp_id, hospital_id=hospital_id)

    if request.method == "POST":
        camp.status = 'COMPLETED'
        camp.donors_count = request.POST.get('donors_count')
        camp.units_collected = request.POST.get('units_collected')
        camp.save()

        messages.success(request, "Blood Camp marked as Completed")

    return redirect('see_camp')


def see_camp(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    camps = BloodCamp.objects.filter(hospital_id=hospital_id)
    return render(request, 'hospital/see_camp.html', {'camps': camps})


# admin
def dashboard(request):
    pending_hospitals = Hospital.objects.filter(is_approved=False)
    approved_hospitals = Hospital.objects.filter(is_approved=True)

    return render(request,'admin/dashboard.html', {
        'pending_hospitals': pending_hospitals,
        'approved_hospitals': approved_hospitals
    })
def reject_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)

    # delete both hospital & user
    hospital.user.delete()
    hospital.delete()

    messages.error(request, "Hospital registration rejected")
    return redirect('dashboard')


def donor_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    try:
        user = user_registerdb.objects.get(id=user_id)
    except user_registerdb.DoesNotExist:
        return redirect('user_login')

    history = BloodDonate.objects.filter(
        user_id=user_id
    ).order_by('-created_at')

    # Calculate next eligible date (example: 3 months / 90 days after last donation)
    next_eligible = None
    if user.last_donation_date:
        next_eligible = user.last_donation_date + timedelta(days=90)

    return render(request, 'user/donation_history.html', {
        'history': history,
        'user': user,
        'next_eligible_date': next_eligible.strftime("%d %b %Y") if next_eligible else "Now",
    })
# def search_blood(request):
#     hospitals = Hospital.objects.all()
#     blood_group = request.GET.get('blood_group')
#     urgency = request.GET.get('urgency')
#
#     if blood_group:
#         hospitals = hospitals.filter(
#             bloodstock__blood_group=blood_group,
#             bloodstock__units__gt=0
#         )
#
#     return render(request, 'user/receiver/search_blood.html', {
#         'hospitals': hospitals
#     })
def search_blood(request):
    hospitals = Hospital.objects.all()

    blood_group = request.GET.get('blood_group')
    urgency = request.GET.get('urgency')

    # Blood groups for dropdown
    BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']

    # Filter by blood group
    if blood_group:
        hospitals = hospitals.filter(
            bloodstock__blood_group=blood_group,
            bloodstock__units__gt=0
        )

    # Optional urgency filter (if you add field later)
    if urgency == 'emergency':
        hospitals = hospitals.filter(
            bloodstock__units__lt=5
        )

    context = {
        'hospitals': hospitals.distinct(),
        'blood_groups': BLOOD_GROUPS,
        'selected_group': blood_group,
        'selected_urgency': urgency,
    }

    return render(request, 'user/receiver/search_blood.html', context)
def request_blood(request, hospital_id):
    if not request.session.get('user_id'):
        return redirect('user_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)
    user = user_registerdb.objects.get(id=request.session['user_id'])

    if request.method == "POST":
        urgency = request.POST.get('urgency')

        BloodRequest.objects.create(
            user=user,
            hospital=hospital,
            blood_group=request.POST.get('blood_group'),
            units=request.POST.get('units'),
            urgency=urgency,
            preferred_date=None if urgency == 'EMERGENCY' else request.POST.get('preferred_date'),
            preferred_time=None if urgency == 'EMERGENCY' else request.POST.get('preferred_time'),
            patient_details=request.POST.get('patient_details')
        )

        messages.success(request, "Blood request submitted successfully")
        return redirect('receiver_history')

    return render(request, 'user/receiver/request_blood.html', {
        'hospital': hospital
    })

TIME_SLOTS = [
    "09:00 - 10:00",
    "10:00 - 11:00",
    "11:00 - 12:00",
    "14:00 - 15:00",
]
# def notifications(request):
#     user_id = request.session.get('user_id')  # your custom session
#     if not user_id:
#         messages.error(request, "Please login first")
#         return redirect('user_login')
#
#     # Get the actual user_registerdb instance
#     user = get_object_or_404(user_registerdb, id=user_id)
#
#     # Fetch notifications
#     donate_notifs = Notification.objects.filter(user=user, notif_type='donate').order_by('-created_at')
#     request_notifs = Notification.objects.filter(user=user, notif_type='request').order_by('-created_at')
#
#     return render(request, 'user/notifications.html', {
#         'donate_notifs': donate_notifs,
#         'request_notifs': request_notifs
#     })
#
#
#
# def approve_receiver_request(request, request_id):
#     req = get_object_or_404(BloodRequest, id=request_id)
#
#     if request.method == "POST":
#         req.assigned_date = request.POST.get('assigned_date')
#         req.time_slot = request.POST.get('time_slot')
#         req.status = 'APPROVED'
#         req.save()
#
#         Notification.objects.create(
#             user=req.user,
#             message=f"""Your blood request has been APPROVED ✅
#                     🏥 Hospital: {req.hospital.hospital_name}
#                     📅 Date: {req.assigned_date}
#                     ⏰ Time: {req.time_slot}
#                     🩸 Units: {req.units}"""
#         )
#         return redirect('hospital_dashboard')
#
#     return render(request, 'hospital/approve_receiver.html', {
#         'req': req,
#         'time_slots': TIME_SLOTS,
#         'today': date.today()
#     })
# def reject_receiver_request(request, request_id):
#     req = get_object_or_404(BloodRequest, id=request_id)
#     req.status = 'REJECTED'
#     req.save()
#     Notification.objects.create(
#         user=req.user,
#         message=f"""Your blood request has been REJECTED ❌
#                 🏥 Hospital: {req.hospital.hospital_name}
#                 Reason: Insufficient stock"""
#     )
#     return redirect('hospital_dashboard')
#
#
# def receiver_history(request):
#     if not request.session.get('user_id'):
#         return redirect('user_login')
#
#     user = user_registerdb.objects.get(id=request.session['user_id'])
#
#     history = BloodRequest.objects.filter(user=user).order_by('-created_at')
#
#     return render(request, 'user/receiver/history.html', {
#         'history': history
#     })
#
# def receiver_requests(request):
#     if not request.session.get('hospital_id'):
#         return redirect('hos_login')
#
#     hospital = Hospital.objects.get(id=request.session['hospital_id'])
#
#     requests = BloodRequest.objects.filter(
#         hospital=hospital
#     ).order_by('-created_at')
#
#     return render(request, 'hospital/receiver_requests.html', {
#         'requests': requests
#     })


TIME_SLOTS = ["9:00 AM - 11:00 AM", "11:00 AM - 1:00 PM", "2:00 PM - 4:00 PM", "4:00 PM - 6:00 PM"]

# ---------------- Notifications Page ----------------
# def notifications(request):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         messages.error(request, "Please login first")
#         return redirect('user_login')
#
#     user = get_object_or_404(user_registerdb, id=user_id)
#
#     donate_notifs = Notification.objects.filter(user=user, notif_type='donate').order_by('-created_at')
#     request_notifs = Notification.objects.filter(user=user, notif_type='request').order_by('-created_at')
#
#     return render(request, 'user/notifications.html', {
#         'donate_notifs': donate_notifs,
#         'request_notifs': request_notifs
#     })
#
#
# # ---------------- Approve Receiver Request ----------------
# def approve_receiver_request(request, request_id):
#     req = get_object_or_404(BloodRequest, id=request_id)
#
#     if request.method == "POST":
#         req.assigned_date = request.POST.get('assigned_date')
#         req.time_slot = request.POST.get('time_slot')
#         req.status = 'APPROVED'
#         req.save()
#
#         # Ensure we get the correct user_registerdb instance
#         user_instance = get_object_or_404(user_registerdb, id=req.user.id)
#
#         Notification.objects.create(
#             user=user_instance,
#             message=f"""Your blood request has been APPROVED ✅
# 🏥 Hospital: {req.hospital.hospital_name}
# 📅 Date: {req.assigned_date}
# ⏰ Time: {req.time_slot}
# 🩸 Units: {req.units}""",
#             notif_type='request'
#         )
#         return redirect('hospital_dashboard')
# # ---------------- Reject Receiver Request ----------------
# def reject_receiver_request(request, request_id):
#     req = get_object_or_404(BloodRequest, id=request_id)
#     req.status = 'REJECTED'
#     req.save()
#
#     # Create notification with correct notif_type
#     Notification.objects.create(
#         user=req.user,
#         message=f"""Your blood request has been REJECTED ❌
# 🏥 Hospital: {req.hospital.hospital_name}
# Reason: Insufficient stock""",
#         notif_type='request'
#     )
#     return redirect('hospital_dashboard')
#
# # ---------------- Receiver History ----------------
# def receiver_history(request):
#     if not request.session.get('user_id'):
#         return redirect('user_login')
#
#     user = get_object_or_404(user_registerdb, id=request.session['user_id'])
#
#     history = BloodRequest.objects.filter(user=user).order_by('-created_at')
#
#     return render(request, 'user/receiver/history.html', {
#         'history': history
#     })
#
# # ---------------- Hospital Receiver Requests ----------------
# def receiver_requests(request):
#     if not request.session.get('hospital_id'):
#         return redirect('hos_login')
#
#     hospital = get_object_or_404(Hospital, id=request.session['hospital_id'])
#
#     requests = BloodRequest.objects.filter(
#         hospital=hospital
#     ).order_by('-created_at')
#
#     return render(request, 'hospital/receiver_requests.html', {
#         'requests': requests
#     })
#
# def approve_request(request, donation_id):
#     donation = get_object_or_404(BloodDonate, id=donation_id)
#
#     if request.method == "POST":
#         donation_date = request.POST.get("donation_date")
#         time_slot = request.POST.get("time_slot")
#
#         if donation_date and time_slot:
#             donation.donation_date = donation_date
#             donation.time_slot = time_slot
#             donation.status = "APPROVED"
#             donation.save()
#             messages.success(request, f"Donation approved for {donation.donation_date} at {donation.time_slot}")
#             # ✅ Notification for user
#             Notification.objects.create(
#                 user=donation.user,
#                 message=f"""
#             Your blood donation request has been APPROVED ✅
#
#             📍 Hospital: {donation.hospital.hospital_name}
#             📅 Date: {donation.donation_date}
#             ⏰ Time Slot: {donation.time_slot}
#
#             Thank you for donating blood!
#             """
#             )
#             return redirect('donate_request')
#         else:
#             messages.error(request, "Please select date and time slot")
#
#     today = date.today()  # <-- add this
#     return render(request, 'hospital/receiver_requests.html', {
#         'donation': donation,
#         'time_slots': TIME_SLOTS,
#         'today': today,  # <-- pass today to template
#     })
#
# # Reject request
# def reject_request(request, donation_id):
#     donation = get_object_or_404(BloodDonate, id=donation_id)
#
#     donation.status = 'REJECTED'
#     donation.save()
#
#     Notification.objects.create(
#         user=donation.user,
#         message=f"""
# Your blood donation request has been REJECTED ❌
#
# 📍 Hospital: {donation.hospital.hospital_name}
#
# Please contact hospital for more details.
# """
#     )
#
#     messages.warning(request, "Donation rejected & user notified")
#     return redirect('donate_request')



# ---------------- Notifications ----------------
def notifications(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first")
        return redirect('user_login')

    user = get_object_or_404(user_registerdb, id=user_id)

    # Fetch notifications by type
    donate_notifs = Notification.objects.filter(user=user, notif_type='donate').order_by('-created_at')
    request_notifs = Notification.objects.filter(user=user, notif_type='request').order_by('-created_at')

    return render(request, 'user/notifications.html', {
        'donate_notifs': donate_notifs,
        'request_notifs': request_notifs
    })


# ---------------- Approve Blood Request ----------------
# def approve_receiver_request(request, request_id):
#     req = get_object_or_404(BloodRequest, id=request_id)
#
#     if request.method == "POST":
#         req.assigned_date = request.POST.get('assigned_date')
#         req.time_slot = request.POST.get('time_slot')
#         req.status = 'APPROVED'
#         req.save()
#
#         # Ensure user is user_registerdb instance
#         user_instance = get_object_or_404(user_registerdb, id=req.user.id)
#
#         # Create notification
#         Notification.objects.create(
#             user=user_instance,
#             message=f"""Your blood request has been APPROVED ✅
# 🏥 Hospital: {req.hospital.hospital_name}
# 📅 Date: {req.assigned_date}
# ⏰ Time: {req.time_slot}
# 🩸 Units: {req.units}""",
#             notif_type='request'
#         )
#         messages.success(request, "Blood request approved & user notified")
#         return redirect('hospital_dashboard')
#
#     return render(request, 'hospital/approve_receiver.html', {
#         'req': req,
#         'time_slots': TIME_SLOTS,
#         'today': date.today()
#     })


# ---------------- Reject Blood Request ----------------
def reject_receiver_request(request, request_id):
    req = get_object_or_404(BloodRequest, id=request_id)
    req.status = 'REJECTED'
    req.save()

    user_instance = get_object_or_404(user_registerdb, id=req.user.id)

    Notification.objects.create(
        user=user_instance,
        message=f"""Your blood request has been REJECTED ❌
🏥 Hospital: {req.hospital.hospital_name}
Reason: Insufficient stock""",
        notif_type='request'
    )
    messages.warning(request, "Blood request rejected & user notified")
    return redirect('hospital_dashboard')


# ---------------- Approve Blood Donation ----------------
# def approve_request(request, donation_id):
#     donation = get_object_or_404(BloodDonate, id=donation_id)
#
#     if request.method == "POST":
#         donation_date = request.POST.get("donation_date")
#         time_slot = request.POST.get("time_slot")
#
#         if donation_date and time_slot:
#             donation.donation_date = donation_date
#             donation.time_slot = time_slot
#             donation.status = "APPROVED"
#             donation.save()
#
#             Notification.objects.create(
#                 user=donation.user,
#                 message=f"""
# Your blood donation request has been APPROVED ✅
#
# 📍 Hospital: {donation.hospital.hospital_name}
# 📅 Date: {donation.donation_date}
# ⏰ Time Slot: {donation.time_slot}
#
# Thank you for donating blood!
# """,
#                 notif_type='donate'  # important
#             )
#             messages.success(request, f"Donation approved for {donation.donation_date} at {donation.time_slot}")
#             return redirect('donate_request')
#         else:
#             messages.error(request, "Please select date and time slot")
#
#     today = date.today()
#     return render(request, 'hospital/receiver_requests.html', {
#         'donation': donation,
#         'time_slots': TIME_SLOTS,
#         'today': today,
#     })
#

# ---------------- Reject Blood Donation ----------------
def reject_request(request, donation_id):
    donation = get_object_or_404(BloodDonate, id=donation_id)

    donation.status = 'REJECTED'
    donation.save()

    Notification.objects.create(
        user=donation.user,
        message=f"""
Your blood donation request has been REJECTED ❌

📍 Hospital: {donation.hospital.hospital_name}

Please contact hospital for more details.
""",
        notif_type='donate'  # important
    )
    messages.warning(request, "Donation rejected & user notified")
    return redirect('donate_request')


# ---------------- Receiver History ----------------
def receiver_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(user_registerdb, id=user_id)
    history = BloodRequest.objects.filter(user=user).order_by('-created_at')

    return render(request, 'user/receiver/history.html', {'history': history})


# ---------------- Hospital Receiver Requests ----------------
def receiver_requests(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)
    requests = BloodRequest.objects.filter(hospital=hospital).order_by('-created_at')

    return render(request, 'hospital/receiver_requests.html', {'requests': requests})
# ---------------- Approve Blood Donation ----------------
def approve_request(request, donation_id):
    donation = get_object_or_404(BloodDonate, id=donation_id)

    if request.method == "POST":
        donation_date = request.POST.get("donation_date")
        time_slot = request.POST.get("time_slot")

        if not donation_date or not time_slot:
            messages.error(request, "Please select date and time")
            return redirect('approve_request', donation_id=donation.id)

        donation.donation_date = donation_date
        donation.time_slot = time_slot
        donation.status = "APPROVED"
        donation.save()

        # 🔔 NOTIFICATION 1 – Donation Approved
        Notification.objects.create(
            user=donation.user,
            notif_type='donate',
            message=f"""🩸 Donation Approved ✅
🏥 Hospital: {donation.hospital.hospital_name}
📅 Date: {donation_date}
⏰ Time: {time_slot}

Please come on time."""
        )

        messages.success(request, "Donation approved & user notified")
        return redirect('donate_request')

    return render(request, 'hospital/approve_donation.html', {
        'donation': donation,
        'time_slots': TIME_SLOTS,
        'today': date.today()
    })



# Do exactly same fix in approve_receiver_request()
def approve_receiver_request(request, request_id):
    req = get_object_or_404(BloodRequest, id=request_id)

    # 🚨 EMERGENCY (already working – direct approve)
    if req.urgency == 'EMERGENCY':
        req.status = 'APPROVED'
        req.assigned_date = date.today()
        req.time_slot = 'IMMEDIATE'
        req.save()

        Notification.objects.create(
            user=req.user,
            notif_type='request',
            message=f"""🚨 Emergency Blood Request Approved
🏥 Hospital: {req.hospital.hospital_name}
🩸 Blood Group: {req.blood_group}
📦 Units: {req.units}

Please come immediately."""
        )

        return redirect('receiver_requests')

    # ⏳ NORMAL REQUEST
    if request.method == "POST":
        assigned_date = request.POST.get('assigned_date')
        time_slot = request.POST.get('time_slot')

        if not assigned_date or not time_slot:
            messages.error(request, "Date & time required")
            return redirect('approve_receiver', request_id=req.id)

        req.status = 'APPROVED'
        req.assigned_date = assigned_date
        req.time_slot = time_slot
        req.save()

        Notification.objects.create(
            user=req.user,
            notif_type='request',
            message=f"""🩸 Blood Request Approved ✅
🏥 Hospital: {req.hospital.hospital_name}
📅 Date: {assigned_date}
⏰ Time: {time_slot}

Please come at the confirmed time."""
        )

        messages.success(request, "Blood request approved & user notified")
        return redirect('receiver_requests')

    # GET → Normal confirmation page
    return render(request, 'hospital/approve_receiver.html', {
        'req': req,
        'time_slots': TIME_SLOTS,
        'today': date.today()
    })
def donors_list(request):
    return render(request,'hospital/donors_list.html');
def increase_stock(hospital, blood_group, units):
    stock, created = BloodStock.objects.get_or_create(
        hospital=hospital,
        blood_group=blood_group
    )
    stock.units += units
    stock.save()


# ➖ Reduce stock (after blood issue)
def decrease_stock(hospital, blood_group, units):
    stock = BloodStock.objects.get(
        hospital=hospital,
        blood_group=blood_group
    )
    if stock.units >= units:
        stock.units -= units
        stock.save()
        return True
    return False
def stock(request):
    hospital_id = request.session.get('hospital_id')

    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    stock = BloodStock.objects.filter(hospital=hospital).order_by('blood_group')

    return render(request, 'hospital/stock/stock.html', {
        'stock': stock,
        'hospital': hospital
    })

def add_stock(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hos_login')

    hospital = get_object_or_404(Hospital, id=hospital_id)

    if request.method == "POST":
        blood_group = request.POST.get('blood_group')
        units = request.POST.get('units')

        if not units or int(units) <= 0:
            messages.error(request, "Units must be greater than zero")
            return redirect('add_stock')

        increase_stock(
            hospital=hospital,
            blood_group=blood_group,
            units=int(units)
        )

        messages.success(
            request,
            f"{units} units added successfully to {blood_group}"
        )
        return redirect('stock')

    return render(request, 'hospital/stock/add_stock.html', {
        'blood_groups': BLOOD_GROUPS
    })
def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = user_registerdb.objects.get(id=user_id)
    return render(request, 'user/profile.html', {'user': user})

def edit_profile(request):
    if not request.session.get('user_id'):
        return redirect('user_login')

    return render(request, 'user/edit_profile.html')
def emergency(request):

    users = user_registerdb.objects.filter(status=1)

    blood_group = request.GET.get('blood_group')
    district = request.GET.get('district')

    if blood_group:
        users = users.filter(blood_group=blood_group)

    if district:
        users = users.filter(district=district)

    today = now().date()

    donors = []
    for user in users:
        is_valid = True

        if user.last_donation_date:
            if today < user.last_donation_date + timedelta(days=90):
                is_valid = False

        donors.append({
            'user': user,
            'blood_group': user.blood_group,
            'district': user.district,
            'is_valid': is_valid
        })

    context = {
        'donors': donors,
        'blood_groups': ['A+','A-','B+','B-','O+','O-','AB+','AB-'],
        'districts': [
            'Thiruvananthapuram','Kollam','Pathanamthitta','Alappuzha',
            'Kottayam','Idukki','Ernakulam','Thrissur','Palakkad',
            'Malappuram','Kozhikode','Wayanad','Kannur','Kasaragod'
        ],
        'selected_group': blood_group,
        'selected_district': district,
    }

    return render(request, 'user/emergency.html', context)

def send_emergency_email(request, donor_id):
    donor = Donor.objects.get(id=donor_id)

    send_mail(
        subject="🚨 Emergency Blood Donation Request",
        message=f"""
Dear {donor.user.username},

An urgent blood donation request has been raised.

Blood Group : {donor.blood_group}
Location    : {donor.district}

If you are available, please reply to this email.

Thank you for saving a life ❤️
LifeFlow Blood Bank
""",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[donor.user.email],
        fail_silently=False
    )

    return render(request, 'user/emergency_sent.html')





def mark_donation(request, donate_id):
    donation = get_object_or_404(BloodDonate, id=donate_id)

    if request.method == "POST":
        donation_date_str = request.POST.get('donation_date')
        time_slot = request.POST.get('time_slot')
        units_str = request.POST.get('units_collected')  # Get units as string

        # Validate units
        try:
            units = int(units_str)
            if units <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Units must be a positive number (e.g., 1).")
            return redirect('mark_donation', donate_id=donate_id)

        # Validate & parse date
        try:
            donation_date = datetime.strptime(donation_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect('mark_donation', donate_id=donate_id)

        # Update donation
        donation.status = 'COMPLETED'
        donation.donation_date = donation_date
        donation.last_donation = donation_date  # Assuming this is for the donation record
        donation.time_slot = time_slot
        donation.units_collected = units  # 🔥 FIXED: Assign units here
        donation.save()

        # Update user last donation date
        user = donation.user
        user.last_donation_date = donation_date
        user.save()

        # Block donor for 90 days (update availability)
        Donor.objects.filter(user=user).update(is_available=False)

        # Update hospital blood stock
        stock, created = BloodStock.objects.get_or_create(
            hospital=donation.hospital,
            blood_group=donation.blood_group
        )
        stock.units += units
        stock.save()

        messages.success(request, f"Donation marked complete! {units} units added to stock.")
        return redirect('approve_list')

    # GET: Show form
    today = datetime.today().strftime('%Y-%m-%d')
    time_slots = ['Morning', 'Afternoon', 'Evening']

    return render(request, 'hospital/approve donation list/mark_donation_form.html', {
        'donation': donation,
        'today': today,
        'time_slots': time_slots
    })

def approve_list(request):
    hospital = request.user.hospital

    donations = BloodDonate.objects.filter(
        hospital=hospital,
        status='APPROVED'
    ).order_by('-created_at')

    return render(request, 'hospital/approve donation list/approve_list.html', {
        'donations': donations
    })
def eligibility_status(request):
    if not request.session.get('user_id'):
        return redirect('user_login')

    user = user_registerdb.objects.get(
        id=request.session['user_id']
    )

    can_donate = True
    next_eligible_date = None
    remaining_days = 0

    if user.last_donation_date:
        next_eligible_date = user.last_donation_date + timedelta(days=90)

        if now().date() < next_eligible_date:
            can_donate = False
            remaining_days = (next_eligible_date - now().date()).days

    context = {
        'user': user,
        'can_donate': can_donate,
        'next_eligible_date': next_eligible_date,
        'remaining_days': remaining_days
    }

    return render(request, 'user/eligibility_status.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def emergency_search(request):
    donors = Donor.objects.filter(is_available=True).select_related('user')

    blood_group = request.GET.get('blood_group', '').strip()
    district = request.GET.get('district', '').strip()

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if district:
        donors = donors.filter(district__icontains=district)

    # Get distinct districts for dropdown (you can also hardcode if preferred)
    districts = sorted(Donor.objects.values_list('district', flat=True).distinct())

    context = {
        'donors': donors,
        'blood_groups': [bg[0] for bg in BLOOD_GROUPS],
        'districts': districts,
        'selected_group': blood_group,
        'selected_district': district,
    }
    return render(request, 'user/emergency_search.html', context)


def send_emergency_request(request, donor_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    donor = get_object_or_404(Donor, id=donor_id, is_available=True)

    # Basic honeypot for spam
    if request.POST.get('website'):  # hidden field in form
        return HttpResponseBadRequest("Spam detected")

    # Get form data
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()

    if not name or not email:
        messages.error(request, "Name and email are required.")
        return redirect('emergency_search')

    # Session-based rate limiting
    session = request.session
    now = timezone.now()

    # Per donor cooldown (6 hours per IP + donor)
    request_key = f"emergency_req_{get_client_ip(request)}_{donor_id}"
    last_time_str = session.get(request_key)
    if last_time_str:
        last_time = timezone.datetime.fromisoformat(last_time_str)
        if now - last_time < timedelta(hours=6):
            messages.warning(request, "You have already contacted this donor recently. Please wait.")
            return redirect('emergency_search')

    # Global daily limit (max 5 per IP)
    daily_key = f"emergency_daily_{get_client_ip(request)}_{now.date()}"
    requests_today = session.get(daily_key, 0)
    if requests_today >= 5:
        messages.error(request, "Daily limit reached for emergency requests.")
        return redirect('emergency_search')

    # Create BloodRequest record (adapted for anonymous)
    blood_request = BloodRequest.objects.create(
        # user=None,  # since anonymous
        # hospital=None,  # optional
        blood_group=donor.blood_group,
        units=1,  # default
        urgency='EMERGENCY',
        patient_details=f"Anonymous emergency request: {message}",
        # Add requester details as text
        requester_name=name,
        requester_email=email,
        requester_phone=phone if phone else '',
        contacted_donor=donor,
    )

    # Notify donor via email
    try:
        send_mail(
            subject="🚨 URGENT Blood Donation Request - LifeFlow",
            message=f"""
Dear {donor.user.full_name or donor.user.username},

An **EMERGENCY** blood donation request has been made for:
Blood Group: {donor.blood_group}
Location/District: {donor.district}

Requester Details:
Name: {name}
Email: {email}
Phone: {phone or 'Not provided'}
Additional Message: {message or 'None'}

This is a direct request through the public emergency donor search.

If you are available and willing to help, please contact the requester directly.

Thank you for being a lifesaver ❤️

LifeFlow Team
            """.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[donor.user.email],
            fail_silently=False,
        )
        donor.last_notified = now
        donor.save(update_fields=['last_notified'])

        # Update session
        session[request_key] = now.isoformat()
        session[daily_key] = requests_today + 1
        session.modified = True

        messages.success(request, "Emergency request sent successfully. The donor has been notified via email.")
    except Exception as e:
        messages.error(request, f"Request recorded, but failed to send email: {str(e)}")

    return redirect('emergency_search')

def approve_hospital(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    hospital.is_approved = True
    hospital.save()

    messages.success(request, "Hospital approved successfully")
    return redirect('dashboard')  # admin dashboard
def admin_header(request):
    # ✅ Allow only superusers
    if not request.user.is_superuser:
        return redirect('admin_login')

    return render(request, 'admin/admin_header.html')
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ allow ONLY superusers
            if user.is_superuser:
                login(request, user)
                request.session['admin'] = True
                return redirect('admin_header')
            else:
                messages.error(request, "You are not authorized as admin")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "admin/admin_login.html")


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


# ADMIN DASHBOARD
def admin_dashboard(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    context = {
        'users_count': user_registerdb.objects.count(),
        'hospitals_count': Hospital.objects.count(),
    }
    return render(request, "admin/admin_dashboard.html", context)


def admin_users(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    users = user_registerdb.objects.all()
    return render(request, "admin/admin_users.html", {'users': users})


def admin_hospitals(request):
    if not request.session.get('admin'):
        return redirect('admin_login')

    hospitals = Hospital.objects.all()
    return render(request, "admin/admin_hospitals.html", {'hospitals': hospitals})