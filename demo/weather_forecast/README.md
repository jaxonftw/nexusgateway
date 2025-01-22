# Function calling

This demo shows how you can use Curve's core function calling capabilites.

# Starting the demo

1. Please make sure the pre-requisites are installed correctly
2. Start Curve

3. ```sh
   sh run_demo.sh
   ```
4. Navigate to http://localhost:18080/
5. You can type in queries like "how is the weather?"

# Observability

Curve gateway publishes stats endpoint at http://localhost:19901/stats. In this demo we are using prometheus to pull stats from curve  and we are using grafana to visalize the stats in dashboard. To see grafana dashboard follow instructions below,

1. Start grafana and prometheus using following command
   ```yaml
   docker compose --profile monitoring up
   ```
2. Navigate to http://localhost:3000/ to open grafana UI (use admin/grafana as credentials)
3. From grafana left nav click on dashboards and select "Intelligent Gateway Overview" to view curve  gateway stats

## Performance Tracking

Choose your preferred monitoring solution:

### Quick Start
```sh
# Launch with default monitoring
sh run_demo.sh
```

### Available Dashboards

#### Jaeger
```sh
# Start with Jaeger tracing
sh run_demo.sh jaeger

# View at http://localhost:16686/
```

#### Signoz
```sh
# Launch with Signoz
sh run_demo.sh signoz

# Access dashboard at http://localhost:3301/
```

#### Logfire
1. Add your API key to `.env`:
   ```
   LOGFIRE_API_KEY=your_key_here
   ```

2. Start with Logfire:
   ```sh
   sh run_demo.sh logfire
   ```

3. View logs in your Logfire dashboard

### Cleanup

Stop all services:
```sh
sh run_demo.sh down
```
