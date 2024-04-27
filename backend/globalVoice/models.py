from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Model for each user
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    favourite_languages = models.ManyToManyField('Language', blank=True, related_name='users_favourite_languages')

    groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name='custom_user_groups'
    )

    user_permissions = models.ManyToManyField(
        to=Permission,
        blank=True,
        related_name='custom_user_permissions'
    )

    def __str__(self):
        return self.username

# Model for languages saved
class Language(models.Model):
    code = models.CharField(max_length=30, default=None)
    name = models.CharField(max_length=255)

# Model for inputs by the user
class InputTranslation(models.Model):
    input_sentence = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='input_translations')

# Model for translated outputs 
class OutputTranslation(models.Model):
    output_sentence = models.TextField()
    context = models.CharField(max_length=255)
    dialect = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='output_translations')
