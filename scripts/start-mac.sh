#!/bin/bash
docker build -t pm-app .
docker run -d --name pm-container -p 8000:8000 --env-file .env pm-app