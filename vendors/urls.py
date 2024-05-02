from django.urls import path, include
from vendors.apis import (
    VendorListCreateAPI,
    VendorRetrieveUpdateDestroyAPI,
    PurchaseOrderListCreateAPI,
    PurchaseOrderAcknowledgmentAPI,
    PurchaseOrderRetrieveUpdateDestroyAPI,
    VendorPerformanceAPI,
    VendorPerformanceTrendAPI
)

app_name = "vendors"

urlpatterns = [
    path(
        "api/",
        include(
            [
                path(
                    "vendors/",
                    VendorListCreateAPI.as_view(),
                    name="vendor_list_create_api",
                ),
                path(
                    "vendors/<int:vendor_id>/",
                    VendorRetrieveUpdateDestroyAPI.as_view(),
                    name="vendor_retrieve_update_destroy_api",
                ),
                path(
                    "vendors/<int:vendor_id>/performance",
                    VendorPerformanceAPI.as_view(),
                    name="vendor_performance_api",
                ),
                path(
                    "vendors/<int:vendor_id>/performance/logs",
                    VendorPerformanceTrendAPI.as_view(),
                    name="vendor_performance_log_api",
                ),
                path(
                    "purchase_orders/",
                    PurchaseOrderListCreateAPI.as_view(),
                    name="po_list_create_api",
                ),
                path(
                    "purchase_orders/<int:po_id>",
                    PurchaseOrderRetrieveUpdateDestroyAPI.as_view(),
                    name="po_retrieve_update_destroy_api",
                ),
                path(
                    "purchase_orders/<int:po_id>/acknowledge",
                    PurchaseOrderAcknowledgmentAPI.as_view(),
                    name="po_acknowledgment_api",
                ),
            ]
        ),
    )
]
