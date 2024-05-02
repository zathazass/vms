from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from vendors.constants import PO_STATUS
from django.utils import timezone

from vendors.services import (
    calculate_on_time_delivery_rating_avg,
    calculate_quality_rating_avg,
    calculate_response_time,
    calculate_fullfilment_rate,
)

PO_ORDER_STATUS_CHOICES = (
    (PO_STATUS.pending, "Pending"),
    (PO_STATUS.completed, "Completed"),
    (PO_STATUS.cancelled, "Cancelled"),
)


class Vendor(models.Model):
    name = models.CharField(max_length=64)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=32, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fullfilment_rate = models.FloatField(default=0.0)


class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    po_number = models.CharField(max_length=32, unique=True)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField(null=True)
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(
        max_length=16, choices=PO_ORDER_STATUS_CHOICES, default=PO_STATUS.pending
    )
    quality_rating = models.FloatField(null=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True)


class VendorPerformanceLog(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()


@receiver(post_save, sender=PurchaseOrder)
def purchase_order_updated(sender, instance: PurchaseOrder, created, **kwargs):
    if not created:
        vendor = instance.vendor
        if instance.status == PO_STATUS.completed:
            vendor.on_time_delivery_rate = calculate_on_time_delivery_rating_avg(vendor)
            vendor.quality_rating_avg = calculate_quality_rating_avg(vendor)

        if instance.acknowledgment_date:
            vendor.average_response_time = calculate_response_time(instance.vendor)

        vendor.fullfilment_rate = calculate_fullfilment_rate(vendor)

        vendor.save()

        if instance.status == PO_STATUS.completed:
            VendorPerformanceLog.objects.create(
                date=timezone.now(),
                vendor=vendor,
                on_time_delivery_rate=vendor.on_time_delivery_rate,
                quality_rating_avg=vendor.quality_rating_avg,
                average_response_time=vendor.average_response_time,
                fulfillment_rate=vendor.fullfilment_rate,
            )


post_save.connect(purchase_order_updated, sender=PurchaseOrder)
