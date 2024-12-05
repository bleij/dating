from django.db import models


class User(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    id = models.PositiveIntegerField(primary_key=True)
    telegram_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, null=True, blank=True)

    # Обязательные поля для профиля
    city = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    description = models.TextField()

    def __str__(self):
        return f'{self.name}'


class Interaction(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_interactions")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_interactions")
    is_like = models.BooleanField()

    class Meta:
        unique_together = ('from_user', 'to_user')


class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_user2")
    created_at = models.DateTimeField(auto_now_add=True)
