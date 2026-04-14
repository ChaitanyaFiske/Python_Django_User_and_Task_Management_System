from django.db import models
from datetime import datetime, date

# Create your models here.

class user_detail(models.Model):
    Name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    mobile = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.Name if self.Name else str(self.id)

    status = models.BooleanField(default=True) 
    # True = Active
    # False = Blocked

    

STATUS = [('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Not Done', 'Not Done'),]

class task_detail(models.Model):

    fk_user = models.ForeignKey(user_detail, on_delete = models.CASCADE, null=True, blank=True)

    taskname = models.CharField(max_length=100, null=True, blank=True)
    taskdetails = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS, default='Pending')
    assigndate = models.DateField(null=True, blank=True)
    duedate = models.DateField(null=True, blank=True)
    totaldays = models.IntegerField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    remaining_days = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    #Status = models.BooleanField(default=True)

    def clean(self):
        # Rule 1: Assign date >= today
        if self.assigndate and self.duedate < date.today():
            from django.core.exceptions import ValidationError
            raise ValidationError("Assign date cannot be in the past")

        # Rule 2: Due date >= assign date
        if self.assigndate and self.duedate and self.completion_date:
            if self.duedate < self.assigndate and self.completion_date < self.assigndate:
                from django.core.exceptions import ValidationError
                raise ValidationError("Completion Date and Due date must be after assign date")
            
        # Completion date must be AFTER assign date
        if self.completion_date and self.assigndate:
            if self.completion_date < self.assigndate:
                raise ValidationError("Completion date cannot be before assign date")

        # Completion date should not be unrealistic
        if self.completion_date and self.duedate:
            if self.completion_date < self.assigndate:
                raise ValidationError("Invalid completion date")

    def save(self, *args, **kwargs):

        self.clean()

        # total days
        if self.assigndate and self.duedate:
            self.totaldays = (self.duedate - self.assigndate).days

        # remaining days (after completion)
        if self.completion_date and self.duedate:
            if self.completion_date < self.assigndate:
                raise ValueError("Completion date cannot be before assign date")
            self.remaining_days = (self.duedate - self.completion_date).days

        super().save(*args, **kwargs)

    # percentage for graph
    @property
    def completion_percentage(self):

        if not self.completion_date or not self.duedate:
            return 0

        if self.completion_date <= self.duedate:
            return 100

        delay = (self.completion_date - self.duedate).days
        return max(0, 100 - delay * 10)


    @property
    def remaining_days_display(self):

        if not self.completion_date or not self.duedate:
            return "Not completed"

        diff = (self.duedate - self.completion_date).days

        if diff > 0:
            return f"{diff} days early"

        elif diff == 0:
            return "Completed on Time"

        else:
            return f"Late by {abs(diff)} days"


    def __str__(self):
        return self.taskname or str(self.id)
