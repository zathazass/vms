import json

from django.urls import reverse
from rest_framework.test import APITestCase
from vendors.models import Vendor, PurchaseOrder
from django.utils import timezone
from django.contrib.auth.models import User

def vendor_data():
    return {
        "name": "ABC Traders",
        "contact_details": "12345\nabc@traders.in",
        "address": "342, New Delhi.",
    }


def create_vendor():
    return Vendor.objects.create(**vendor_data())


def purchase_order_data():
    vendor = create_vendor()
    return {
        "vendor": vendor,
        "po_number": "PO-2024-000001",
        "order_date": timezone.now(),
        "items": json.dumps(["leather strap"]),
        "quantity": 100,
    }


def create_purchase_order():
    return PurchaseOrder.objects.create(**purchase_order_data())


class TestVendorCreateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse("vendors:vendor_list_create_api")
        self.data = vendor_data()

    def test_should_raises_400_when_without_data(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})
        assert response.status_code == 400

    def test_should_returns_201_when_proper_data(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        assert response.status_code == 201

    def test_should_auto_create_vendor_code_when_201(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        assert response.status_code == 201

        data = response.json()

        assert "id" in data
        assert "vendor_code" in data
        assert "vendor_code" != ""


class TestVendorListAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse("vendors:vendor_list_create_api")

    def test_returns_paginated_response_when_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        status_code = response.status_code
        data = response.json()

        assert status_code == 200
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

    def test_returns_empty_list_when_table_is_empty(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        status_code = response.status_code
        data = response.json().get("results")

        assert status_code == 200
        assert len(data) == 0

    def test_return_vendors_when_creates_many(self):
        abc_traders = vendor_data()
        xyz_traders = {
            "name": "XYZ Traders",
            "contact_details": "63534522\nxyz@traders.in",
            "address": "43, Chennai, Tamilnadu.",
        }

        self.client.force_login(self.user)
        self.client.post(self.url, abc_traders)
        self.client.post(self.url, xyz_traders)

        response = self.client.get(self.url)
        status_code = response.status_code
        data = response.json().get("results")

        assert status_code == 200
        assert len(data) == 2


class TestVendorRetrieveAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        create_vendor()

    def test_raises_404_when_invalid_vendor_id(self):
        url = reverse(
            "vendors:vendor_retrieve_update_destroy_api", kwargs={"vendor_id": 234}
        )
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 404

    def test_returns_vendor_details_when_id_exists(self):
        url = reverse(
            "vendors:vendor_retrieve_update_destroy_api", kwargs={"vendor_id": 1}
        )
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 200
        assert "id" in response.json()


class TestVendorUpdateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        create_vendor()
        self.url = reverse(
            "vendors:vendor_retrieve_update_destroy_api", kwargs={"vendor_id": 1}
        )

    def test_raises_400_when_missing_input_data(self):
        self.client.force_login(self.user)
        response = self.client.put(self.url, data={"contact_details": ""})
        assert response.status_code == 400

    def test_returns_updated_data_when_proper_input(self):
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data={
                "name": "New Traders",
                "contact_details": "12345\nabc@traders.in",
                "address": "123, Tamilnadu.",
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert "id" in data
        assert data["name"] == "New Traders"
        assert data["contact_details"] == "12345\nabc@traders.in"
        assert data["address"] == "123, Tamilnadu."

    def test_update_does_not_change_auto_calculated_values(self):
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data={
                "name": "New Traders",
                "contact_details": "12345\nabc@traders.in",
                "address": "123, Tamilnadu.",
                "on_time_delivery_rate": 1.23,
                "quality_rating_avg": 1.23,
                "average_response_time": 1.23,
                "fullfilment_rate": 1.23,
            },
        )
        data = response.json()
        vendor = Vendor.objects.first()

        assert response.status_code == 200
        assert "id" in data
        assert vendor.on_time_delivery_rate == 0.0
        assert vendor.quality_rating_avg == 0.0
        assert vendor.average_response_time == 0.0
        assert vendor.fullfilment_rate == 0.0


class TestVendorDeleteAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_raises_404_when_invalid_vendor_id(self):
        url = reverse(
            "vendors:vendor_retrieve_update_destroy_api", kwargs={"vendor_id": 232}
        )
        self.client.force_login(self.user)
        response = self.client.delete(url)
        assert response.status_code == 404

    def test_returns_204_when_delete_a_vendor(self):
        create_vendor()

        url = reverse(
            "vendors:vendor_retrieve_update_destroy_api", kwargs={"vendor_id": 1}
        )
        self.client.force_login(self.user)
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Vendor.objects.count() == 0


class TestPurchaseOrderCreateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse("vendors:po_list_create_api")
        self.data = purchase_order_data()

    def test_should_raises_400_when_without_data(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})
        assert response.status_code == 400

    def test_should_returns_201_when_proper_data(self):
        self.data.update({"vendor": 1})
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        assert response.status_code == 201
        assert "id" in response.json()


class TestPurchaseOrderListAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse("vendors:po_list_create_api")

    def test_returns_paginated_response_when_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        status_code = response.status_code
        data = response.json()

        assert status_code == 200
        assert "count" in data
        assert "next" in data
        assert "previous" in data
        assert "results" in data

    def test_returns_empty_list_when_table_is_empty(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        status_code = response.status_code
        data = response.json().get("results")

        assert status_code == 200
        assert len(data) == 0

    def test_return_pos_when_po_exists(self):
        create_purchase_order()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        data = response.json()
        assert response.status_code == 200
        assert len(data["results"]) == 1


class TestPurchaseOrderRetrieveAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        create_purchase_order()

    def test_raises_404_when_invalid_po_id(self):
        url = reverse("vendors:po_retrieve_update_destroy_api", kwargs={"po_id": 25})
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 404

    def test_returns_po_details_when_id_exists(self):
        url = reverse("vendors:po_retrieve_update_destroy_api", kwargs={"po_id": 1})
        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 200
        assert "id" in response.json()


class TestPurchaseOrderUpdateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.po = create_purchase_order()
        self.url = reverse(
            "vendors:po_retrieve_update_destroy_api", kwargs={"po_id": 1}
        )

    def test_raises_400_when_missing_input_data(self):
        self.client.force_login(self.user)
        response = self.client.put(self.url, data={})
        assert response.status_code == 400

    def test_returns_updated_data_when_proper_input(self):
        self.client.force_login(self.user)
        response = self.client.put(
            self.url,
            data={
                "delivery_date": "2024-04-30",
                "quality_rating": 4.5,
                "items": json.dumps(["belt metal"]),
                "vendor": self.po.vendor.id,
                "status": "completed",
                "quantity": 250,
            },
        )
        data = response.json()

        assert response.status_code == 200
        assert "id" in data
        assert data["status"] == "completed"


class TestPurchaseOrderDeleteAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_raises_404_when_invalid_po_id(self):
        url = reverse("vendors:po_retrieve_update_destroy_api", kwargs={"po_id": 44})
        self.client.force_login(self.user)
        response = self.client.delete(url)
        assert response.status_code == 404

    def test_returns_204_when_delete_a_po(self):
        create_purchase_order()

        url = reverse("vendors:po_retrieve_update_destroy_api", kwargs={"po_id": 1})
        self.client.force_login(self.user)
        response = self.client.delete(url)
        assert response.status_code == 204
        assert PurchaseOrder.objects.count() == 0

class TestVendorPerformanceTrendAPI(APITestCase):
    def test_new_vendor_should_not_have_records(self):
        create_vendor()

        url = reverse("vendors:vendor_performance_log_api", kwargs={"vendor_id": 1})
        self.user = User.objects.create_user(username='testuser', password='password123')

        self.client.force_login(self.user)
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.json()['performance_logs']) == 0