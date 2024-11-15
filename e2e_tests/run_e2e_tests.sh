#/bin/bash
# if any of the commands fail, the script will exit
set -e

. ./common_scripts.sh

print_disk_usage

mkdir -p ~/curve_logs
touch ~/curve_logs/modelserver.log

print_debug() {
  log "Received signal to stop"
  log "Printing debug logs for server"
  log "===================================="
  tail -n 500 ~/curve_logs/modelserver.log
  log "Printing debug logs for docker"
  log "===================================="
  tail -n 500 ../build.log
}

# trap 'print_debug' INT TERM ERR

log starting > ../build.log

log building and running function_callling demo
log ===========================================
cd ../demos/weather_forecast
docker compose up weather_forecast_service --build -d
cd -

log building and install model server
log =================================
cd ../server
poetry install
cd -

log building and installing curve cli
log ==================================
cd ../curve /tools
sh build_cli.sh
cd -

log building docker image for curve  gateway
log ======================================
cd ../
curve build
cd -

log startup curve  gateway with function calling demo
cd ..
tail -F ~/curve_logs/modelserver.log &
server_tail_pid=$!
curve down
curve up demos/weather_forecast/curve_config.yaml
kill $server_tail_pid
cd -

log running e2e tests
log =================
poetry install
poetry run pytest

log shutting down the curve  gateway service
log ======================================
cd ../
curve down
cd -

log shutting down the weather_forecast demo
log =======================================
cd ../demos/weather_forecast
docker compose down
cd -
