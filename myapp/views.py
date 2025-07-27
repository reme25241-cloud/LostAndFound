# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.conf import settings

from django.contrib.auth import get_user_model

from .forms import *
from .models import *

def base(request):
    return render(request, 'base.html')

from django.contrib.auth import get_user_model
from .models import Message

CustomUser = get_user_model()

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserSignupForm  # Make sure this matches your form name

def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful. Welcome!")
            return redirect('dashboard')  # Change as per your URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserSignupForm()

    return render(request, 'registration/signup.html', {'form': form})


# Handle user logout
def logout_view(request):
    logout(request)
    return redirect('login')

# profile
@login_required
def profile_view(request):
    return render(request, 'account/profile.html', {'user': request.user})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'account/edit_profile.html', {'form': form})




# dashboard
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import render


def about(request):
    return render(request, 'about/about.html')

# chat
@login_required
def user_list_view(request):
    users = get_user_model().objects.exclude(id=request.user.id)  
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def chat_view_by_id(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')
        Message.objects.create(sender=request.user, receiver=other_user, text=text, image=image)
        return redirect('chat', user_id=other_user.id)  # ✅ Corrected: use user_id instead of username

    return render(request, 'users/chat.html', {
        'messages': messages,
        'receiver': other_user
    })

# Feedback

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import FeedbackForm
from .models import Feedback

@login_required
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return render(request, 'feedback/feedback_thanks.html')  # Create this template
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback.html', {'form': form})

@login_required
def view_feedbacks(request):
    if request.user.is_superuser:
        feedbacks = Feedback.objects.all().order_by('-created_at')
        return render(request, 'feedback/view_feedbacks.html', {'feedbacks': feedbacks})
    else:
        return redirect('dashboard')


# product List


@login_required
def dashboard(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    location_filter = request.GET.get('location', '')
    date_filter = request.GET.get('date', '')

    items = LostItem.objects.filter(is_archived=False)

    if search_query:
        items = items.filter(
            Q(full_name__icontains=search_query) |
            Q(item_description__icontains=search_query) |
            Q(location_lost__icontains=search_query)
        )

    if category_filter:
        items = items.filter(item_category=category_filter)

    if location_filter:
        items = items.filter(location_lost__icontains=location_filter)

    if date_filter:
        items = items.filter(date_lost=date_filter)

    context = {'items': items}
    return render(request, 'dashboard/dashboard.html',context)


def terms_and_conditions(request):
    return render(request, 'terms/terms.html')

# mainApplicationFunctionality20240625
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LostItemForm, FoundReportForm
from .models import LostItem

@login_required
def report_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            lost_item = form.save(commit=False)
            lost_item.user = request.user
            lost_item.save()
            return redirect('lost_items_list')
    else:
        form = LostItemForm()
    return render(request, 'lost_found/report_lost.html', {'form': form})


@login_required
def report_found_item(request, lost_item_id):
    lost_item = get_object_or_404(LostItem, id=lost_item_id)
    if request.method == 'POST':
        form = FoundReportForm(request.POST, request.FILES)
        if form.is_valid():
            found_report = form.save(commit=False)
            found_report.lost_item = lost_item
            found_report.save()  # triggers auto-email
            return redirect('lost_items_list')
    else:
        form = FoundReportForm()
    return render(request, 'lost_found/report_found.html', {
        'form': form,
        'lost_item': lost_item
    })


from django.core.paginator import Paginator

@login_required
def lost_items_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    items = LostItem.objects.all()

    if query:
        items = items.filter(
            Q(full_name__icontains=query) |
            Q(item_description__icontains=query) |
            Q(location_lost__icontains=query)
        )

    if category and category != 'all':
        items = items.filter(item_category=category)

    paginator = Paginator(items.order_by('-reported_at'), 10)
    page_number = request.GET.get('page')
    paginated_items = paginator.get_page(page_number)

    return render(request, 'lost_found/lost_items_list.html', {
        'items': paginated_items,
        'query': query,
        'category': category
    })

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.utils import timezone

@login_required
def mark_as_found(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)

    if request.method == 'POST':
        item.is_found = True
        item.found_timestamp = timezone.now()
        item.found_by = request.user
        item.save()
        messages.success(request, 'Thank you for reporting this item as found.')
        return redirect('lost_items_list')

    return render(request, 'lost_found/confirm_mark_as_found.html', {'item': item})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def archive_lost_item(request, item_id):
    item = get_object_or_404(LostItem, id=item_id, user=request.user)
    item.is_archived = True
    item.save()
    return redirect('dashboard')



@login_required
def archived_items_view(request):
    user = request.user
    archived_items = LostItem.objects.filter(user=user, is_archived=True)
    
    return render(request, 'lost_found/archived_items.html', {
        'archived_items': archived_items
    })