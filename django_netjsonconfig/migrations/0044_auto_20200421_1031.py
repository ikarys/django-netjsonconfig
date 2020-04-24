# Generated by Django 3.0.5 on 2020-04-21 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_netjsonconfig', '0043_add_indexes_on_ip_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='type',
            field=models.CharField(choices=[('generic', 'Generic'), ('vpn', 'VPN-client'), ('ipam', 'IPAM')], db_index=True, default='generic', help_text='template type, determines which features are available', max_length=16, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='vpn',
            name='backend',
            field=models.CharField(choices=[('django_netjsonconfig.vpn_backends.OpenVpn', 'OpenVPN'), ('django_netjsonconfig.vpn_backends.WireGuardVpn', 'WireGuard')], help_text='Select VPN configuration backend', max_length=128, verbose_name='VPN backend'),
        ),
    ]
