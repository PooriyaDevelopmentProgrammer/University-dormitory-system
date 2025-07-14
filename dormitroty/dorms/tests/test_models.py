from django.test import TestCase
from dorms.models import Dorm, Room, Bed


class DormModelTest(TestCase):
    def setUp(self):
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male",
            description="Test Description"
        )

    def test_dorm_creation(self):
        self.assertEqual(self.dorm.name, "Test Dorm")
        self.assertEqual(self.dorm.location, "Test Location")
        self.assertEqual(self.dorm.gender_restriction, "male")
        self.assertEqual(self.dorm.description, "Test Description")

    def test_dorm_string_representation(self):
        self.assertEqual(str(self.dorm), "Test Dorm - male")


class RoomModelTest(TestCase):
    def setUp(self):
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male"
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=4,
            floor=1
        )

    def test_room_creation(self):
        self.assertEqual(self.room.dorm, self.dorm)
        self.assertEqual(self.room.room_number, "101")
        self.assertEqual(self.room.capacity, 4)
        self.assertEqual(self.room.floor, 1)

    def test_room_string_representation(self):
        self.assertEqual(str(self.room), "Room 101 - Test Dorm")


class BedModelTest(TestCase):
    def setUp(self):
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male"
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=4,
            floor=1
        )
        self.bed = Bed.objects.create(
            room=self.room,
            bed_number="B1",
            is_occupied=False
        )

    def test_bed_creation(self):
        self.assertEqual(self.bed.room, self.room)
        self.assertEqual(self.bed.bed_number, "B1")
        self.assertFalse(self.bed.is_occupied)

    def test_bed_string_representation(self):
        self.assertEqual(str(self.bed), "Bed B1 in Room 101")


class RoomFullSignalTest(TestCase):
    def setUp(self):
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male"
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=2,
            floor=1
        )
        self.bed1 = Bed.objects.create(room=self.room, bed_number="1", is_occupied=False)
        self.bed2 = Bed.objects.create(room=self.room, bed_number="2", is_occupied=False)

    def test_room_full_becomes_true_when_all_beds_occupied(self):
        self.assertFalse(self.room.full)

        self.bed1.is_occupied = True
        self.bed1.save()
        self.room.refresh_from_db()
        self.assertFalse(self.room.full)

        self.bed2.is_occupied = True
        self.bed2.save()
        self.room.refresh_from_db()
        self.assertTrue(self.room.full)

    def test_room_full_becomes_false_when_bed_is_freed(self):
        self.bed1.is_occupied = True
        self.bed1.save()
        self.bed2.is_occupied = True
        self.bed2.save()
        self.room.refresh_from_db()
        self.assertTrue(self.room.full)

        self.bed2.is_occupied = False
        self.bed2.save()
        self.room.refresh_from_db()
        self.assertFalse(self.room.full)
