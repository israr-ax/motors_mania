from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Vehicle, Category, Message, Favorite
from .forms import CustomSignupForm, CustomLoginForm, VehiclePostForm, MessageForm
from .forms import VehiclePostForm
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomSignupForm
from .models import Profile

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomSignupForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # User create hota hai, signals.py profile create karega
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Don't Use Similar Username And Passowrd "  )
            return redirect('auth')
    else:
        form = CustomSignupForm()

    return render(request, 'listings/auth.html', {'form': form})







# Home page with filters and search
@login_required(login_url='auth')
def home(request):
    vehicles = Vehicle.objects.all()

    # Filters
    category = request.GET.get('category')
    v_type = request.GET.get('vehicle_type')
    sort_by = request.GET.get('sort')

    if category and category != 'all':
        vehicles = vehicles.filter(category=category)

    if v_type and v_type != 'all':
        vehicles = vehicles.filter(vehicle_type=v_type)

    # Search
    search_query = request.GET.get('search')
    if search_query:
        vehicles = vehicles.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sorting
    if sort_by == 'price_asc':
        vehicles = vehicles.order_by('price')
    elif sort_by == 'price_desc':
        vehicles = vehicles.order_by('-price')
    else:
        vehicles = vehicles.order_by('-posted_on')

    categories = Category.objects.all()

    # Add "is_favorited" flag for each vehicle
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('vehicle_id', flat=True)
        for v in vehicles:
            v.is_favorited = v.id in user_favorites
    else:
        for v in vehicles:
            v.is_favorited = False

    return render(request, 'listings/home.html', {
        'vehicles': vehicles,
        'categories': categories,
        'selected_category': category,
        'selected_type': v_type,
        'search_query': search_query,
        'sort_by': sort_by
    })


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'listings/auth.html'


from .models import Vehicle, VehicleImage
from .forms import VehiclePostForm, VehicleImageForm

@login_required
def post_vehicle(request):
    if request.method == 'POST':
        form = VehiclePostForm(request.POST)
        files = request.FILES.getlist('images')  # Handle multiple files
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.seller = request.user
            vehicle.save()

            # Save multiple images
            for file in files:
                VehicleImage.objects.create(vehicle=vehicle, image=file)

            messages.success(request, "🚗 Vehicle posted successfully!")
            return redirect('home')
    else:
        form = VehiclePostForm()

    return render(request, 'listings/post.html', {'form': form})





@login_required
def toggle_favorite(request, vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, vehicle=vehicle)

    if not created:
        favorite.delete()  # remove if already exists

    return redirect('home')


def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'listings/vehicle_detail.html', {'vehicle': vehicle})




from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from django.db.models import Q


from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from .forms import MessageForm
from django.db.models import Q

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from .forms import MessageForm
from django.db.models import Q

@login_required
def chat_view(request, user_id=None):
    users = User.objects.exclude(id=request.user.id)
    other_user = None
    messages = []

    if user_id:
        other_user = get_object_or_404(User, id=user_id)
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).order_by('timestamp')

        if request.method == 'POST':
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                msg = form.save(commit=False)
                msg.sender = request.user
                msg.receiver = other_user
                msg.save()
                return redirect('start_chat', user_id=other_user.id)
        else:
            form = MessageForm()
    else:
        form = None

    return render(request, 'listings/chat.html', {
        'users': users,
        'other_user': other_user,
        'messages': messages,
        'form': form
    })



@login_required
def update_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ['Available', 'Sold']:
            vehicle.status = new_status
            vehicle.save()
            messages.success(request, f"Vehicle marked as {new_status}.")
    return redirect('vehicle_detail', pk=vehicle_id)


@login_required
def seller_dashboard(request):
    categories = Vehicle.CATEGORY_CHOICES
    vehicle_types = Vehicle.VEHICLE_TYPE_CHOICES
    vehicles = Vehicle.objects.filter(seller=request.user).order_by('-posted_on')

    # Stats
    total_vehicles = vehicles.count()
    available_count = vehicles.filter(status="Available").count()
    sold_count = vehicles.filter(status="Sold").count()

    return render(request, 'listings/seller_dashboard.html', {
        'vehicles': vehicles,
        'total_vehicles': total_vehicles,
        'available_count': available_count,
        'sold_count': sold_count,
        'categories': categories,
        'vehicle_types': vehicle_types,
    })

@login_required
def update_vehicle_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)
    
    # Toggle status
    if vehicle.status == "Available":
        vehicle.status = "Sold"
    else:
        vehicle.status = "Available"
    
    vehicle.save()
    messages.success(request, f"Vehicle status updated to {vehicle.status}")
    return redirect('seller_dashboard')

from django.http import JsonResponse

@login_required
def edit_vehicle(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        if not vehicle_id:
            messages.error(request, "Vehicle ID is missing.")
            return redirect('seller_dashboard')

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, seller=request.user)
        except Vehicle.DoesNotExist:
            messages.error(request, "Vehicle not found.")
            return redirect('seller_dashboard')

        vehicle.title = request.POST.get('title')
        vehicle.price = request.POST.get('price')
        vehicle.category = request.POST.get('category')
        vehicle.description = request.POST.get('description')
        vehicle.vehicle_type=request.POST.get('vehicle_type')
        vehicle.save()

        messages.success(request, "Vehicle updated successfully.")
        return redirect('seller_dashboard')
    return redirect('seller_dashboard')


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle, VehicleImage

@login_required
def edit_vehicle_image(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)

    if request.method == "POST":
        # Get multiple uploaded images
        images = request.FILES.getlist('new_images')

        for image in images:
            VehicleImage.objects.create(vehicle=vehicle, image=image)

        return redirect('seller_dashboard')  # redirect to your dashboard or wherever needed

@login_required
def delete_vehicle_image(request, image_id):
    image = get_object_or_404(VehicleImage, id=image_id)
    image.delete()
    messages.success(request, "Deleted Successfully.")
    return redirect('seller_dashboard')


@login_required
def saved_vehicles(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('vehicle')
    return render(request, 'listings/saved_vehicles.html', {'favorites': favorites})


@login_required
def toggle_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)
    if vehicle.status == "Available":
        vehicle.status = "Sold"
    else:
        vehicle.status = "Available"
    vehicle.save()
    messages.success(request, f"Status updated to {vehicle.status}.")
    return redirect('seller_dashboard')


@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)
    vehicle.delete()
    messages.success(request, "Deleted Successfully.")
    return redirect('seller_dashboard')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile  # Ensure Profile model is imported

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        bio = request.POST.get('bio')
        profile_image = request.FILES.get('profile_image')

        profile.phone = phone
        profile.address = address
        profile.bio = bio
        if profile_image:
            profile.profile_image = profile_image

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')  # Redirect to the same page

    return render(request, 'listings/profile.html', {'profile': profile})

from .forms import CustomSignupForm, CustomLoginForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomSignupForm, CustomLoginForm

def auth_view(request):
    signup_form = CustomSignupForm()
    login_form = CustomLoginForm()

    if request.method == 'POST':
        if 'signup' in request.POST:
            signup_form = CustomSignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('home')
            else:
                messages.error(request, "Don't Use Similar Username And Passowrd.")
        
        elif 'login' in request.POST:
            login_form = CustomLoginForm(request, data=request.POST)
            if login_form.is_valid():
                user = authenticate(
                    username=login_form.cleaned_data['username'],
                    password=login_form.cleaned_data['password']
                )
                if user is not None:
                    login(request, user)
                    messages.success(request, "Logged in successfully!")
                    return redirect('home')
                else:
                    messages.error(request, "Invalid credentials.")
            else:
                messages.error(request, "Error in login form.")

    return render(request, 'listings/auth.html', {
        'signup_form': signup_form,
        'login_form': login_form
    })

from django.http import JsonResponse

@login_required
def get_vehicle_images_json(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, seller=request.user)
    images = vehicle.images.all()
    data = {
        "images": [{"id": img.id, "url": img.image.url} for img in images]
    }
    return JsonResponse(data)
