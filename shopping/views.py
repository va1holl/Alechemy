from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import adult_required, premium_required
from .forms import ShoppingCalcForm
from .models import ShoppingItem, ShoppingList
from .services import build_shopping_items


@login_required
@adult_required
@require_http_methods(["GET", "POST"])
def preview(request):
    items = None

    if request.method == "POST":
        form = ShoppingCalcForm(request.POST, user=request.user)
        if form.is_valid():
            scenario = form.cleaned_data["scenario"]
            stages = form.cleaned_data["stages"]
            people_count = form.cleaned_data["people_count"]
            duration_hours = form.cleaned_data["duration_hours"]
            intensity = form.cleaned_data["intensity"]

            items = build_shopping_items(
                scenario=scenario,
                stages=stages,
                people_count=people_count,
                duration_hours=duration_hours,
                intensity=intensity,
            )
    else:
        form = ShoppingCalcForm(user=request.user)

    return render(
        request,
        "shopping/preview.html",
        {
            "form": form,
            "items": items,
        },
    )


@login_required
@adult_required
@premium_required
@require_http_methods(["POST"])
def create_from_preview(request):
    form = ShoppingCalcForm(request.POST, user=request.user)
    if not form.is_valid():
        messages.error(request, "Не получилось сохранить список: проверь форму.")
        return redirect("shopping:preview")

    scenario = form.cleaned_data["scenario"]
    event = form.cleaned_data["event"]
    stages = form.cleaned_data["stages"]
    people_count = form.cleaned_data["people_count"]
    duration_hours = form.cleaned_data["duration_hours"]
    intensity = form.cleaned_data["intensity"]

    items = build_shopping_items(
        scenario=scenario,
        stages=stages,
        people_count=people_count,
        duration_hours=duration_hours,
        intensity=intensity,
    )

    sl = ShoppingList.objects.create(
        user=request.user,
        event=event,
        scenario=scenario,
        people_count=people_count,
        duration_hours=duration_hours,
        intensity=intensity,
        stages=stages,
    )

    ShoppingItem.objects.bulk_create(
        [
            ShoppingItem(
                shopping_list=sl,
                name=i["name"],
                category=i["category"],
                unit=i["unit"],
                qty=i["qty"],
                is_auto=True,
            )
            for i in items
        ]
    )

    messages.success(request, "Список покупок сохранён.")
    return redirect("shopping:detail", pk=sl.pk)


@login_required
@adult_required
def detail(request, pk: int):
    sl = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    return render(request, "shopping/detail.html", {"sl": sl})


@login_required
@adult_required
def my_lists(request):
    qs = ShoppingList.objects.filter(user=request.user).select_related("event", "scenario")
    return render(request, "shopping/my_lists.html", {"lists": qs})