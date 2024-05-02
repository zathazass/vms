from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from vendors.serializers import (
    VendorSerializer,
    CreatePurchaseOrderSerializer,
    EditPurchaseOrderSerializer,
    VendorPOAcknowledgmentSerializer,
)
from vendors.models import Vendor, PurchaseOrder, VendorPerformanceLog
from rest_framework.permissions import IsAuthenticated


def get_vendor_object_or_none(vendor_id):
    try:
        return Vendor.objects.get(pk=vendor_id)
    except Vendor.DoesNotExist:
        return None


class VendorListCreateAPI(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = VendorSerializer
    queryset = Vendor.objects.all().order_by("id")


class VendorRetrieveUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = VendorSerializer
    lookup_url_kwarg = "vendor_id"
    queryset = Vendor.objects.all()


class VendorPerformanceAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id):

        vendor = get_vendor_object_or_none(vendor_id)
        if not vendor:
            return Response(
                data={"detail": "No Vendor matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

        vendor_performance_details = {
            "name": vendor.name,
            "on_time_delivery_rate": vendor.on_time_delivery_rate,
            "quality_rating_avg": vendor.quality_rating_avg,
            "average_response_time": vendor.average_response_time,
            "fulfillment_rate": vendor.fullfilment_rate,
        }
        return Response(data=vendor_performance_details, status=status.HTTP_200_OK)


class PurchaseOrderListCreateAPI(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = CreatePurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all().order_by("id")


class PurchaseOrderRetrieveUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = EditPurchaseOrderSerializer
    queryset = PurchaseOrder.objects.all()
    lookup_url_kwarg = "po_id"

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().partial_update(request, *args, **kwargs)


class PurchaseOrderAcknowledgmentAPI(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = VendorPOAcknowledgmentSerializer
    lookup_url_kwarg = "po_id"
    queryset = PurchaseOrder.objects.all()


class VendorPerformanceTrendAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, vendor_id):
        vendor = get_vendor_object_or_none(vendor_id)
        if not vendor:
            return Response(
                data={"detail": "No Vendor matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

        logs = (
            VendorPerformanceLog.objects.filter(vendor=vendor)
            .order_by("date")
            .values(
                "date",
                "on_time_delivery_rate",
                "quality_rating_avg",
                "average_response_time",
                "fulfillment_rate",
            )
        )

        return Response(
            data={
                "vendor": {"id": vendor.id, "name": vendor.name},
                "performance_logs": logs,
            }
        )
