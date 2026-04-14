from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password

from .models import user_detail, task_detail

# Create your views here.

from django.shortcuts import get_object_or_404

@api_view(['PATCH','PUT'])
@permission_classes([IsAuthenticated])
def updatetask(request):
    
    data = request.data
    obj = task_detail.objects.filter(fk_user_id=data['user_id'],id=data['task_id']).last()

    if not obj :
        return Response({"error": "Task not found"},status=status.HTTP_404_NOT_FOUND)

    else :
        obj.taskname=data['taskname']
        obj.taskdetails=data['taskdetails']
        obj.status=data['status']
        assigndate = data.get('assigndate')
        duedate = data.get('duedate')

        if not assigndate or not duedate:
            return Response({"error": "Assign date and Due date are required"}, status=400)

        assigndate = datetime.strptime(assigndate, "%Y-%m-%d").date()
        duedate = datetime.strptime(duedate, "%Y-%m-%d").date()

        #obj.assigndate=datetime.strptime(data.get('assigndate'), "%Y-%m-%d").date()
        #obj.duedate=datetime.strptime(data.get('duedate'), "%Y-%m-%d").date()

        #obj.completion_date = datetime.strptime(data.get('completion_date'), "%Y-%m-%d").date()
        #if obj.completion_date < obj.assigndate:
            #return JsonResponse({"error": "Completion date cannot be before assign date"}, status=400)
        
        completion_date = data.get('completion_date')

        if completion_date:
            completion_date = datetime.strptime(completion_date, "%Y-%m-%d").date()
        else:
            completion_date = None

        obj.save()

        user = obj.fk_user
        if user.email and obj.status != 'Completed' :

            send_mail(
                subject="Task Updated",
                message=f"""Hello {user.Name},
                User ID: {obj.fk_user_id}
                Task ID: {obj.id}
                Your task has been updated successfully.
                Task Name: {obj.taskname}
                Details: {obj.taskdetails}
                Assign Date: {obj.assigndate}
                Due Date: {obj.duedate}
                Status: {obj.status}""",
                from_email="chaitanyafiske2001@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

        else :
            send_mail(
                subject="Task Completed",
                message=f"""Hello {user.Name},
                User ID: {obj.fk_user_id}
                Task ID: {obj.id}
                Your task has been Completed successfully.
                Task Name: {obj.taskname}
                Details: {obj.taskdetails}
                Completion Date: {obj.completion_date}
                Status: {obj.status}""",
                from_email="chaitanyafiske2001@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
        
        return Response({"message": "Task updated successfully and Email sent"},status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(
        {"error": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = user_detail.objects.all().values()
    return Response({"data": list(users)}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def taskdetails(request):
    tasks = task_detail.objects.all().values()
    return Response({"data": list(tasks)}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def taskdetail(request, user_id):
    if not user_id:
        return Response(
            {"error": "fk_user is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    task = task_detail.objects.filter(fk_user_id=user_id).values()
    return Response({"data": list(task)}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletetask(request, task_id):
        
        task = task_detail.objects.get(id=task_id)
        task.delete()

        return Response({"message": "Task deleted successfully"},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gettask(request):
    data = request.data
    user_id = data.get('fk_user')

    if not user_id:
        return Response(
            {"error": "fk_user is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = user_detail.objects.get(id=int(user_id))

    task = task_detail.objects.create(
        fk_user=user,
        taskname=data.get('taskname'),
        taskdetails=data.get('taskdetails'),
        status=data.get('status'),
        assigndate=datetime.strptime(data.get('assigndate'), "%Y-%m-%d").date(),
        duedate=datetime.strptime(data.get('duedate'), "%Y-%m-%d").date()
    )
    if user.email:
        send_mail(
            subject="New Task Assigned",
            message=f"""Hello {user.Name},
            User ID: {user.id}
            Task ID: {task.id}
            You have been assigned a new task.
            Task Name: {task.taskname}
            Details: {task.taskdetails}
            Assign Date: {task.assigndate}
            Due Date: {task.duedate}
            Status: {task.status}""",
            from_email="chaitanyafiske2001@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

    return Response(
        {"message": "Task created"},
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getdata(request):
    data = request.data

    required_fields = ['Name', 'email', 'mobile', 'city', 'password']

    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required"},status=status.HTTP_400_BAD_REQUEST)

    if not data['email'].lower().endswith('@gmail.com'):
        return Response(
            {"error": "Email must end with @gmail.com"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = user_detail.objects.create(
        Name=data['Name'],
        email=data['email'],
        mobile=data['mobile'],
        city=data['city'],
        password=make_password(data['password'])
    )

    return Response(
        {
            "message": "User created successfully",
            "user_id": user.id
        },
        status=status.HTTP_201_CREATED
    )

#---------------------------API^-----------------------------API^------------------------------API^-----------------------------#

@login_required
def users(request):
    objs = user_detail.objects.all()
    return render(request, 'UI/home.html', {"objs": objs})

@login_required
def tasks(request):
    objs = task_detail.objects.all()
    return render(request, 'UI/home_task.html', {"objs": objs})

@csrf_exempt
def index(request) :
    return render(request, 'UI/login.html')

@login_required
@csrf_exempt
def users(request) :
    return render(request, 'UI/home.html')

@login_required
@csrf_exempt
def tasks(request) :
    return render(request, 'UI/home_task.html')

@login_required
@csrf_exempt
def profile(request) :
    return render(request, 'UI/profile.html')

@login_required
@csrf_exempt
def setting(request) :
    return render(request, 'UI/setting.html')

@csrf_exempt
def login(request) :
    return render(request, 'UI/login.html')

@csrf_exempt
def register(request) :
    return render(request, 'UI/reg.html')

@login_required
@csrf_exempt
def dashboard(request) :
    return render(request, 'UI/dashboard.html')

@csrf_exempt
def getdata(request) :
    data = request.POST.dict()
    obj = user_detail.objects.create(**data)
    #obj = user_detail.objects.create(name=data['name'], email=data['email'], age=data['age'], address=data['address'], password=data['password'])
    print(obj)
    return JsonResponse({"status":200})

@csrf_exempt
def gettask(request):

    data = request.POST.dict()
    user_id = data.get('fk_user')

    if not user_id:
        return JsonResponse({"error": "fk_user is required"}, status=400)
    
    user = user_detail.objects.get(id=int(user_id))

    task = task_detail.objects.create(
        fk_user=user,
        taskname=data.get('taskname'),
        taskdetails=data.get('taskdetails'),
        status=data.get('status'),
        assigndate=datetime.strptime(data.get('assigndate'), "%Y-%m-%d").date(),
        duedate=datetime.strptime(data.get('duedate'), "%Y-%m-%d").date()
    )

    if user.email:
        send_mail(
            subject="New Task Assigned",
            message=f"""Hello {user.Name},
            User ID: {user.id}
            Task ID: {task.id}
            You have been assigned a new task.
            Task Name: {task.taskname}
            Details: {task.taskdetails}
            Assign Date: {task.assigndate}
            Due Date: {task.duedate}
            Status: {task.status}""",
            from_email="chaitanyafiske2001@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

    return JsonResponse({"status": 200})

@csrf_exempt
@login_required  
def users(request) :
    session_id = request.session.get('session_id')
    if session_id :
        objs = user_detail.objects.all()
        return render(request, 'UI/home.html', {"objs": objs})
    else :
        return redirect('/login/')
    
@csrf_exempt
@login_required  
def tasks(request) :
    session_id = request.session.get('session_id')
    if session_id :
        objs = task_detail.objects.all()
        return render(request, 'UI/home_task.html', {"objs": objs})
    else :
        return redirect('/login/')

@csrf_exempt
@login_required  
def dashboard(request) :
    session_id = request.session.get('session_id')
    if session_id :
        return render(request, 'UI/dashboard.html')
    else :
        return redirect('/login/')

@csrf_exempt
def delete_user(request) :
    data = request.POST.dict()
    user_detail.objects.get(id=data['user_id']).delete()
    return JsonResponse({"status":200})

@csrf_exempt
def delete_task(request) :
    data = request.POST.dict()
    task_detail.objects.get(id=data['user_id']).delete()
    return JsonResponse({"status":200})

def edit_user(request, user_id) :
    obj = user_detail.objects.get(id=user_id)
    return render(request, 'UI/edit_user.html', {'obj':obj})

def edit_task(request, user_id) :
    obj = task_detail.objects.get(id=user_id)
    return render(request, 'UI/edit_task.html', {'obj':obj})

@csrf_exempt
def update_user(request) :
    session_id = request.session.get('session_id')
    if session_id :
        data = request.POST.dict()
        print(data)
        obj = user_detail.objects.get(id=data['user_id'])
        obj.Name = data['Name']
        obj.email = data['email']
        obj.mobile = data['mobile']
        obj.city = data['city']

        if not obj.email.lower().endswith('@gmail.com'):
            return JsonResponse({"error": "Email Format Error"},status=400)
        else :
            obj.save()
            return JsonResponse({"status":200})
        
    else :
        return redirect('/login/')
    
@csrf_exempt
def update_task(request) :
    session_id = request.session.get('session_id')
    if session_id :
        data = request.POST.dict()
        print(data)
        try:
            obj = task_detail.objects.get(id=data['user_id'])
        except task_detail.DoesNotExist:
            return JsonResponse({"error": "Task not found"}, status=404)

        # get user object
        try:
            user = user_detail.objects.get(id=int(data.get('fk_user')))
        except user_detail.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        obj = task_detail.objects.get(id=data['user_id'])
        obj.fk_user = user
        obj.taskname = data['taskname']
        obj.taskdetails = data['taskdetails']
        obj.status = data['status']
        obj.assigndate = data['assigndate']
        obj.duedate = data['duedate']
        #obj.totaldays = data['totaldays']
        obj.assigndate = datetime.strptime(data.get('assigndate'), "%Y-%m-%d").date()
        obj.duedate = datetime.strptime(data.get('duedate'), "%Y-%m-%d").date()

        status = data.get('status')
        
        completion_date = data.get('completion_date')

        if status == "Completed":
            if completion_date:
                obj.completion_date = datetime.strptime(completion_date, "%Y-%m-%d").date()
            else:
                return Response({"error": "Completion date required for completed task"}, status=400)
        else:
            obj.completion_date = None

        obj.save()

        if user.email and obj.status != 'Completed':
            send_mail(
                subject="Updated Task",
                message=f"""Hello {user.Name},
                User ID: {user.id}
                Task ID: {obj.id}
                Your Task has been Updated.
                Task Name: {obj.taskname}
                Details: {obj.taskdetails}
                Assign Date: {obj.assigndate}
                Due Date: {obj.duedate}
                Status: {obj.status}""",
                from_email="chaitanyafiske2001@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

        else :
            send_mail(
                subject="Task Completed",
                message=f"""Hello {user.Name},
                User ID: {user.id}
                Task ID: {obj.id}
                Your Task has been Completed Successfully.
                Task Name: {obj.taskname}
                Details: {obj.taskdetails}
                Completion Date: {obj.completion_date}
                Status: {obj.status}""",
                from_email="chaitanyafiske2001@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

        return JsonResponse({"status":200})

    else :
        return redirect('/login/')
    
@csrf_exempt
def logout(request) :
    #session_id = request.session.get('session_id')
    request.session.flush()
    return JsonResponse({"status":200})

@csrf_exempt
def login_check(request):
    data = request.POST.dict()
    obj = authenticate(username=data['username'], password=data['password'])
    if obj is not None:
        auth_login(request, obj)
        request.session['session_id'] = obj.id
        return JsonResponse({"status":200})
    else:
        return JsonResponse({"status":403, "Message":"invalid credentials"})

@csrf_exempt
def toggle_status(request):

    user_id = request.POST.get('user_id')
    action = request.POST.get("action")

    user = user_detail.objects.get(id=user_id)

    #user.status = not user.status
    if action == "Block":
        user.status = False
    else:
        user.status = True
    
    user.save()

    return JsonResponse({"message":"Status Updated"})


def add_user(request) :
    return render(request, 'UI/add_user.html')

import json
from datetime import datetime

import json

@login_required
@csrf_exempt
def dashboard(request):
    
    tasks = task_detail.objects.select_related('fk_user').all()

    # -------- Existing Monthly Data --------
    monthly_data = {
        "total": [0]*12,
        "done": [0]*12,
        "proc": [0]*12,
        "pend": [0]*12,
        "notdone": [0]*12,
    }

    user_task_data = [] 

    for task in tasks:
        if not task.assigndate:
            continue

        month = task.assigndate.month - 1
        monthly_data["total"][month] += 1

        if task.status == "Completed":
            monthly_data["done"][month] += 1

            if task.completion_date and task.duedate:
                user_task_data.append({
                    "username": task.fk_user.Name,   # from your model :contentReference[oaicite:1]{index=1}
                    "assign_date": task.assigndate.strftime('%Y-%m-%d'),
                    "due_date": task.duedate.strftime('%Y-%m-%d'),
                    "completed_date": task.completion_date.strftime('%Y-%m-%d'),
                })
        elif task.status == "Processing":
            monthly_data["proc"][month] += 1

        elif task.status == "Pending":
            monthly_data["pend"][month] += 1

        elif task.status == "Not Done":
            monthly_data["notdone"][month] += 1

    context = {
        "chart_data": json.dumps(monthly_data),
        "user_task_data": json.dumps(user_task_data)   # ADD THIS
    }

    return render(request, 'UI/dashboard.html', context)

def add_task(request) :
    users = user_detail.objects.all()
    return render(request, 'UI/add_task.html',{'users': users})


'''@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def updatetasks(request):
    data = request.data
    task_id = data.get('task_id')

    if not task_id:
        return Response(
            {"error": "task_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    task = get_object_or_404(task_detail, id=task_id)

    if data.get('fk_user'):
        try:
            user = user_detail.objects.get(id=int(data.get('fk_user')))
            task.fk_user = user
        except user_detail.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        user = task.fk_user

    if data.get('taskname'):
        task.taskname = data.get('taskname')

    if data.get('taskdetails'):
        task.taskdetails = data.get('taskdetails')

    if data.get('status'):
        task.status = data.get('status')

    if data.get('assigndate'):
        task.assigndate = datetime.strptime(data.get('assigndate'), "%Y-%m-%d").date()

    if data.get('duedate'):
        task.duedate = datetime.strptime(data.get('duedate'), "%Y-%m-%d").date()

    if data.get('completion_date'):
        task.completion_date=datetime.strptime(data.get('completion_date'), "%Y-%m-%d").date()

    task.save()

    if user and user.email:
        send_mail(
            subject="Task Updated",
            message=f"""Hello {user.Name},
            Your task has been updated.
            Task Name: {task.taskname}
            Assign Date: {task.assigndate}
            Due Date: {task.duedate}
            Status: {task.status}""",
            from_email="chaitanyafiske2001@gmail.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

    return Response(
        {"message": "Task updated successfully"},
        status=status.HTTP_200_OK
    )'''



'''@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(
        {"error": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )'''


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getdata(request):
    data = request.data

    required_fields = ['Name', 'email', 'mobile', 'city', 'password']

    for field in required_fields:
        if not data.get(field):
            return Response({"error": f"{field} is required"},status=status.HTTP_400_BAD_REQUEST)

    if not data['email'].lower().endswith('@gmail.com'):
        return Response(
            {"error": "Email must end with @gmail.com"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = user_detail.objects.create(
        Name=data['Name'],
        email=data['email'],
        mobile=data['mobile'],
        city=data['city'],
        password=make_password(data['password'])
    )

    return Response(
        {
            "message": "User created successfully",
            "user_id": user.id
        },
        status=status.HTTP_201_CREATED
    )
