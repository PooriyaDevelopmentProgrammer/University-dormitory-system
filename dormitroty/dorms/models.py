from django.db import models


class Dorm(models.Model):
    name = models.CharField(max_length=100)
    location = models.TextField()
    gender_restriction = models.CharField(
        max_length=6,
        choices=[('male', 'Male'), ('female', 'Female')],
        default='male'
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.gender_restriction}"


class Room(models.Model):
    dorm = models.ForeignKey(Dorm, related_name='rooms', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField()
    floor = models.IntegerField()
    full = models.BooleanField(default=False)

    def __str__(self):
        return f"Room {self.room_number} - {self.dorm.name}"

    def available_beds(self):
        return self.beds.filter(is_occupied=False).count()

    def set_full_true(self):
        if self.available_beds() == 0:
            self.full = True
            self.save()
        else:
            self.full = False
            self.save()


class Bed(models.Model):
    room = models.ForeignKey(Room, related_name='beds', on_delete=models.CASCADE)
    bed_number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Bed {self.bed_number} in Room {self.room.room_number}"
