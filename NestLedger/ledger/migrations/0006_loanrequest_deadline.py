# Generated by Django 5.1.5 on 2025-02-06 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0005_loan_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanrequest',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
    ]
