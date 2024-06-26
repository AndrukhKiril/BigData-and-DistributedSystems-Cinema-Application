CREATE KEYSPACE cinema WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2};
USE cinema;

CREATE TABLE movies (movie_name text, show_timestamp timestamp, taken_seats set<int>, PRIMARY KEY (movie_name));

INSERT INTO movies(movie_name, show_timestamp, taken_seats) VALUES ('The Lord of the Rings Trilogy', '2024-07-25 18:00', {});
INSERT INTO movies(movie_name, show_timestamp, taken_seats) VALUES ('Furiosa', '2024-08-14 15:15', {});

CREATE TABLE reservations (reservation_id uuid, name text, movie_name text, reservation_timestamp timestamp, seat_number int, PRIMARY KEY (name, reservation_id));

INSERT INTO reservations(reservation_id, name, movie_name, reservation_timestamp, seat_number) VALUES (uuid(), 'Krzysztof', 'The Lord of the Rings Trilogy', currentTimestamp(), 4);
INSERT INTO reservations(reservation_id, name, movie_name, reservation_timestamp, seat_number) VALUES (uuid(), 'Krzysztof', 'Furiosa', currentTimestamp(), 35);

UPDATE movies SET taken_seats = taken_seats + {4} WHERE movie_name = 'The Lord of the Rings Trilogy';
UPDATE movies SET taken_seats = taken_seats + {35} WHERE movie_name = 'Furiosa';
