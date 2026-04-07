import email
from email import message
from multiprocessing import context
from turtle import title
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from hospital_admin.views import prescription_list
from .forms import DoctorUserCreationForm, DoctorForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from hospital.models import User, Patient
from hospital_admin.models import Admin_Information, Clinical_Laboratory_Technician, Test_Information
from .models import Doctor_Information, Appointment, Education, Experience, Prescription_medicine, Report, Specimen, Test, Prescription_test, Prescription, Doctor_review
from django.db.models import Q, Count
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import random
import string
from datetime import datetime, timedelta
import datetime
import re
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from io import BytesIO
from urllib import response
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Create your views here.

def generate_random_string():
    N = 8
    string_var = ""
    string_var = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=N))
    return string_var

@csrf_exempt
@login_required(login_url="doctor-login")
def doctor_change_password(request,pk):
    doctor = Doctor_Information.objects.get(user_id=pk)
    context={'doctor':doctor}
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("doctor-dashboard")
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'doctor-change-password.html',context)

@csrf_exempt
@login_required(login_url="doctor-login")
def schedule_timings(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    context = {'doctor': doctor}
    return render(request, 'schedule-timings.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def patient_id(request):
    return render(request, 'patient-id.html')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutDoctor(request):
    user = User.objects.get(id=request.user.id)
    if user.is_doctor:
        user.login_status = False # Fixed: should be assignment, not comparison
        user.save()
        logout(request)
    messages.success(request, 'User Logged out')
    return redirect('doctor-login')

@csrf_exempt
def doctor_register(request):
    page = 'doctor-register'
    form = DoctorUserCreationForm()
    if request.method == 'POST':
        form = DoctorUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_doctor = True
            user.save()
            messages.success(request, 'Doctor account was created!')
            return redirect('doctor-login')
        else:
            messages.error(request, 'An error has occurred during registration')
    context = {'page': page, 'form': form}
    return render(request, 'doctor-register.html', context)

@csrf_exempt
def doctor_login(request):
    if request.method == 'GET':
        return render(request, 'doctor-login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_doctor:
                messages.success(request, 'Welcome Doctor!')
                return redirect('doctor-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Doctor')
                return redirect('doctor-logout')   
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'doctor-login.html')

@csrf_exempt
@login_required(login_url="doctor-login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def doctor_dashboard(request):
    if request.user.is_authenticated:    
        if request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            current_date = datetime.date.today()
            current_date_str = str(current_date)  
            today_appointments = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor).filter(appointment_status='confirmed')
            next_date = current_date + datetime.timedelta(days=1)
            next_date_str = str(next_date)  
            next_days_appointment = Appointment.objects.filter(date=next_date_str).filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
            today_patient_count = Appointment.objects.filter(date=current_date_str).filter(doctor=doctor).count()
            total_appointments_count = Appointment.objects.filter(doctor=doctor).count()
        else:
            return redirect('doctor-logout')
        context = {'doctor': doctor, 'today_appointments': today_appointments, 'today_patient_count': today_patient_count, 'total_appointments_count': total_appointments_count, 'next_days_appointment': next_days_appointment, 'current_date': current_date_str}
        return render(request, 'doctor-dashboard.html', context)
    else:
        return redirect('doctor-login')
 
@csrf_exempt
@login_required(login_url="doctor-login")
def appointments(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='pending').order_by('date')
    context = {'doctor': doctor, 'appointments': appointments}
    return render(request, 'appointments.html', context) 
 
@csrf_exempt        
@login_required(login_url="doctor-login")
def accept_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'confirmed'
    appointment.save()
    
    # Email notification (Localized & Fixed)
    patient_email = appointment.patient.email
    subject = "Appointment Accepted - HealthStack Kenya"
    values = {
            "name":appointment.patient.name,
            "doctor_name":appointment.doctor.name,
            "appointment_date":appointment.date,
            "appointment_time":appointment.time,
    }
    html_message = render_to_string('appointment_accept_mail.html', {'values': values})
    plain_message = strip_tags(html_message)
    try:
        send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [patient_email], html_message=html_message)
    except:
        pass # Prevent crash if email fails
    
    messages.success(request, 'Appointment Accepted')
    return redirect('doctor-dashboard')

@csrf_exempt
@login_required(login_url="doctor-login")
def reject_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'cancelled'
    appointment.save()
    
    patient_email = appointment.patient.email
    subject = "Appointment Rejection Email"
    values = {"name": appointment.patient.name, "doctor_name": appointment.doctor.name}
    html_message = render_to_string('appointment_reject_mail.html', {'values': values})
    try:
        send_mail(subject, strip_tags(html_message), settings.EMAIL_HOST_USER, [patient_email], html_message=html_message)
    except:
        pass
    
    messages.error(request, 'Appointment Rejected')
    return redirect('doctor-dashboard')

@csrf_exempt
@login_required(login_url="doctor-login")
def doctor_profile(request, pk):
    if request.user.is_patient:
        patient = request.user.patient
    else:
        patient = None
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    educations = Education.objects.filter(doctor=doctor).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctor).order_by('-from_year','-to_year')
    doctor_review = Doctor_review.objects.filter(doctor=doctor)
    context = {'doctor': doctor, 'patient': patient, 'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review}
    return render(request, 'doctor-profile.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def delete_education(request, pk):
    if request.user.is_doctor:
        educations = Education.objects.get(education_id=pk)
        educations.delete()
        messages.success(request, 'Education Deleted')
        return redirect('doctor-profile-settings')

@csrf_exempt  
@login_required(login_url="doctor-login")
def delete_experience(request, pk):
    if request.user.is_doctor:
        experiences = Experience.objects.get(experience_id=pk)
        experiences.delete()
        messages.success(request, 'Experience Deleted')
        return redirect('doctor-profile-settings')
      
@csrf_exempt      
@login_required(login_url="doctor-login")
def doctor_profile_settings(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        old_featured_image = doctor.featured_image
        if request.method == 'GET':
            educations = Education.objects.filter(doctor=doctor)
            experiences = Experience.objects.filter(doctor=doctor)
            context = {'doctor': doctor, 'educations': educations, 'experiences': experiences}
            return render(request, 'doctor-profile-settings.html', context)
        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image
            doctor.name = request.POST.get('name')
            doctor.phone_number = request.POST.get('number')
            doctor.gender = request.POST.get('gender')
            doctor.dob = request.POST.get('dob')
            doctor.description = request.POST.get('description')
            doctor.consultation_fee = request.POST.get('consultation_fee')
            doctor.report_fee = request.POST.get('report_fee')
            doctor.nid = request.POST.get('nid')
            doctor.visiting_hour = request.POST.get('visit_hour')
            doctor.featured_image = featured_image
            doctor.save()
            
            degree = request.POST.getlist('degree')
            institute = request.POST.getlist('institute')
            year_complete = request.POST.getlist('year_complete')
            for i in range(len(degree)):
                if degree[i]:
                    Education.objects.create(doctor=doctor, degree=degree[i], institute=institute[i], year_of_completion=year_complete[i])

            hospital_name = request.POST.getlist('hospital_name')     
            start_year = request.POST.getlist('from')
            end_year = request.POST.getlist('to')
            designation = request.POST.getlist('designation')
            for i in range(len(hospital_name)):
                if hospital_name[i]:
                    Experience.objects.create(doctor=doctor, work_place_name=hospital_name[i], from_year=start_year[i], to_year=end_year[i], designation=designation[i])
      
            messages.success(request, 'Profile Updated')
            return redirect('doctor-dashboard')
    else:
        return redirect('doctor-logout')
               
@csrf_exempt    
@login_required(login_url="doctor-login")      
def booking_success(request):
    return render(request, 'booking-success.html')

@csrf_exempt
@login_required(login_url="doctor-login")
def booking(request, pk):
    patient = request.user.patient
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    if request.method == 'POST':
        date = request.POST['appoint_date']
        transformed_date = datetime.datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
        appointment = Appointment.objects.create(
            patient=patient, doctor=doctor, date=transformed_date, 
            time=request.POST['appoint_time'], appointment_type=request.POST['appointment_type'],
            message=request.POST['message'], appointment_status='pending', serial_number=generate_random_string()
        )
        if appointment.message:
            subject = "New Appointment Request - HealthStack Kenya"
            values = {"name":patient.name, "doctor_name":doctor.name, "message":appointment.message}
            html_message = render_to_string('appointment-request-mail.html', {'values': values})
            try:
                send_mail(subject, strip_tags(html_message), settings.EMAIL_HOST_USER, [patient.email], html_message=html_message)
            except:
                pass
        messages.success(request, 'Appointment Booked')
        return redirect('patient-dashboard')
    context = {'patient': patient, 'doctor': doctor}
    return render(request, 'booking.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def my_patients(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).filter(appointment_status='confirmed')
    context = {'doctor': doctor, 'appointments': appointments}
    return render(request, 'my-patients.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def patient_profile(request, pk):
    doctor = Doctor_Information.objects.get(user=request.user)
    patient = Patient.objects.get(patient_id=pk)
    appointments = Appointment.objects.filter(doctor=doctor).filter(patient=patient)
    prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
    report = Report.objects.filter(doctor=doctor).filter(patient=patient) 
    context = {'doctor': doctor, 'appointments': appointments, 'patient': patient, 'prescription': prescription, 'report': report}  
    return render(request, 'patient-profile.html', context)

@csrf_exempt
@login_required(login_url="doctor-login")
def create_prescription(request,pk):
    doctor = Doctor_Information.objects.get(user=request.user)
    patient = Patient.objects.get(patient_id=pk) 
    if request.method == 'POST':
        prescription = Prescription.objects.create(doctor=doctor, patient=patient, extra_information=request.POST.get('extra_information'), create_date=datetime.date.today())
        medicine_name = request.POST.getlist('medicine_name')
        medicine_quantity = request.POST.getlist('quantity')
        medecine_frequency = request.POST.getlist('frequency')
        medicine_duration = request.POST.getlist('duration')
        medicine_relation_with_meal = request.POST.getlist('relation_with_meal')
        medicine_instruction = request.POST.getlist('instruction')
        for i in range(len(medicine_name)):
            if medicine_name[i]:
                Prescription_medicine.objects.create(prescription=prescription, medicine_name=medicine_name[i], quantity=medicine_quantity[i], frequency=medecine_frequency[i], duration=medicine_duration[i], instruction=medicine_instruction[i], relation_with_meal=medicine_relation_with_meal[i])
        test_name = request.POST.getlist('test_name')
        test_description = request.POST.getlist('description')
        test_info_id = request.POST.getlist('id')
        for i in range(len(test_name)):
            if test_name[i]:
                test_info = Test_Information.objects.get(test_id=test_info_id[i])
                Prescription_test.objects.create(prescription=prescription, test_name=test_name[i], test_description=test_description[i], test_info_id=test_info_id[i], test_info_price=test_info.test_price)
        messages.success(request, 'Prescription Created')
        return redirect('patient-profile', pk=patient.patient_id)
    return render(request, 'create-prescription.html', {'doctor': doctor,'patient': patient})

@csrf_exempt      
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(),content_type="aplication/pdf")
    return None

@csrf_exempt
def report_pdf(request, pk):
    report = Report.objects.get(report_id=pk)
    specimen = Specimen.objects.filter(report=report)
    test = Test.objects.filter(report=report)
    context={'report':report,'test':test,'specimen':specimen}
    pdf=render_to_pdf('report_pdf.html', context)
    return HttpResponse(pdf, content_type='application/pdf') if pdf else HttpResponse("Not Found")

@csrf_exempt
@login_required(login_url="login")
def patient_search(request, pk):
    """Fixed: Now searches by Name or ID"""
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    query = request.GET.get('search_query', '')
    patients = Patient.objects.filter(Q(name__icontains=query) | Q(patient_id__icontains=query)).distinct()
    return render(request, 'patient-profile.html', {'patients': patients, 'doctor': doctor, 'search_query': query})

@csrf_exempt
@login_required(login_url="login")
def doctor_test_list(request):
    tests = Test_Information.objects.all()
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        return render(request, 'doctor-test-list.html', {'doctor': doctor, 'tests': tests})
    elif request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        return render(request, 'doctor-test-list.html', {'patient': patient, 'tests': tests})
    return redirect('doctor-login')

@csrf_exempt
@login_required(login_url="login")
def doctor_view_prescription(request, pk):
    doctor = Doctor_Information.objects.get(user=request.user)
    prescriptions = Prescription.objects.get(prescription_id=pk)
    medicines = Prescription_medicine.objects.filter(prescription=prescriptions)
    tests = Prescription_test.objects.filter(prescription=prescriptions)
    return render(request, 'doctor-view-prescription.html', {'prescription': prescriptions, 'medicines': medicines, 'tests': tests, 'doctor': doctor})

@csrf_exempt
@login_required(login_url="login")
def doctor_view_report(request, pk):
    doctor = Doctor_Information.objects.get(user=request.user)
    report = Report.objects.get(report_id=pk)
    specimen = Specimen.objects.filter(report=report)
    test = Test.objects.filter(report=report)
    return render(request, 'doctor-view-report.html', {'report': report, 'test': test, 'specimen': specimen, 'doctor': doctor})

@csrf_exempt
@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.login_status = True
    user.save()

@csrf_exempt
@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.login_status = False
    user.save()

@csrf_exempt
@login_required(login_url="login")
def doctor_review(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        doctor_review = Doctor_review.objects.filter(doctor=doctor)
        return render(request, 'doctor-profile.html', {'doctor': doctor, 'doctor_review': doctor_review})
    if request.user.is_patient:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        patient = Patient.objects.get(user=request.user)
        if request.method == 'POST':
            Doctor_review.objects.create(doctor=doctor, patient=patient, title=request.POST.get('title'), message=request.POST.get('message'))
        return redirect('doctor-profile', pk=pk)
    return redirect('logout')