# shopping/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods, require_POST

from accounts.decorators import adult_required, premium_required
from events.models import DishIngredient, Event, Scenario
from .forms import ShoppingCalcForm
from .models import ShoppingItem, ShoppingList
from .services import build_shopping_items


def _build_result_context(form: ShoppingCalcForm):
    items = None
    grouped = {}
    dish_cards = []
    missing_dishes = []

    if not form.is_valid():
        return {
            "items": None,
            "grouped": {},
            "dish_cards": [],
            "missing_dishes": [],
        }

    scenario = form.cleaned_data["scenario"]
    dishes = list(form.cleaned_data.get("dishes") or [])
    stages = form.cleaned_data["stages"]
    people_count = form.cleaned_data["people_count"]
    duration_hours = form.cleaned_data["duration_hours"]

    items = build_shopping_items(
        scenario=scenario,
        stages=stages,
        people_count=people_count,
        duration_hours=duration_hours,
        dishes=dishes,
    )

    for i in items:
        grouped.setdefault(i["category_label"], []).append(i)

    if dishes:
        di_qs = (
            DishIngredient.objects
            .filter(dish__in=dishes)
            .select_related("dish", "ingredient")
            .order_by("dish_id", "ingredient__name")
        )

        by_dish = {}
        for di in di_qs:
            by_dish.setdefault(di.dish_id, []).append(di)

        for d in dishes:
            ing_rows = []
            dis = by_dish.get(d.id, [])
            if not dis:
                missing_dishes.append(d)
                continue

            for di in dis:
                qty_total = (di.qty_per_person * Decimal(people_count)).quantize(Decimal("0.001"))
                ing_rows.append(
                    {
                        "name": di.ingredient.name,
                        "qty": qty_total,
                        "unit": di.get_unit_display() if hasattr(di, "get_unit_display") else di.unit,
                    }
                )

            dish_cards.append({"dish": d, "ingredients": ing_rows})

    return {
        "items": items,
        "grouped": grouped,
        "dish_cards": dish_cards,
        "missing_dishes": missing_dishes,
    }


@login_required
@adult_required
@require_http_methods(["GET", "POST"])
def preview(request):
    items = None
    grouped = {}
    dish_cards = []
    missing_dishes = []

    if request.method == "POST":
        form = ShoppingCalcForm(request.POST, user=request.user)
        result = _build_result_context(form)
        items = result["items"]
        grouped = result["grouped"]
        dish_cards = result["dish_cards"]
        missing_dishes = result["missing_dishes"]
    else:
        initial = {}
        event_id = request.GET.get("event")
        scenario_id = request.GET.get("scenario")

        if event_id:
            ev = get_object_or_404(Event, pk=event_id, user=request.user)
            initial.update(
                {
                    "event": ev,
                    "scenario": ev.scenario,
                    "people_count": getattr(ev, "people_count", 4),
                    "duration_hours": getattr(ev, "duration_hours", 4),
                    "stages": ["prep", "during", "recovery"],
                }
            )
            if getattr(ev, "dish_id", None):
                initial["dishes"] = [ev.dish]
        elif scenario_id:
            sc = get_object_or_404(Scenario, pk=scenario_id)
            initial.update({"scenario": sc, "stages": ["prep", "during", "recovery"]})

        form = ShoppingCalcForm(initial=initial, user=request.user)

    return render(
        request,
        "shopping/preview.html",
        {
            "form": form,
            "items": items,
            "grouped": grouped,
            "dish_cards": dish_cards,
            "missing_dishes": missing_dishes,
        },
    )


@login_required
@adult_required
@require_POST
def ajax_preview(request):
    # Ключевой фикс: если JS дергает /ajax/preview/ без ?event=...,
    # или если <select name="event"> по какой-то причине не ушёл в POST,
    # подхватываем event/scenario из querystring.
    data = request.POST

    event_qs = request.GET.get("event")
    scenario_qs = request.GET.get("scenario")

    if event_qs and not data.get("event"):
        data = data.copy()
        data["event"] = event_qs

    if scenario_qs and not data.get("scenario"):
        data = data.copy()
        data["scenario"] = scenario_qs

    form = ShoppingCalcForm(data, user=request.user)

    ctx = _build_result_context(form)
    html = render_to_string(
        "shopping/_result.html",
        {"form": form, **ctx},
        request=request,
    )
    return JsonResponse({"ok": True, "html": html, "has_errors": bool(form.errors)})


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
    dishes = form.cleaned_data.get("dishes")

    items = build_shopping_items(
        scenario=scenario,
        stages=stages,
        people_count=people_count,
        duration_hours=duration_hours,
        dishes=dishes,
    )

    sl = ShoppingList.objects.create(
        user=request.user,
        event=event,
        scenario=scenario,
        people_count=people_count,
        duration_hours=duration_hours,
        stages=stages,
    )

    if dishes:
        sl.dishes.set(dishes)

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
def my_lists(request):
    qs = (
        ShoppingList.objects
        .filter(user=request.user)
        .select_related("event", "scenario")
        .order_by("-created_at", "-id")
    )
    return render(request, "shopping/my_lists.html", {"lists": qs})


@login_required
@adult_required
def detail(request, pk: int):
    sl = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    return render(request, "shopping/detail.html", {"sl": sl})