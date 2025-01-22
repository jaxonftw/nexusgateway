# Public API Integration Demo

Connect your LLM with external services through **Curve**. This example demonstrates real-time currency data integration using a public REST API.

## Overview

The demo shows how to:
- Route LLM responses through external APIs
- Handle real-time data fetching
- Process structured API responses
- Maintain conversation context

## Setup

1. Start the demo:
   ```sh
   sh run_demo.sh
   ```

2. Open chat interface:
   ```
   http://localhost:18080/
   ```

## Example Interactions

Chat naturally about currency data:

```
You: What's today's USD to EUR rate?
Assistant: Let me check the current rate...
[Fetches from API]
The current USD to EUR exchange rate is 0.92

You: How about Japanese Yen?
Assistant: According to the latest data...
[Fetches from API]
1 USD equals 148.23 JPY
```

## Behind the Scenes

The demo:
1. Receives your query
2. Extracts currency pairs
3. Calls Frankfurter API
4. Formats response
5. Returns natural language answer

## Technical Details

- API: frankfurter.dev
- Base Currency: USD
- Update Frequency: Real-time
- Response Format: JSON

## Stats & Monitoring

Monitor the integration:
```sh
# View metrics dashboard
docker compose --profile monitoring up
```

Access at:
- http://localhost:19901/stats
- http://localhost:3000/ (admin/grafana)
