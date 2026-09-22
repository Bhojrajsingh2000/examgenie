from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import staff_required
from .models import Blueprint
from .forms import BlueprintForm


@staff_required
def blueprint_list(request):
    blueprints = Blueprint.objects.select_related('subject').all()
    return render(request, 'blueprint/blueprint_list.html', {'blueprints': blueprints})


@staff_required
def blueprint_create(request):
    if request.method == 'POST':
        form = BlueprintForm(request.POST)
        if form.is_valid():
            blueprint = form.save(commit=False)
            blueprint.created_by = request.user
            blueprint.save()
            messages.success(request, "Blueprint created.")
            return redirect('blueprint:blueprint_list')
    else:
        form = BlueprintForm()
    return render(request, 'blueprint/blueprint_form.html', {'form': form})


@staff_required
def blueprint_detail(request, pk):
    blueprint = get_object_or_404(Blueprint, pk=pk)
    return render(request, 'blueprint/blueprint_detail.html', {'blueprint': blueprint})


@staff_required
def blueprint_delete(request, pk):
    get_object_or_404(Blueprint, pk=pk).delete()
    messages.success(request, "Blueprint deleted.")
    return redirect('blueprint:blueprint_list')
