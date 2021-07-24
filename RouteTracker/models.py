from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

from EVEESystem.settings import DEFAULT_FROM_EMAIL
from django.core.mail import send_mail 
from .validators import validateFileExtension


# To sync db -> python manage.py migrate --run-syncdb
# Manually delete migrations folder, delete sqlite3 then run makemigrations then migrate 

PROPULSION_METHODS = (
    ('full electric', 'Full Electric'),
    ('hybrid electric', 'Hybrid Electric'),
)

DOCKED_CHARGING_METHODS = (
    ('grid power', 'Grid Power'),
    ('engine power','Engine Power')
)

class Route(models.Model):
    routeId              = models.AutoField(primary_key=True)
    dateAdded            = models.DateTimeField(auto_now=False, auto_now_add=True)
    initialSOC           = models.PositiveIntegerField("Initial SOC (%)")
    batteryCapacity      = models.PositiveIntegerField("Battery Capacity (Kwh)") # This is in kwh.    
    routeTitle           = models.CharField("Route Title", max_length=50, default="")
    batteryRating        = models.PositiveIntegerField(verbose_name="Battery Rating (VDC)")
    propulsionMethod     = models.CharField("propulsion method", null=False, blank=False, choices=PROPULSION_METHODS, max_length=20, default=PROPULSION_METHODS[0][0])
    dockedChargingMethod = models.CharField("docked charging method", null=True, blank=False, choices=DOCKED_CHARGING_METHODS, max_length=20, default=DOCKED_CHARGING_METHODS[0][0])
    #chargingTime        = models.PositiveIntegerField(verbose_name="Charging Time (m)") # In minutes  
    fileName             = models.FileField(upload_to='uploads/%Y/%m/%d/', max_length=100, verbose_name="Vessel Timetable File", validators=[validateFileExtension], blank=True, null=True)  
    thresholdPower       = models.PositiveIntegerField("Engine Power (kw)", null=True, blank=True)
    departure            = ArrayField(models.DateTimeField(), verbose_name="Departure")
    transit              = ArrayField(models.DateTimeField(), verbose_name="Transit")
    arrival              = ArrayField(models.DateTimeField(), verbose_name="Arrival")
    stay                 = ArrayField(models.DateTimeField(), verbose_name="Stay")
    calcSOC              = ArrayField(models.PositiveIntegerField(), null=True, blank=True)
    minDeparturePow      = ArrayField(models.PositiveIntegerField(), verbose_name="Min Departure Power Req") # Power requirements 
    maxDeparturePow      = ArrayField(models.PositiveIntegerField(), verbose_name="Max Departure Power Req", null=True) # Power requirements 
    minTransitPow        = ArrayField(models.PositiveIntegerField(), verbose_name="Min Transit Power Req", null=True) 
    maxTransitPow        = ArrayField(models.PositiveIntegerField(), verbose_name="Max Transit Power Req", null=True)
    minArrivalPow        = ArrayField(models.PositiveIntegerField(), verbose_name="Min Arrival Power Req", null=True) 
    maxArrivalPow        = ArrayField(models.PositiveIntegerField(), verbose_name="Max Arrival Power Req",null=True) 
    minStayPow           = ArrayField(models.PositiveIntegerField(), verbose_name="Min Stay Power Req", null=True) 
    maxStayPow           = ArrayField(models.PositiveIntegerField(), verbose_name="Max Stay Power Req", null=True)
    
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
