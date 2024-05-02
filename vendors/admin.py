from django.contrib import admin

from vendors.models import Vendor, VendorPerformanceLog, PurchaseOrder

admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(VendorPerformanceLog)