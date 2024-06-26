import unittest
from cassandra.cluster import Cluster
from utils import *
import uuid
import threading

class CassandraStressTests(unittest.TestCase):
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

    def test_stress_1(self):
        """ Stress Test 1: The client makes the same request very quickly (10,000 times). """
        for _ in range(10000):
            reservation_id = uuid.uuid4()
            delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat)

    def test_stress_2(self):
        """ Stress Test 2: Two or more clients make possible requests randomly (10,000 times). """
        threads = []
        for _ in range(10000):
            t1 = threading.Thread(target=add_reservation, args=(self.user1, self.session, self.movie_name, self.seat))
            t2 = threading.Thread(target=add_reservation, args=(self.user2, self.session, self.movie_name, self.seat))
            threads.extend([t1, t2])
            t1.start()
            t2.start()

        for t in threads:
            t.join()

    def test_stress_3(self):
        """ Stress Test 3: Immediate occupancy of all seats/reservations by 2 clients. """
        for seat in range(1, 16):
            t1 = threading.Thread(target=add_reservation, args=(self.user1, self.session, self.movie_name, seat))
            t2 = threading.Thread(target=add_reservation, args=(self.user2, self.session, self.movie_name, seat))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

    def test_stress_4(self):
        """ Stress Test 4: Constant cancellations and seat occupancy (for the same seat 10,000 times). """
        for _ in range(10000):
            reservation_id = uuid.uuid4()
            add_reservation(self.user1, self.session, self.movie_name, self.seat)
            delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat)
            add_reservation(self.user2, self.session, self.movie_name, self.seat)
            delete_reservation(self.user2, self.session, reservation_id, self.movie_name, self.seat)

    def test_stress_5(self):
        """ Stress Test 5: Update of 1,000 reservations (e.g., change date for all reservations). """
        for _ in range(1000):
            reservation_id = uuid.uuid4()
            add_reservation(self.user1, self.session, self.movie_name, self.seat)
            update_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat, self.seat+1)
            delete_reservation(self.user1, self.session, reservation_id, self.movie_name, self.seat+1)

    @classmethod
    def tearDownClass(cls):
        cls.session.shutdown()
        cls.cluster.shutdown()

if __name__ == "__main__":
    unittest.main()
