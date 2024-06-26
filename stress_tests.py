import unittest
from cassandra.cluster import Cluster
from utils import *
import uuid
import asyncio

class CassandraStressTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.cluster = Cluster()
        cls.keyspace = 'cinema'
        cls.session = cls.cluster.connect(cls.keyspace)
        cls.user1 = 'user1'
        cls.user2 = 'user2'
        cls.movie_name = 'Test Movie'
        cls.seat = 1  # Define seat here
        cls.setup_test_movie()

    @classmethod
    def setup_test_movie(cls):
        query = f"INSERT INTO cinema.movies (movie_name, taken_seats) VALUES ('{cls.movie_name}', {{}});"
        cls.session.execute(query)

    async def async_add_reservation(self, user, session, movie_name, seat):
        add_reservation(user, session, movie_name, seat)

    async def async_delete_reservation(self, user, session, reservation_id, movie_name, seat):
        delete_reservation(user, session, reservation_id, movie_name, seat)

    async def async_update_reservation(self, user, session, reservation_id, movie_name, seat, new_seat):
        update_reservation(user, session, reservation_id, movie_name, seat, new_seat)

    async def test_stress_1(self):
        """ Stress Test 1: The client makes the same request very quickly (10,000 times). """
        tasks = []
        for _ in range(10000):
            reservation_id = uuid.uuid4()
            tasks.append(asyncio.create_task(self.async_delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat)))
        await asyncio.gather(*tasks)

    async def test_stress_2(self):
        """ Stress Test 2: Two or more clients make possible requests randomly (10,000 times). """
        tasks = []
        for _ in range(10000):
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user1, self.session, self.movie_name, self.seat)))
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user2, self.session, self.movie_name, self.seat)))
        await asyncio.gather(*tasks)

    async def test_stress_3(self):
        """ Stress Test 3: Immediate occupancy of all seats/reservations by 2 clients. """
        tasks = []
        for seat in range(1, 16):
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user1, self.session, self.movie_name, seat)))
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user2, self.session, self.movie_name, seat)))
        await asyncio.gather(*tasks)

    async def test_stress_4(self):
        """ Stress Test 4: (only for pairs) constant cancellations and seat occupancy (for the same seat 10,000 times). """
        tasks = []
        for _ in range(10000):
            reservation_id = uuid.uuid4()
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user1, self.session, self.movie_name, self.seat)))
            tasks.append(asyncio.create_task(self.async_delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat)))
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user2, self.session, self.movie_name, self.seat)))
            tasks.append(asyncio.create_task(self.async_delete_reservation(self.user2, self.session, reservation_id, self.movie_name, self.seat)))
        await asyncio.gather(*tasks)

    async def test_stress_5(self):
        """ Stress Test 5: (only for pairs) Update of 1,000 reservations (e.g., change date for all reservations). """
        tasks = []
        for _ in range(1000):
            reservation_id = uuid.uuid4()
            tasks.append(asyncio.create_task(self.async_add_reservation(self.user1, self.session, self.movie_name, self.seat)))
            tasks.append(asyncio.create_task(self.async_update_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat, self.seat + 1)))
            tasks.append(asyncio.create_task(self.async_delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat + 1)))
        await asyncio.gather(*tasks)


    @classmethod
    def tearDownClass(cls):
        cls.session.shutdown()
        cls.cluster.shutdown()

if __name__ == "__main__":
    unittest.main()
