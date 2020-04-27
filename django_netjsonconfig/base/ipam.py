from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractSupernetVpn(models.Model):
    vpn = models.ForeignKey('django_netjsonconfig.Vpn',
                            on_delete=models.CASCADE)
    supernet = models.CharField(max_length=20,
                                help_text=_('Supernet block for devices.'),
                                unique=True,
                                null=False,
                                blank=False)
    subnet = models.CharField(max_length=20,
                              help_text=_('Subnet for back to back.'),
                              unique=False,
                              null=False,
                              blank=False)

    class Meta:
        abstract = True
        unique_together = ('supernet', 'vpn')
        verbose_name = _('Supernet VPN')
        verbose_name_plural = _('Supernets VPN')


class AbstractIpamSubnet(models.Model):
    subnet = models.CharField(max_length=20, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    is_used = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name = _('IPAM subnet')
        verbose_name_plural = _('IPAM subnets')
