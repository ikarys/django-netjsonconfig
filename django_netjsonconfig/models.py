from .base.config import AbstractConfig, TemplatesVpnMixin
from .base.device import AbstractDevice
from .base.tag import AbstractTaggedTemplate, AbstractTemplateTag
from .base.template import AbstractTemplate
from .base.vpn import AbstractVpn, AbstractVpnClient
from .base.ipam import AbstractSupernetVpn, AbstractIpamSubnet


class Config(TemplatesVpnMixin, AbstractConfig):
    """
    Concrete Config model
    """
    class Meta(AbstractConfig.Meta):
        abstract = False


class Device(AbstractDevice):
    """
    Concrete device model
    """
    class Meta(AbstractDevice.Meta):
        abstract = False


class TemplateTag(AbstractTemplateTag):
    """
    Concrete template tag model
    """
    class Meta(AbstractTemplateTag.Meta):
        abstract = False


class TaggedTemplate(AbstractTaggedTemplate):
    """
    tagged item model with support for UUID primary keys
    """
    class Meta(AbstractTaggedTemplate.Meta):
        abstract = False


class Template(AbstractTemplate):
    """
    Concrete Template model
    """
    class Meta(AbstractTemplate.Meta):
        abstract = False


class VpnClient(AbstractVpnClient):
    """
    Concrete VpnClient model
    """
    class Meta(AbstractVpnClient.Meta):
        abstract = False


class Vpn(AbstractVpn):
    """
    Concrete VPN model
    """
    class Meta(AbstractVpn.Meta):
        abstract = False


class SupernetVPN(AbstractSupernetVpn):
    """
    CONCRETE SUPERNET VPN model
    """
    class Meta(AbstractSupernetVpn.Meta):
        abstract = False

# *********************************************************************************************************************
# *********************************************************************************************************************
# TODO: QUICK AND DIRTY, move later
# *********************************************************************************************************************
# *********************************************************************************************************************
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from ipaddress import IPv4Network


# --------------------------
# ----------- MODELS
# --------------------------
class IpamSubnet(AbstractIpamSubnet):
    class Meta(AbstractIpamSubnet.Meta):
        abstract = False


# --------------------------
# ----------- METHODS
# --------------------------

def get_supernet():
    supernet = IpamSubnet.objects.filter(parent=None, is_used=False).first()

    if not supernet:
        raise Exception("No supernet available")

    supernet.is_used = True
    supernet.save()
    return supernet.subnet


def get_subnet_from_supernet(supernet_cidr):
    if not supernet_cidr:
        raise Exception("supernet_cidr cannot be null")

    subnet = IpamSubnet.objects.filter(parent__subnet=supernet_cidr, is_used=False).order_by("id").first()

    if not subnet:
        raise Exception("No subnet available for %s" % supernet_cidr)

    subnet.is_used = True
    subnet.save()
    return subnet.subnet


# --------------------------
# ----------- SIGNALS
# --------------------------
@receiver(post_save, sender=Vpn)
def attribute_supernet(sender, instance, created, **kwargs):
    if created:
        if SupernetVPN.objects.filter(vpn=instance).count() < 1:
            SupernetVPN.objects.create(
                vpn=instance,
                supernet=get_supernet(),
                subnet="192.167.1.0/24"
            )


@receiver(post_save, sender=IpamSubnet)
def split_subnet(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.parent:
        nw = IPv4Network(instance.subnet)
        for sub in nw.subnets(new_prefix=28):
            IpamSubnet.objects.create(
                subnet=str(sub),
                parent=instance
            )


@receiver(pre_delete, sender=Config)
def clean_subnet(sender, instance, **kwargs):
    try:
        IpamSubnet.objects.filter(subnet=instance.context["Scope_subnet"], is_used=True).update(is_used=False)
    except Exception as err:
        print(err)


@receiver(pre_delete, sender=Vpn)
def clean_supernet(sender, instance, **kwargs):
    # Find the supernet instance
    supernet_vpn = SupernetVPN.objects.get(vpn=instance)
    # Free the subnet contained in the supernet
    IpamSubnet.objects.filter(parent__subnet=supernet_vpn.supernet, is_used=True).update(is_used=False)
    # Free the supernet
    IpamSubnet.objects.filter(subnet=supernet_vpn.supernet, is_used=True).update(is_used=False)


@receiver(pre_delete, sender=VpnClient)
def clean_config(sender, instance, **kwargs):
    context_field = [
        "dhcp_address_start",
        "dhcp_address_limit",
        "lan_interface_address",
        "lan_netmask_dot",
        "lan_network_address",
        "lan_broadcast_address",
        "lan_netmask_cidr",
        "Scope_subnet"
    ]
    config = Config.objects.get(id=instance.config_id)
    config_updated = False
    for field in context_field:
        if field in config.context:
            config_updated = True
            del config.context[field]

    if config_updated:
        config.save()


# @receiver(post_save, sender=Config)
@receiver(post_save, sender=VpnClient)
def device_attribute_vpn_supernet(sender, instance, created, **kwargs):
    if not created:
        return

    config = instance.config

    if "Scope_subnet" in config.context:
        return

    vpn_supernet = SupernetVPN.objects.get(vpn__id=instance.vpn_id)
    net = IPv4Network(get_subnet_from_supernet(vpn_supernet.supernet))
    subnets = net.subnets(new_prefix=28)
    subnet = next(subnets)

    config.context["dhcp_address_start"] = str(subnet[2]).split(".")[-1]
    config.context["dhcp_address_limit"] = str(subnet.num_addresses - 3)
    config.context["lan_interface_address"] = str(subnet[1])
    config.context["lan_netmask_dot"] = str(subnet.netmask)
    config.context["lan_network_address"] = str(subnet.network_address)
    config.context["lan_broadcast_address"] = str(subnet.broadcast_address)
    config.context["lan_netmask_cidr"] = "28"
    config.context["Scope_subnet"] = str(subnet)
    config.save()