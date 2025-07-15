# Python
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from dorms.models import Dorm, Room, Bed
from users.models import User


class DormAPIViewTest(APITestCase):
    def setUp(self):
        # Create a test admin user
        self.admin_user = User.objects.create_superuser(
            student_code='11111111111', password='admin123', email='admin@example.com',
            national_code='1234567890', phone_number='+989398413991'
        )
        self.normal_user = User.objects.create_user(
            student_code='11111111112', password='normal123', email='normal@example.com',
            national_code='1234567891', phone_number='+989398413992'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Create test dorms
        self.dorm1 = Dorm.objects.create(name="Dorm A", location="Location A")
        self.dorm2 = Dorm.objects.create(name="Dorm B", location="Location B")

    def test_get_dorms(self):
        response = self.client.get('/api/dorms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Dorm A")
        self.assertEqual(response.data[1]['name'], "Dorm B")

    def test_create_dorm(self):
        data = {
            "name": "Dorm C",
            "location": "Location C"
        }
        response = self.client.post('/api/dorms/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Dorm C")
        self.assertEqual(response.data['location'], "Location C")

    def test_search_dorms(self):
        response = self.client.get('/api/dorms/', {'name': 'Dorm A'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Dorm A')

    def test_create_dorm_as_non_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post('/api/dorms/', {
            "name": "Dorm B",
            "location": "Location B",
            "gender_restriction": "female",
            "description": "A dorm for female students."
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DormDetailsAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            student_code='11111111111', password='admin123', email='admin@example.com',
            national_code='1234567890', phone_number='+989398413991'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)
        self.dorm = Dorm.objects.create(
            name="Test Dorm",
            location="Test Location",
            gender_restriction="male",
            description="Test Description"
        )
        self.update_url = f'/api/dorms/details/{self.dorm.id}/'
        self.delete_url = f'/api/dorms/details/{self.dorm.id}/'

    def test_update_dorm(self):
        data = {
            "name": "Updated Dorm",
            "location": "Updated Location",
            "gender_restriction": "female",
            "description": "Updated Description"
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Dorm")
        self.assertEqual(response.data['location'], "Updated Location")
        self.assertEqual(response.data['gender_restriction'], "female")
        self.assertEqual(response.data['description'], "Updated Description")

    def test_delete_dorm(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dorm.objects.filter(id=self.dorm.id).exists())


class RoomModelTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            student_code='11111111111', password='admin123', email='admin@example.com',
            national_code='1234567890', phone_number='+989398413991'
        )
        self.normal_user = User.objects.create_user(
            student_code='11111111112', password='normal123', email='normal@example.com',
            national_code='1234567891', phone_number='+989398413992'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        self.dorm = Dorm.objects.create(
            name="Dorm B",
            location="Location B",
            gender_restriction="female",
            description="A dorm for female students."
        )

    def test_create_room(self):
        room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=4,
            floor=1
        )
        self.assertEqual(room.dorm, self.dorm)
        self.assertEqual(room.room_number, "101")
        self.assertEqual(room.capacity, 4)
        self.assertEqual(room.floor, 1)
        self.assertEqual(str(room), "Room 101 - Dorm B")

    def test_available_beds(self):
        room = Room.objects.create(
            dorm=self.dorm,
            room_number="102",
            capacity=3,
            floor=2
        )
        Bed.objects.create(room=room, bed_number="1", is_occupied=False)
        Bed.objects.create(room=room, bed_number="2", is_occupied=True)
        Bed.objects.create(room=room, bed_number="3", is_occupied=False)
        self.assertEqual(room.available_beds(), 2)

    def test_search_rooms(self):
        Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=4,
            floor=1
        )
        response = self.client.get('/api/dorms/rooms/', {'dorm_id': self.dorm.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['room_number'], "101")

    def test_create_room_as_non_admin(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post('/api/dorms/rooms/', {
            "dorm": self.dorm.id,
            "room_number": "102",
            "capacity": 3,
            "floor": 2
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bed_creation_for_room(self):
        # Create a Room instance with a specific capacity
        data = {
            "dorm": self.dorm.id,
            "room_number": "101",
            "capacity": 3,
            "floor": 1
        }
        serializer = RoomSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()

        # Verify that the correct number of beds are created
        self.assertEqual(room.beds.count(), 3)

        # Check the bed numbers
        bed_numbers = [bed.bed_number for bed in room.beds.all()]
        self.assertListEqual(bed_numbers, ["1", "2", "3"])


class BedModelTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            student_code='11111111111', password='admin123', email='admin@example.com',
            national_code='1234567890', phone_number='+989398413991'
        )
        self.normal_user = User.objects.create_user(
            student_code='11111111112', password='normal123', email='normal@example.com',
            national_code='1234567891', phone_number='+989398413992'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        self.dorm = Dorm.objects.create(
            name="Dorm C",
            location="Location C",
            gender_restriction="male",
            description="Another dorm for male students."
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="201",
            capacity=2,
            floor=1
        )

    def test_create_bed(self):
        bed = Bed.objects.create(
            room=self.room,
            bed_number="1",
            is_occupied=False
        )
        self.assertEqual(bed.room, self.room)
        self.assertEqual(bed.bed_number, "1")
        self.assertFalse(bed.is_occupied)
        self.assertEqual(str(bed), "Bed 1 in Room 201")

    def test_bed_occupancy(self):
        bed = Bed.objects.create(
            room=self.room,
            bed_number="2",
            is_occupied=True
        )
        self.assertTrue(bed.is_occupied)

    def test_get_beds_by_room(self):
        bed1 = Bed.objects.create(room=self.room, bed_number="1", is_occupied=False)
        bed2 = Bed.objects.create(room=self.room, bed_number="2", is_occupied=True)
        beds = self.room.beds.all()
        self.assertIn(bed1, beds)
        self.assertIn(bed2, beds)
        self.assertEqual(len(beds), 2)

    def test_search_beds(self):
        Bed.objects.create(
            room=self.room,
            bed_number="1",
            is_occupied=False
        )
        response = self.client.get('/api/dorms/beds/', {'room_id': self.room.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['bed_number'], "1")


# Python
class BedCapacityAPITest(APITestCase):
    def setUp(self):
        # Create a test admin user
        self.admin_user = User.objects.create_superuser(
            student_code='11111111111', password='admin123', email='admin@example.com',
            national_code='1234567890', phone_number='+989398413991'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Create a test dorm and room
        self.dorm = Dorm.objects.create(
            name="Dorm A",
            location="Location A",
            gender_restriction="male",
            description="A dorm for male students."
        )
        self.room = Room.objects.create(
            dorm=self.dorm,
            room_number="101",
            capacity=2,
            floor=1
        )

    def test_create_beds_within_capacity(self):
        # Create beds within the room's capacity
        response1 = self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": "1",
            "is_occupied": False
        })
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": "2",
            "is_occupied": True
        })
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_create_bed_exceeding_capacity(self):
        # Create beds exceeding the room's capacity
        self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": "1",
            "is_occupied": False
        })
        self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": "2",
            "is_occupied": True
        })
        response = self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": "3",
            "is_occupied": False
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The number of beds cannot exceed the room's capacity", str(response.data['non_field_errors'][0]))

    def test_create_bed_and_check_resequence_and_full_false(self):
        Bed.objects.create(room=self.room, is_occupied=True)
        response = self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": 1,
            "is_occupied": False
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.room.beds.count(), 2)

        bed_numbers = [b.bed_number for b in self.room.beds.order_by('id')]
        self.assertEqual(bed_numbers, ['1', '2'])

        self.room.refresh_from_db()
        self.assertFalse(self.room.full)

    def test_create_bed_and_check_room_becomes_full(self):
        response = self.client.post('/api/dorms/beds/', {
            "room": self.room.id,
            "bed_number": 1,
            "is_occupied": True,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.room.refresh_from_db()
        self.assertTrue(self.room.full)


# Python
from django.test import TestCase
from dorms.models import Dorm, Room
from dorms.serializers import RoomSerializer


class RoomNumberAlgorithmTest(TestCase):
    def setUp(self):
        self.dorm = Dorm.objects.create(
            name="Dorm A",
            location="Location A",
            gender_restriction="male",
            description="A dorm for male students."
        )

    def test_generate_room_number_no_existing_rooms(self):
        # Test when no rooms exist in the dorm
        data = {
            "capacity": 2,
            "floor": 1,
            "dorm": self.dorm.id
        }
        serializer = RoomSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        self.assertEqual(room.room_number, "101")

    def test_generate_room_number_with_existing_rooms(self):
        # Test when rooms already exist in the dorm
        Room.objects.create(dorm=self.dorm, room_number="101", capacity=2, floor=1)
        Room.objects.create(dorm=self.dorm, room_number="102", capacity=2, floor=1)

        data = {
            "capacity": 2,
            "floor": 1,
            "dorm": self.dorm.id
        }
        serializer = RoomSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        self.assertEqual(room.room_number, "103")

    def test_generate_room_number_different_floor(self):
        # Test when creating a room on a different floor
        Room.objects.create(dorm=self.dorm, room_number="101", capacity=2, floor=1)

        data = {
            "capacity": 2,
            "floor": 2,
            "dorm": self.dorm.id
        }
        serializer = RoomSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        self.assertEqual(room.room_number, "201")
