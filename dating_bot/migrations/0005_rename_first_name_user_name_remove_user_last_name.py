# Generated by Django 5.1.3 on 2024-12-05 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dating_bot", "0004_remove_user_photo"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="first_name",
            new_name="name",
        ),
        migrations.RemoveField(
            model_name="user",
            name="last_name",
        ),
    ]
