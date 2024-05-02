from rest_framework import serializers
from vendors.models import Vendor, PurchaseOrder

from vendors.services import generate_vendor_code, generate_po_number


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"
        read_only_fields = [
            "vendor_code",
            "on_time_delivery_rate",
            "quality_rating_avg",
            "average_response_time",
            "fullfilment_rate",
        ]

    def create(self, validated_data):
        recent_vendor = Vendor.objects.order_by("-id").first()
        recent_vendor_code = recent_vendor.id if recent_vendor else 0
        name = validated_data.get("name")
        vendor_code = generate_vendor_code(name, recent_vendor_code)

        vendor = Vendor.objects.create(**validated_data, vendor_code=vendor_code)
        return vendor


class CreatePurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = [
            "po_number",
            "delivery_date",
            "status",
            "quality_rating",
            "acknowledgment_date",
        ]

    def create(self, validated_data):
        recent_po = PurchaseOrder.objects.order_by("-id").first()
        recent_po_id = recent_po.id if recent_po else 0
        po_number = generate_po_number(recent_po_id)

        vendor = PurchaseOrder.objects.create(
            **validated_data,
            po_number=po_number,
            delivery_date=None,
            quality_rating=None,
            acknowledgment_date=None,
        )
        return vendor


class EditPurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = [
            "po_number",
            "order_date",
            "issue_date",
            "acknowledgment_date",
        ]


class VendorPOAcknowledgmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ["acknowledgment_date"]
