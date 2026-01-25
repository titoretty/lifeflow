
from django.contrib.auth.models import User
from django.db import models
import datetime  # datetime error fix cheyyan

# Kerala District Choices
KERALA_DISTRICTS = [
    ('Alappuzha','Alappuzha'),
    ('Ernakulam','Ernakulam'),
    ('Idukki','Idukki'),
    ('Kannur','Kannur'),
    ('Kasaragod','Kasaragod'),
    ('Kollam','Kollam'),
    ('Kottayam','Kottayam'),
    ('Kozhikode','Kozhikode'),
    ('Malappuram','Malappuram'),
    ('Palakkad','Palakkad'),
    ('Pathanamthitta','Pathanamthitta'),
    ('Thiruvananthapuram','Thiruvananthapuram'),
    ('Thrissur','Thrissur'),
    ('Wayanad','Wayanad'),
]

BLOOD_GROUPS = [
    ('A+','A+'), ('A-','A-'), ('B+','B+'), ('B-','B-'),
    ('AB+','AB+'), ('AB-','AB-'), ('O+','O+'), ('O-','O-')
]

GENDER_CHOICES = [
    ('Male','Male'),
    ('Female','Female'),
    ('Other','Other')
]

class user_registerdb(models.Model):
    is_new_user = models.BooleanField(default=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=128)  # store hashed password
    full_name = models.CharField(max_length=150)
    address = models.TextField()
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50, choices=KERALA_DISTRICTS)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    slogan_question = models.CharField(max_length=200, blank=True, null=True)

    # New fields for donation readiness
    last_donation_date = models.DateField(null=True, blank=True, verbose_name="Last Donation Date")
    is_eligible_now = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        blank=True,
        verbose_name="Eligible to donate now?"
    )
    weight_above_50kg = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        blank=True,
        verbose_name="Weight above 50kg?"
    )
    ready_for_emergency = models.CharField(
        max_length=3,
        choices=[('Yes', 'Yes'), ('No', 'No')],
        blank=True,
        verbose_name="Ready for emergency donation?"
    )

    status = models.IntegerField(default=0)  # 0 = inactive, 1 = active
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Hospital(models.Model):
    HOSPITAL_TYPE_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Blood Bank', 'Blood Bank'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, unique=True)
    hospital_type = models.CharField(max_length=20, choices=HOSPITAL_TYPE_CHOICES)
    district = models.CharField(max_length=30, choices=KERALA_DISTRICTS)
    address = models.TextField()
    contact_number = models.CharField(max_length=10)
    email = models.EmailField()
    blood_bank_available = models.BooleanField(default=True)
    supported_blood_groups = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)  # Admin approval
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hospital_name


class BloodDonate(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    TIME_SLOTS = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
    )

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    user = models.ForeignKey(user_registerdb, on_delete=models.CASCADE)

    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=5)

    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    weight = models.PositiveIntegerField()

    district = models.CharField(max_length=50)
    address = models.TextField()

    donation_date = models.DateField(null=True, blank=True)

    last_donation = models.DateField(null=True, blank=True)

    medical_condition = models.CharField(max_length=10)
    medical_info = models.TextField(blank=True, null=True)
    units_collected = models.PositiveIntegerField(default=0)
    time_slot = models.CharField(
        max_length=20,
        choices=TIME_SLOTS,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.blood_group}"


class BloodCamp(models.Model):
    STATUS_CHOICES = (
        ('UPCOMING', 'Upcoming'),
        ('COMPLETED', 'Completed'),
    )
    organizer_name = models.CharField(max_length=150)

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    camp_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='UPCOMING'
    )

    total_donors = models.PositiveIntegerField(default=0)
    units_collected = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# class Notification(models.Model):
#     user = models.ForeignKey(user_registerdb, on_delete=models.CASCADE)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.message



class Notification(models.Model):
    NOTIF_TYPE = [
        ('donate', 'Blood Donate Request'),
        ('request', 'Blood Request'),
    ]

    user = models.ForeignKey(user_registerdb, on_delete=models.CASCADE)
    message = models.TextField()
    notif_type = models.CharField(max_length=10, choices=NOTIF_TYPE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.notif_type}"



class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EMERGENCY', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),
    ]

    user = models.ForeignKey('user_registerdb', on_delete=models.CASCADE)
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE)

    blood_group = models.CharField(max_length=5)
    units = models.PositiveIntegerField()

    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)

    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.CharField(max_length=50, null=True, blank=True)

    assigned_date = models.DateField(null=True, blank=True)
    time_slot = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    patient_details = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.blood_group}"

class BloodStock(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    units = models.PositiveIntegerField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hospital', 'blood_group')

    def __str__(self):
        return f"{self.hospital.hospital_name} - {self.blood_group} ({self.units})"

class Donor(models.Model):
    user = models.OneToOneField(user_registerdb, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=3)
    district = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.blood_group})"
