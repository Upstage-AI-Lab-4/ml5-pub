#!/bin/bash
airflow db init
airflow users create --username admin --firstname admin --lastname kisms --role Admin --email admin@gmail.com --password 123
airflow scheduler & airflow webserver -p 8080