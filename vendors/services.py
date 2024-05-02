from django.utils import timezone
from django.db.models import (
    fields,
    Avg,
    Case,
    Count,
    ExpressionWrapper,
    F,
    Sum,
    Q,
    When,
    FloatField,
)
from vendors.constants import PO_STATUS


def calculate_on_time_delivery_rating_avg_old(vendor):
    orders = vendor.purchaseorder_set.filter(status=PO_STATUS.completed).values_list(
        "delivery_date", flat=True
    )
    total_orders = len(orders)
    on_time_count = 0
    for delivery_date in orders:
        if delivery_date and (timezone.now() <= delivery_date):
            on_time_count += 1

    on_time_delivery_rating = (on_time_count / total_orders) * 100
    return on_time_delivery_rating


def calculate_on_time_delivery_rating_avg(vendor):
    """Performance optimized version of calculate_on_time_delivery_rating_avg_old"""
    completed_orders = vendor.purchaseorder_set.filter(status=PO_STATUS.completed)

    completed_orders = completed_orders.annotate(
        is_on_time=Case(
            When(
                delivery_date__isnull=False, delivery_date__gte=timezone.now(), then=1
            ),
            default=0,
            output_field=fields.IntegerField(),
        )
    )

    on_time_delivery_count = completed_orders.aggregate(
        on_time_delivery_count=Count("id", filter=Q(is_on_time=1)),
        total_completed_orders=Count("id"),
    )

    total_completed_orders = on_time_delivery_count["total_completed_orders"]
    on_time_delivery_count = on_time_delivery_count["on_time_delivery_count"]

    on_time_delivery_rating = (
        (on_time_delivery_count / total_completed_orders) * 100
        if total_completed_orders > 0
        else 0
    )

    return on_time_delivery_rating


def calculate_quality_rating_avg_old(vendor):
    orders = vendor.purchaseorder_set.filter(status=PO_STATUS.completed).values_list(
        "quality_rating", flat=True
    )
    total_orders = len(orders)

    if total_orders:
        return sum([quality_rating or 0 for quality_rating in orders]) / total_orders

    return 0


def calculate_quality_rating_avg(vendor):
    """Performance optimized version of calculate_quality_rating_avg_old"""
    completed_orders = vendor.purchaseorder_set.filter(status=PO_STATUS.completed)

    quality_rating_avg = completed_orders.aggregate(
        avg_quality_rating=Avg("quality_rating", output_field=FloatField()),
        total_orders=Count("id"),
    )

    total_orders = quality_rating_avg["total_orders"]
    avg_quality_rating = quality_rating_avg["avg_quality_rating"]

    return avg_quality_rating if total_orders > 0 else 0


def calculate_response_time_old(vendor):
    vendor_pos = vendor.purchaseorder_set.filter(status=PO_STATUS.completed).values(
        "issue_date", "acknowledgment_date"
    )
    response_times = []

    for po in vendor_pos:
        if po["issue_date"] and po["acknowledgment_date"]:
            response_time = (
                po["acknowledgment_date"] - po["issue_date"]
            ).total_seconds()
            response_times.append(response_time)

    if vendor_pos:
        return sum(response_times) / len(response_times)

    return 0


def calculate_response_time(vendor):
    """Performance optimized version of calculate_response_time_old"""
    completed_orders = vendor.purchaseorder_set.filter(status=PO_STATUS.completed)

    response_time_expression = ExpressionWrapper(
        F("acknowledgment_date") - F("issue_date"), output_field=fields.DurationField()
    )

    average_response_time = completed_orders.annotate(
        response_time=response_time_expression
    ).aggregate(avg_response_time=Sum("response_time") / Count("response_time"))[
        "avg_response_time"
    ]

    return average_response_time.total_seconds() if average_response_time else 0


def calculate_fullfilment_rate_old(vendor):
    orders = vendor.purchaseorder_set.values("issue_date", "status")
    issues_count = 0
    completed_orders_count = 0
    for order in orders:
        if order["issue_date"]:
            issues_count += 1
            if order["status"] == PO_STATUS.completed:
                completed_orders_count += 1

    if completed_orders_count:
        return issues_count / completed_orders_count

    return 0


def calculate_fullfilment_rate(vendor):
    """Performance optimized version of calculate_fullfilment_rate_old"""

    orders = vendor.purchaseorder_set.values("issue_date").annotate(
        total_orders=Count("issue_date"),
        completed_orders=Count("status", filter=Q(status=PO_STATUS.completed)),
    )

    if orders:
        total_orders_count = orders[0]["total_orders"]
        completed_orders_count = orders[0]["completed_orders"]

        if completed_orders_count:
            return total_orders_count / completed_orders_count

    return 0


def generate_vendor_code(vendor_name, recent_vendor_id):
    vendor_prefix = "VE"
    current_year = timezone.datetime.now().year
    first_letter = vendor_name[0].upper()
    vendor_id = recent_vendor_id + 1
    digit = 5
    return (
        f"{vendor_prefix}-{current_year}-{first_letter}-{str(vendor_id).zfill(digit)}"
    )


def generate_po_number(recent_po_id):
    po_prefix = "PO"
    current_year = timezone.datetime.now().year
    po_id = recent_po_id + 1
    digit = 6
    return f"{po_prefix}-{current_year}-{str(po_id).zfill(digit)}"
