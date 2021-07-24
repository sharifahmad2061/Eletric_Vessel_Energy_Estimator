from django.views.generic import TemplateView 
from django.http import HttpResponseRedirect 
from django.shortcuts import render 
from django.shortcuts import redirect 
from django.views import View 
from django.views.generic import ListView, CreateView
from django.contrib import messages

from .models import Route
from .forms import RouteForm
from django.http import JsonResponse
import statistics

"""
from .models import Author
"""

class AboutView(TemplateView):
    template_name = "about.html"
    

class RouteListView(ListView):
    template_name = "viewRoutes.html"
    context_object_name = "routes"      
    model = Route 
    
    # return only the user's requests if they don't have admin privilege 
    def get_queryset(self):
        user = list(CustomUser.objects.filter(username=self.request.user))[0] 
        # If the user has isAdminUser then return all the requests for viewing 
        if user.isAdminUser:
            return  Route.objects.all().order_by('-dateAdded')
        else:
           return Route.objects.filter(user=self.request.user).order_by('-dateAdded')
    
    
class RouteCreateView(CreateView):
    form_class = RouteForm
    template_name = "createRoute.html"
    context_object_name = "routes"




def view_routes(request):
    """ Meant to gather route details and display SOC levels """
    user = request.user
    instance = None 
    if request.method == "POST":
        instance = Route.objects.filter(routeTitle=request.POST.get("routeTitle")).first()
        form = RouteForm(request.POST, instance=instance)
        if form.is_valid():
           route = form.save(commit=False) # get the new route without saving to database
           route.user = user # Add the current user to the record 
           # handle min max departure and other powers
           num_of_sails = len(route.departure)
           route.minDeparturePow = route.minDeparturePow*num_of_sails
           route.maxDeparturePow = route.maxDeparturePow*num_of_sails
           route.minTransitPow = route.minTransitPow*num_of_sails
           route.maxTransitPow = route.maxTransitPow*num_of_sails
           route.minArrivalPow = route.minArrivalPow*num_of_sails
           route.maxArrivalPow = route.maxArrivalPow*num_of_sails
           route.minStayPow = route.minStayPow*num_of_sails
           route.maxStayPow = route.maxStayPow*num_of_sails
           route.save() # Save route information to the database
           form = RouteForm() # blank form if data has been saved            
      
        return render(request, 'viewRoutes.html', {'form': form})

    else:
        form = RouteForm() 
        context = {
            'form': form
        }
        return render(request, 'viewRoutes.html', context)
    
def getRoutes(request):
    """ Used to view the available routes that have been saved """
    results = {"Routes": ["There are no Routes present!"]}
    routes = list(Route.objects.all().values_list('routeTitle', flat=True))
    if len(routes) > 0:
        results["Routes"] = routes 
    return JsonResponse(results)
    

def calculate_SOC(SOC_previous, min_power, max_power, voltage, last_date_time, current_date_time, Qn):
    average_power=(max_power+min_power)/2
    load_current=average_power/voltage
    second_diff=(current_date_time-last_date_time).total_seconds()
    result=SOC_previous+(load_current*second_diff)/Qn
    return result

def getOutputData(request):
    labels = []
    data = []
    issue = []
    print("This is request", request.GET) 
    if request.method == "POST":
        routeName = request.POST.get('routeName', None) 
        routeInfo = None
        try:
            routeInfo = Route.objects.get(routeTitle=routeName)
        except Exception as ex:
            print("Route not found with err", ex)
            return JsonResponse({})

        # change kw to w
        routeInfo.minDeparturePow  = [x*1000 for x in routeInfo.minDeparturePow]
        routeInfo.maxDeparturePow  = [x*1000 for x in routeInfo.maxDeparturePow]
        routeInfo.minTransitPow    = [x*1000 for x in routeInfo.minTransitPow]
        routeInfo.maxTransitPow    = [x*1000 for x in routeInfo.maxTransitPow]
        routeInfo.minArrivalPow    = [x*1000 for x in routeInfo.minArrivalPow]
        routeInfo.maxArrivalPow    = [x*1000 for x in routeInfo.maxArrivalPow]
        routeInfo.minStayPow       = [x*1000 for x in routeInfo.minStayPow]
        routeInfo.maxStayPow       = [x*1000 for x in routeInfo.maxStayPow]
        routeInfo.thresholdPower *= 1000

        SOC_previous=routeInfo.initialSOC
        last_min_power=0
        last_max_power=0
        last_voltage=routeInfo.batteryRating
        last_Qn= (routeInfo.batteryCapacity * 1000 * 3600 ) / last_voltage
        last_date_time=routeInfo.departure[0]
        for i, depart in enumerate(routeInfo.departure):
            #Departure
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.departure[i],last_Qn)
            if calculated_SOC < 30:
                print("Error: SOC is less than 30%")
                issue.append("Error: SOC is less than 30%"+" at "+routeInfo.departure[i].strftime("%H:%M:%S"))
            elif calculated_SOC > 100:
                calculated_SOC = 100
            data.append(calculated_SOC)
            labels.append(routeInfo.departure[i])
            SOC_previous=calculated_SOC
            # if we are in hybrid electric use threshold power otherwise not
            if routeInfo.propulsionMethod == 'hybrid electric':
                last_min_power=-1*(routeInfo.minDeparturePow[i]-routeInfo.thresholdPower)
                last_max_power=-1*(routeInfo.maxDeparturePow[i]-routeInfo.thresholdPower)
            else:
                last_min_power=-1*(routeInfo.minDeparturePow[i])
                last_max_power=-1*(routeInfo.maxDeparturePow[i])
            last_date_time=routeInfo.departure[i]
            #Transit
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.transit[i],last_Qn)
            if calculated_SOC < 30:
                print("Error: SOC is less than 30%")
                issue.append("Error: SOC is less than 30%"+" at "+routeInfo.transit[i].strftime("%H:%M:%S"))       
            elif calculated_SOC > 100:
                calculated_SOC = 100
            data.append(calculated_SOC)
            labels.append(routeInfo.transit[i])
            SOC_previous=calculated_SOC
            if routeInfo.propulsionMethod == 'hybrid electric':
                last_min_power=-1*(routeInfo.minTransitPow[i]-routeInfo.thresholdPower)
                last_max_power=-1*(routeInfo.maxTransitPow[i]-routeInfo.thresholdPower)
            else:
                last_min_power=-1*(routeInfo.minTransitPow[i])
                last_max_power=-1*(routeInfo.maxTransitPow[i])

            last_date_time=routeInfo.transit[i]
            #Arrival
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.arrival[i],last_Qn)
            if calculated_SOC < 30:
                print("Error: SOC is less than 30%")
                issue.append("Error: SOC is less than 30%"+" at "+routeInfo.arrival[i].strftime("%H:%M:%S"))      
            elif calculated_SOC > 100:
                calculated_SOC = 100
            data.append(calculated_SOC)
            labels.append(routeInfo.arrival[i])
            SOC_previous=calculated_SOC
            if routeInfo.propulsionMethod == 'hybrid electric':
                last_min_power=-1*(routeInfo.minArrivalPow[i]-routeInfo.thresholdPower)
                last_max_power=-1*(routeInfo.maxArrivalPow[i]-routeInfo.thresholdPower)
            else:
                last_min_power=-1*(routeInfo.minArrivalPow[i])
                last_max_power=-1*(routeInfo.maxArrivalPow[i])
            last_date_time=routeInfo.arrival[i]
            #Stay
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.stay[i],last_Qn)
            if calculated_SOC < 30:
                print("Error: SOC is less than 30%")
                issue.append("Error: SOC is less than 30%"+" at "+routeInfo.stay[i].strftime("%H:%M:%S"))      
            elif calculated_SOC > 100:
                calculated_SOC = 100
            data.append(calculated_SOC)
            labels.append(routeInfo.stay[i])
            SOC_previous=calculated_SOC
            if routeInfo.propulsionMethod == 'hybrid electric':
                if routeInfo.dockedChargingMethod == 'grid power':
                    last_min_power= routeInfo.minStayPow[i]
                    last_max_power= routeInfo.maxStayPow[i]
                else:
                    last_min_power=-1 * (routeInfo.minStayPow[i]-routeInfo.thresholdPower)
                    last_max_power=-1 * (routeInfo.maxStayPow[i]-routeInfo.thresholdPower)
            else:
                last_min_power= routeInfo.minStayPow[i]
                last_max_power= routeInfo.maxStayPow[i]
            last_date_time=routeInfo.stay[i]

        print('data', data)
        return JsonResponse({'labels': labels, 'data': data, 'issue': issue}) 

    else:
        return redirect('/')
