# Generated by Django 3.2.15 on 2022-09-18 12:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0004_auto_20211003_0941'),
        ('coop', '0029_auto_20220617_1056'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreatePaymentLogEntry',
            fields=[
                ('logentry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='log.logentry')),
                ('amount', models.FloatField()),
                ('payment_date', models.DateField()),
            ],
            bases=('log.logentry',),
        ),
    ]