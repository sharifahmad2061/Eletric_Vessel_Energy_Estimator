from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

from django.contrib.auth.models import User
from EVEESystem.settings import DEFAULT_FROM_EMAIL
from django.core.mail import send_mail 
from .validators import validateFileExtension


class CustomUser(AbstractUser):    
    userId        = models.AutoField(primary_key=True)
    createdDate = models.DateTimeField(auto_now=False, auto_now_add=True)
    lastAccessDate  = models.DateTimeField(auto_now=True, auto_now_add=False)
    isAdminUser = models.BooleanField(default=False)
    studentId = models.CharField(max_length=10)
    
    class Meta:
        ordering =["-username"]
        verbose_name = 'User'

# To sync db -> python manage.py migrate --run-syncdb
# Manually delete migrations folder, delete sqlite3 then run makemigrations then migrate 

PROPULSION_METHODS = (
    ('full electric', 'FULL ELECTRIC'),
    ('diesel electric', 'DIESEL ELECTRIC')
)

class Route(models.Model):
    routeId            = models.AutoField(primary_key=True)
    user               = models.ForeignKey(CustomUser, verbose_name="User", on_delete=models.CASCADE)    
    dateAdded          = models.DateTimeField(auto_now=False, auto_now_add=True)
    initialSOC         = models.IntegerField(verbose_name="Initial SOC (%)")
    batteryCapacity    = models.IntegerField(verbose_name="Battery Capacity (Kwh)") # This is in kwh.    
    routeTitle         = models.CharField(max_length=50, verbose_name="Route Title", default="")
    batteryRating      = models.IntegerField(verbose_name="Battery Rating (VDC)") 
    propulsionMethod   = models.CharField(max_length=50, choices=PROPULSION_METHODS, blank=False, default=PROPULSION_METHODS[0][0])
    chargingTime       = models.IntegerField(verbose_name="Charging Time (m)", null=True, blank=True) # In minutes  
    fileName           = models.FileField(upload_to='uploads/%Y/%m/%d/', max_length=100, verbose_name="Vessel Timetable File", validators=[validateFileExtension], blank=True, null=True)  
    departure          = ArrayField(models.DateTimeField(), verbose_name="Departure")
    transit            = ArrayField(models.DateTimeField(), verbose_name="Transit")
    arrival            = ArrayField(models.DateTimeField(), verbose_name="Arrival")
    stay               = ArrayField(models.DateTimeField(), verbose_name="Stay")
    calcSOC            = ArrayField(models.IntegerField(), null=True, blank=True)
    minDeparturePow    = models.IntegerField(verbose_name="Min Departure Power Req") # Power requirements 
    maxDeparturePow    = models.IntegerField(verbose_name="Max Departure Power Req")
    minTransitPow      = models.IntegerField(verbose_name="Min Transit Power Req") 
    maxTransitPow      = models.IntegerField(verbose_name="Max Transit Power Req") 
    minArrivalPow      = models.IntegerField(verbose_name="Min Arrival Power Req") 
    maxArrivalPow      = models.IntegerField(verbose_name="Max Arrival Power Req") 
    minStayingPow      = models.IntegerField(verbose_name="Min Stay Power Req") 
    maxStayingPow      = models.IntegerField(verbose_name="Max Stay Power Req") 

    def save(self, force_insert=False, force_update=False, *args, **kwargs):        
            
        super(Route, self).save()           
    
    class Meta:
        """ Allows to define metadata for the database """
        ordering = ["dateAdded"]
        db_table = 'Route'
        verbose_name = "Route List"
    
    def __str__(self):
        """ Lets us name instances of each record(row) """
        return str(self.routeId)
    
    def get_absolute_url(self):
        return reverse("routes/view", kwargs={})
