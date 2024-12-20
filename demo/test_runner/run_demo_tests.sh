#!/bin/bash
set -eu

for demo in currency_exchange hr_agent
do
  echo "******************************************"
  echo "Running tests for $demo ..."
  echo "****************************************"
  cd ../$demo
  curve up curve_config.yaml
  docker compose up -d
  cd ../test_runner
  TEST_DATA=../$demo/test_data.yaml poetry run pytest
  cd ../$demo
  docker compose down -v
  curve down
  cd ../test_runner
done
