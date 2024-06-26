# Cassandra distributed database cinema application
## Instructions
Setup:
```shell
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the database:
```shell
docker compose up -d && ./scripts/initialize.sh
```

Start the application:
```shell
python main.py
```

Execute stress tests:
```shell
python stress_tests.py
```

Remove the database:
```shell
docker compose down --volumes
```
