from vendors.models import Vendor, PurchaseOrder
import pytest
import json
from vendors.tests.api_tests import create_vendor
from django.utils import timezone


@pytest.mark.django_db
class TestVendorModelShould:
    def test_returns_expected_values_when_create_new(self):
        vendor = Vendor.objects.create(
            name="A",
            contact_details="9924232422\nsme@gmail.com",
            address="234, Tamilnadu.",
        )

        assert vendor.name == "A"
        assert vendor.contact_details == "9924232422\nsme@gmail.com"
        assert vendor.address == "234, Tamilnadu."
        assert vendor.on_time_delivery_rate == 0.0
        assert vendor.quality_rating_avg == 0.0
        assert vendor.average_response_time == 0.0
        assert vendor.fullfilment_rate == 0.0


@pytest.mark.django_db
class TestPurchaseOrderModelShould:
    def test_returns_expected_values_when_create_new(self):
        vendor = create_vendor()
        po = PurchaseOrder.objects.create(
            vendor=vendor,
            po_number="PO-2024-000001",
            order_date=timezone.now(),
            items=json.dumps(["leather straps"]),
            quantity=20,
        )

        assert po.vendor == vendor
        assert po.po_number != ""
        assert po.order_date is not None
        assert po.delivery_date is None
        assert po.items == json.dumps(["leather straps"])
        assert po.quantity == 20
        assert po.status == "pending"
        assert po.quality_rating is None
        assert po.issue_date is not None
        assert po.acknowledgment_date is None
