from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter

from .base.admin import (AbstractConfigForm, AbstractConfigInline, AbstractDeviceAdmin, AbstractTemplateAdmin,
                         AbstractVpnAdmin, AbstractVpnForm, BaseForm)
from .models import Config, Device, Template, Vpn, SupernetVPN, IpamSubnet


class ConfigForm(AbstractConfigForm):
    class Meta(AbstractConfigForm.Meta):
        model = Config


class TemplateForm(BaseForm):
    class Meta(BaseForm.Meta):
        model = Template


class TemplateAdmin(AbstractTemplateAdmin):
    form = TemplateForm


class VpnForm(AbstractVpnForm):
    class Meta(AbstractVpnForm.Meta):
        model = Vpn


class VpnAdmin(AbstractVpnAdmin):
    form = VpnForm


class ConfigInline(AbstractConfigInline):
    model = Config
    form = ConfigForm
    extra = 0


class DeviceAdmin(AbstractDeviceAdmin):
    inlines = [ConfigInline]


class SupernetVPNAdmin(admin.ModelAdmin):
    model = SupernetVPN
    list_display = ("vpn", "supernet", "subnet")


class IpamSubnetFilter(SimpleListFilter):
    title = 'IpamSubnet' # a label for our filter
    parameter_name = 'pages' # you can put anything here

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ('supernet', 'supernet'),
            ('subnet', 'subnet'),
        ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        if self.value() == 'supernet':
            # Get websites that have at least one page.
            return queryset.distinct().filter(parent__isnull=True)

        if self.value():
            # Get websites that don't have any pages.
            return queryset.distinct().filter(parent__isnull=False)


class IpamSubnetAdmin(admin.ModelAdmin):
    model = IpamSubnet
    list_display = ("subnet", "get_parent", "is_used")
    list_filter = ("is_used", IpamSubnetFilter)

    def get_parent(self, obj):
        return obj.parent.subnet if obj.parent else None


admin.site.register(Device, DeviceAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(Vpn, VpnAdmin)
admin.site.register(SupernetVPN, SupernetVPNAdmin)
admin.site.register(IpamSubnet, IpamSubnetAdmin)
