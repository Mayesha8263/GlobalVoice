# Generated by Django 5.0.1 on 2024-03-10 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('globalVoice', '0005_inputtranslation_user_outputtranslation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='favourite_languages',
            field=models.ManyToManyField(blank=True, related_name='users_favourite_languages', to='globalVoice.language'),
        ),
    ]
