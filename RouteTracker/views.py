from django.views.generic import TemplateView 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect 
from django.shortcuts import render 
from django.shortcuts import redirect 
from django.views import View 
from django.views.generic import ListView, CreateView

from .models import Route, CustomUser
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
    if request.method == "POST":
        form = RouteForm(request.POST)
        if form.is_valid():
           route = form.save(commit=False) # get the new route without saving to database
           route.user = user # Add the current user to the record 
           route.save() # Save route information to the database
           print("Calculating soc ")
           # Calculate soc here 
           return JsonResponse({'data_SOC':[1,2]})
        else:
           return render(request, 'viewRoutes.html', {'form': form})

    else:
        form = RouteForm() 
        context = {
            'form': form
        }
        return render(request, 'viewRoutes.html', context)

def calculate_SOC(SOC_previous, min_power, max_power, voltage, last_date_time, current_date_time, Qn):
    average_power=(max_power+min_power)/2
    load_current=average_power/voltage
    second_diff=(current_date_time-last_date_time).total_seconds()
    result=SOC_previous+load_current*second_diff/Qn
    return result

def getOutputData(request):
    labels = []
    data = []
    print("This is request", request.GET) 
    if request.method == "POST":
        routeName = request.POST.get('routeName', None) 
        routeInfo = None
        try:
            routeInfo = Route.objects.get(routeTitle=routeName)
        except:
            return JsonResponse({})
        #data.append(routeInfo.initialSOC)
        #labels.append(routeInfo.departure[0])
        SOC_previous=routeInfo.initialSOC
        last_min_power=0
        last_max_power=0
        last_voltage=routeInfo.batteryRating
        last_Qn=routeInfo.batteryCapacity
        last_date_time=routeInfo.departure[0]
        for i, depart in enumerate(routeInfo.departure):
            #Departure
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.departure[i],last_Qn)
            if calculated_SOC < 0.3:
                print("Error: SOC is less than 30%")
                # Consider showing error in the web page        
            data.append(calculated_SOC)
            labels.append(routeInfo.departure[i])
            SOC_previous=calculated_SOC
            last_min_power=routeInfo.minDeparturePow[i]
            last_max_power=routeInfo.maxDeparturePow[i]
            last_date_time=routeInfo.departure[i]
            #Transit
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.transit[i],last_Qn)
            if calculated_SOC < 0.3:
                print("Error: SOC is less than 30%")
                # Consider showing error in the web page        
            data.append(calculated_SOC)
            labels.append(routeInfo.transit[i])
            SOC_previous=calculated_SOC
            last_min_power=routeInfo.minTransitPow[i]
            last_max_power=routeInfo.maxTransitPow[i]
            last_date_time=routeInfo.transit[i]
            #Arrival
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.arrival[i],last_Qn)
            if calculated_SOC < 0.3:
                print("Error: SOC is less than 30%")
                # Consider showing error in the web page        
            data.append(calculated_SOC)
            labels.append(routeInfo.arrival[i])
            SOC_previous=calculated_SOC
            last_min_power=routeInfo.minArrivalPow[i]
            last_max_power=routeInfo.maxArrivalPow[i]
            last_date_time=routeInfo.arrival[i]
            #Stay
            calculated_SOC=calculate_SOC(SOC_previous,last_min_power,last_max_power,last_voltage,last_date_time,routeInfo.stay[i],last_Qn)
            if calculated_SOC < 0.3:
                print("Error: SOC is less than 30%")
                # Consider showing error in the web page        
            data.append(calculated_SOC)
            labels.append(routeInfo.stay[i])
            SOC_previous=calculated_SOC
            last_min_power=routeInfo.minStayPow[i]
            last_max_power=routeInfo.maxStayPow[i]
            last_date_time=routeInfo.stay[i]

        print('data', data)
        return JsonResponse({'labels': labels, 'data': data}) 
    else:
        return redirect('/')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
