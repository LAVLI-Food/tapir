# Generated by Django 3.1.13 on 2021-08-29 13:35

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("log", "0003_textlogentry"),
        ("shifts", "0012_allow_slot_requirements_empty"),
    ]

    operations = [
        migrations.CreateModel(
            name="CreateShiftAttendanceLogEntry",
            fields=[
                (
                    "logentry_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="log.logentry",
                    ),
                ),
                ("values", django.contrib.postgres.fields.hstore.HStoreField()),
                ("slot_name", models.CharField(blank=True, max_length=255)),
                (
                    "shift",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="shifts.shift"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("log.logentry",),
        ),
    ]
