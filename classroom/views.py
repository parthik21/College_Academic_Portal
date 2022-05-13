from django.shortcuts import render,get_object_or_404,redirect
from django.views import generic
from django.views.generic import  (View,TemplateView,
                                  ListView,DetailView,
                                  CreateView,UpdateView,
                                  DeleteView)
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
from classroom.forms import UserForm,TeacherProfileForm,StudentProfileForm,MarksForm,MessageForm,NoticeForm,AssignmentForm,SubmitForm,TeacherProfileUpdateForm,StudentProfileUpdateForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.http import HttpResponseRedirect,HttpResponse
from classroom import models
from classroom.models import StudentsInClass,StudentMarks,ClassAssignment,SubmitAssignment,Student,Teacher
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)

# For Teacher Sign Up
def TeacherSignUp(request):
    if request == None:
        return 200
    user_type = 'teacher'
    registered = False
    logger.info('Teacher sign up accessed!')
    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        teacher_profile_form = TeacherProfileForm(data = request.POST)

        if user_form.is_valid() and teacher_profile_form.is_valid():
            user = user_form.save()
            user.is_teacher = True
            user.save()

            profile = teacher_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
            logger.info('Teacher sign up successfull')
        else:
            logger.info("error: Teacher sign up was unsuccessfull")
            print(user_form.errors,teacher_profile_form.errors)
    else:
       
        user_form = UserForm()
        teacher_profile_form = TeacherProfileForm()
        
    logger.info("Teacher form was rendered.")
    return render(request,'classroom/teacher_signup.html',{'user_form':user_form,'teacher_profile_form':teacher_profile_form,'registered':registered,'user_type':user_type})


###  For Student Sign Up
def StudentSignUp(request):
    if request == None:
        return 200
    user_type = 'student'
    registered = False
    logger.info('Student sign up accessed!')

    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        student_profile_form = StudentProfileForm(data = request.POST)

        if user_form.is_valid() and student_profile_form.is_valid():

            user = user_form.save()
            user.is_student = True
            user.save()

            profile = student_profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
            logger.info('Student sign up successfull')
        else:
            logger.info('error: Student sign up unsuccessfull')
            print(user_form.errors,student_profile_form.errors)
    else:
        user_form = UserForm()
        student_profile_form = StudentProfileForm()

    logger.info('Student form was rendered.')
    return render(request,'classroom/student_signup.html',{'user_form':user_form,'student_profile_form':student_profile_form,'registered':registered,'user_type':user_type})

## Sign Up page which will ask whether you are teacher or student.
def SignUp(request):
    logger.info('Signup requested')
    return render(request,'classroom/signup.html',{})

## login view.
def user_login(request):
    if request == None:
        return 200
    if request.method == "POST":
        logger.info('User login accessed')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        logger.info('User being authenticated')

        if user:
            if user.is_active:
                
                login(request,user)
                logger.info('User login successfull')
                return HttpResponseRedirect(reverse('home'))

            else:
                logger.info('error: Account not active')
                return HttpResponse("Account not active")

        else:
            logger.info('error: User login unsuccessfull')
            messages.error(request, "Invalid Details")
            return redirect('classroom:login')
    else:
        logger.info('User login redirecting to login')
        return render(request,'classroom/login.html',{})

## logout view.
@login_required
def user_logout(request):
    logout(request)
    logger.info('User logged out')
    return HttpResponseRedirect(reverse('home'))

## User Profile of student.
class StudentDetailView(LoginRequiredMixin,DetailView):

    context_object_name = "student"
    model = models.Student
    template_name = 'classroom/student_detail_page.html'
    logger.info('StudentDetailView accessed')

## User Profile for teacher.
class TeacherDetailView(LoginRequiredMixin,DetailView):
    context_object_name = "teacher"
    model = models.Teacher
    template_name = 'classroom/teacher_detail_page.html'
    logger.info('TeacherDetailView accessed')

## Profile update for students.
@login_required
def StudentUpdateView(request,pk):
    if request == None:
        return 200
    profile_updated = False
    student = get_object_or_404(models.Student,pk=pk)
    logger.info('StudentUpdateView accessed')
    if request.method == "POST":
        form = StudentProfileUpdateForm(request.POST,instance=student)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'student_profile_pic' in request.FILES:
                profile.student_profile_pic = request.FILES['student_profile_pic']
            logger.info('Student Profile Pic fetched and saved')
            profile.save()
            profile_updated = True
    else:
        form = StudentProfileUpdateForm(request.POST or None,instance=student)
    logger.info('StudentDetailView rendered')
    return render(request,'classroom/student_update_page.html',{'profile_updated':profile_updated,'form':form})

## Profile update for teachers.
@login_required
def TeacherUpdateView(request,pk):
    if request == None:
        return 200
    profile_updated = False
    teacher = get_object_or_404(models.Teacher,pk=pk)
    logger.info('TeacherUpdateView accessed')
    if request.method == "POST":
        form = TeacherProfileUpdateForm(request.POST,instance=teacher)
        if form.is_valid():
            profile = form.save(commit=False)
            if 'teacher_profile_pic' in request.FILES:
                profile.teacher_profile_pic = request.FILES['teacher_profile_pic']
            logger.info('Student Profile Pic fetched and saved')
            profile.save()
            profile_updated = True
    else:
        form = TeacherProfileUpdateForm(request.POST or None,instance=teacher)
    logger.info('TeacherUpdateView rendered')
    return render(request,'classroom/teacher_update_page.html',{'profile_updated':profile_updated,'form':form})

## List of all students that teacher has added in their class.
def class_students_list(request):
    if request == None:
        return 200
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    logger.info('Class Students list accessed')
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            qs_one.append(x)
        else:
            pass
    context = {
        "class_students_list": qs_one,
    }
    template = "classroom/class_students_list.html"
    logger.info('All class student rendered')
    return render(request, template, context)

class ClassStudentsListView(LoginRequiredMixin,DetailView):
    model = models.Teacher
    template_name = "classroom/class_students_list.html"
    context_object_name = "teacher"

## For Marks obtained by the student in all subjects.
class StudentAllMarksList(LoginRequiredMixin,DetailView):
    model = models.Student
    template_name = "classroom/student_allmarks_list.html"
    context_object_name = "student"

## To give marks to a student.
@login_required
def add_marks(request,pk):
    if request == None:
        return 200
    marks_given = False
    student = get_object_or_404(models.Student,pk=pk)
    logger.info('Add marks accessed')
    if request.method == "POST":
        form = MarksForm(request.POST)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.student = student
            marks.teacher = request.user.Teacher
            marks.save()
            messages.success(request,'Marks uploaded successfully!')
            logger.info('Marks uploaded successfully')
            return redirect('classroom:submit_list')
    else:
        logger.info('error: Invalid Add Marks form')
        form = MarksForm()
    logger.info('Add marks rendered')
    return render(request,'classroom/add_marks.html',{'form':form,'student':student,'marks_given':marks_given})

## For updating marks.
@login_required
def update_marks(request,pk):
    if request == None:
        return 200
    marks_updated = False
    obj = get_object_or_404(StudentMarks,pk=pk)
    logger.info('Update marks accessed')
    if request.method == "POST":
        form = MarksForm(request.POST,instance=obj)
        if form.is_valid():
            marks = form.save(commit=False)
            marks.save()
            marks_updated = True
            logger.info('Updated marks uploaded successfull')
    else:
        logger.info('error: Invalid Update Marks form')
        form = MarksForm(request.POST or None,instance=obj)
    logger.info('Update marks rendered')
    return render(request,'classroom/update_marks.html',{'form':form,'marks_updated':marks_updated})

## For writing notice which will be sent to all class students.
@login_required
def add_notice(request):
    if request == None:
        return 200
    notice_sent = False
    teacher = request.user.Teacher
    students = StudentsInClass.objects.filter(teacher=teacher)
    students_list = [x.student for x in students]
    logger.info('Add notice accessed')
    if request.method == "POST":
        notice = NoticeForm(request.POST)
        if notice.is_valid():
            object = notice.save(commit=False)
            object.teacher = teacher
            object.save()
            object.students.add(*students_list)
            notice_sent = True
            logger.info('Notice added successfully')
    else:
        logger.info('error: Invalid Add notice form')
        notice = NoticeForm()
    logger.info('Add notice rendered')
    return render(request,'classroom/write_notice.html',{'notice':notice,'notice_sent':notice_sent})

## For student writing message to teacher.
@login_required
def write_message(request,pk):
    if request == None:
        return 200
    message_sent = False
    teacher = get_object_or_404(models.Teacher,pk=pk)
    logger.info('Write message accessed')

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            mssg = form.save(commit=False)
            mssg.teacher = teacher
            mssg.student = request.user.Student
            mssg.save()
            message_sent = True
            logger.info('Notice Wrote successfully')
    else:
        logger.info('error: Invalid write notice form')
        form = MessageForm()
    return render(request,'classroom/write_message.html',{'form':form,'teacher':teacher,'message_sent':message_sent})

## For the list of all the messages teacher have received.
@login_required
def messages_list(request,pk):
    teacher = get_object_or_404(models.Teacher,pk=pk)
    logger.info('Messege list rendered')
    return render(request,'classroom/messages_list.html',{'teacher':teacher})

## Student can see all notice given by their teacher.
@login_required
def class_notice(request,pk):
    student = get_object_or_404(models.Student,pk=pk)
    logger.info('Class notice rendered')
    return render(request,'classroom/class_notice_list.html',{'student':student})

## To see the list of all the marks given by the techer to a specific student.
@login_required
def student_marks_list(request,pk):
    error = True
    student = get_object_or_404(models.Student,pk=pk)
    teacher = request.user.Teacher
    given_marks = StudentMarks.objects.filter(teacher=teacher,student=student)
    logger.info('Student marks list rendered')
    return render(request,'classroom/student_marks_list.html',{'student':student,'given_marks':given_marks})

## To add student in the class.
class add_student(LoginRequiredMixin,generic.RedirectView):

    def get_redirect_url(self,*args,**kwargs):
        return reverse('classroom:students_list')

    def get(self,request,*args,**kwargs):
        student = get_object_or_404(models.Student,pk=self.kwargs.get('pk'))

        try:
            StudentsInClass.objects.create(teacher=self.request.user.Teacher,student=student)
        except:
            messages.warning(self.request,'warning, Student already in class!')
        else:
            messages.success(self.request,'{} successfully added!'.format(student.name))

        return super().get(request,*args,**kwargs)

@login_required
def student_added(request):
    logger.info('Student Added rendered')
    return render(request,'classroom/student_added.html',{})

## List of students which are not added by teacher in their class.
def students_list(request):
    query = request.GET.get("q", None)
    students = StudentsInClass.objects.filter(teacher=request.user.Teacher)
    students_list = [x.student for x in students]
    qs = Student.objects.all()
    logger.info('Student not added by teacher in their class accessed')
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )
    qs_one = []
    for x in qs:
        if x in students_list:
            pass
        else:
            qs_one.append(x)

    context = {
        "students_list": qs_one,
    }
    template = "classroom/students_list.html"
    logger.info('Student not added by teacher in their class rendered')
    return render(request, template, context)

## List of all the teacher present in the portal.
def teachers_list(request):
    query = request.GET.get("q", None)
    qs = Teacher.objects.all()
    logger.info('Teacher list accessed')
    if query is not None:
        qs = qs.filter(
                Q(name__icontains=query)
                )

    context = {
        "teachers_list": qs,
    }
    template = "classroom/teachers_list.html"
    logger.info('All teachers rendered')
    return render(request, template, context)


####################################################

## Teacher uploading assignment.
@login_required
def upload_assignment(request):
    assignment_uploaded = False
    teacher = request.user.Teacher
    students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
    logger.info('Assignment uploader accessed')
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            students = Student.objects.filter(user_student_name__teacher=request.user.Teacher)
            upload.save()
            upload.student.add(*students)
            assignment_uploaded = True
            logger.info('Assignmnet uploaded successfully')
    else:
        logger.info('error: Invalid assignment uploder form')
        form = AssignmentForm()
    logger.info('Assignment uploder rendered')
    return render(request,'classroom/upload_assignment.html',{'form':form,'assignment_uploaded':assignment_uploaded})

## Students getting the list of all the assignments uploaded by their teacher.
@login_required
def class_assignment(request):
    student = request.user.Student
    logger.info('Class assignment accessed')
    assignment = SubmitAssignment.objects.filter(student=student)
    assignment_list = [x.submitted_assignment for x in assignment]
    logger.info('All class assignment rendered')
    return render(request,'classroom/class_assignment.html',{'student':student,'assignment_list':assignment_list})

## List of all the assignments uploaded by the teacher himself.
@login_required
def assignment_list(request):
    teacher = request.user.Teacher
    logger.info('Assignment list accessed')
    logger.info('All assignments uploaded by the teacher rendered')
    return render(request,'classroom/assignment_list.html',{'teacher':teacher})

## For updating the assignments later.
@login_required
def update_assignment(request,id=None):
    logger.info('Update assignment accessed')
    obj = get_object_or_404(ClassAssignment, id=id)
    form = AssignmentForm(request.POST or None, instance=obj)
    context = {
        "form": form
    }
    if form.is_valid():
        obj = form.save(commit=False)
        if 'assignment' in request.FILES:
            obj.assignment = request.FILES['assignment']
        obj.save()
        messages.success(request, "Updated Assignment".format(obj.assignment_name))
        logger.info('Assignment updated successfully')
        return redirect('classroom:assignment_list')
    template = "classroom/update_assignment.html"
    logger.info('Updated assignment rendered')
    return render(request, template, context)

## For deleting the assignment.
@login_required
def assignment_delete(request, id=None):
    obj = get_object_or_404(ClassAssignment, id=id)
    logger.info('Assignment delete accessed')
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Assignment Removed")
        logger.info('Assignment removed successfully')
        return redirect('classroom:assignment_list')
    context = {
        "object": obj,
    }
    template = "classroom/assignment_delete.html"
    logger.info('Deleted assignment rendered')
    return render(request, template, context)

## For students submitting their assignment.
@login_required
def submit_assignment(request, id=None):
    student = request.user.Student
    assignment = get_object_or_404(ClassAssignment, id=id)
    teacher = assignment.teacher
    logger.info('Submit assignment accessed')
    if request.method == 'POST':
        form = SubmitForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.teacher = teacher
            upload.student = student
            upload.submitted_assignment = assignment
            upload.save()
            logger.info('Assignment submitted successfully')
            return redirect('classroom:class_assignment')
    else:
        logger.info('error: Invalid submitted assignment')
        form = SubmitForm()
    logger.info('Submitted assignmnet rendered')
    return render(request,'classroom/submit_assignment.html',{'form':form,})

## To see all the submissions done by the students.
@login_required
def submit_list(request):
    teacher = request.user.Teacher
    logger.info('All submissions done by student rendered')
    return render(request,'classroom/submit_list.html',{'teacher':teacher})

##################################################################################################

## For changing password.
@login_required
def change_password(request):
    logger.info('Change password accessed')
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST , user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed")
            logger.info('Password changed successfully')
            return redirect('home')
        else:
            logger.info('error: Invalid password (unsuccessfull operation)')
            return redirect('classroom:change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form':form}
        logger.info('error: Invalid password change form')
        return render(request,'classroom/change_password.html',args)

