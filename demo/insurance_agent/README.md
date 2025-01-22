# Insurance Agent Demo

This demo showcases how the **Curve** can be used to manage insurance-related tasks such as policy inquiries, initiating policies, and updating claims or deductibles. In this demo, the assistant provides factual information related to insurance policies (e.g., car, boat, house, motorcycle).

The system can perform a variety of tasks, such as answering insurance-related questions, retrieving policy coverage details, initiating policies, and updating claims or deductibles.

## Available Actions

### Ask About Insurance
Get instant answers about policies, coverage, and insurance terms
```
Endpoint: /policy/qa
Example: "What does comprehensive coverage include?"
```

### Check Coverage Details
View policy specifics for any vehicle or property
```
Endpoint: /policy/coverage
Required: Type (car/boat/house/motorcycle)
Example: /policy/coverage?policy_type=car
```

### Start New Policy
Begin coverage for your assets
```
Endpoint: /policy/initiate
Required:
- Asset type (car/boat/house/motorcycle)
- Initial deductible amount
Example: /policy/initiate?policy_type=car&deductible=500
```

### Manage Claims
Add or update claim information
```
Endpoint: /policy/claim
Required: Claim ID
Optional: Adjustor notes
Example: /policy/claim?claim_id=123&notes=Damage_assessed
```

### Adjust Deductibles
Modify your policy deductible amounts
```
Endpoint: /policy/deductible
Required:
- Policy ID
- New deductible amount
Example: /policy/deductible?policy_id=ABC123&deductible=1000
```

The assistant automatically picks the right service based on your request - just ask naturally about what you need.

# Starting the demo
1. Please make sure the pre-requisites are installed correctly
2. Start Curve
   ```sh
   sh run_demo.sh
   ```
3. Navigate to http://localhost:18080/
4. Tell me what can you do for me?"

# Observability
Curve gateway publishes stats endpoint at http://localhost:19901/stats. In this demo we are using prometheus to pull stats from curve  and we are using grafana to visalize the stats in dashboard. To see grafana dashboard follow instructions below,

1. Start grafana and prometheus using following command
   ```yaml
   docker compose --profile monitoring up
   ```
1. Navigate to http://localhost:3000/ to open grafana UI (use admin/grafana as credentials)
1. From grafana left nav click on dashboards and select "Intelligent Gateway Overview" to view curve  gateway stats
