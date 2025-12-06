from django.shortcuts import render


def home(request):
    """Landing page view"""
    return render(request, "landing/home.html")


def services(request):
    """Services page - describes what HealthBridge offers"""
    return render(request, "landing/services.html")


def about(request):
    """About page - mission and background"""
    return render(request, "landing/about.html")


def contact(request):
    """Contact page - initial contact information and form stub"""
    return render(request, "landing/contact.html")
