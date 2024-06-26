# Cassandra distributed database cinema application
## Instructions
Setup:
```shell
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
In case you don't have an installed Tkinter:
```shell
sudo apt-get install python3.11-tk
```

Start the database:
```shell
docker compose up -d && ./scripts/initialize.sh
```

Start the application:
```shell
python app.py
```

When entering an application, you need to specify your username - it is needed to keep a record, which user made a reservation and to interact with your own reservations.

Execute stress tests:
```shell
python stress_tests.py
```

Remove the database:
```shell
docker compose down --volumes
```