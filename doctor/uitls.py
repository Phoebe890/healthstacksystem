from django.db.models import Q
from .models import Patient

def searchPatients(request):
    search_query = ''
    
    # Get the search term from the URL (e.g., ?search_query=Phoebe)
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
        
    # We use Q objects to search multiple fields at once.
    # distinct() prevents duplicate results if a query matches multiple fields.
    patients = Patient.objects.distinct().filter(
        Q(name__icontains=search_query) |           # Search by Name 
        Q(phone_number__icontains=search_query) |   # Search by  Phone 
        Q(nid__icontains=search_query) |            # Search by National ID
        Q(patient_id__icontains=search_query)       # Search by System ID
    )
    
    return patients, search_query