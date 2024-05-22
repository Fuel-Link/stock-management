# stock-management for Fuel Link

To start the service run

```bash
docker compose up -d
```

The following endpoint will keep track of fuel consumption so that future use can be estimated.

```bash
curl -X POST "http://localhost:5001/usePump" \
     -H "Content-Type: application/json" \
     -d '{
           "pump_id": 1,
           "amount": 50.0,
	       "client "user123"
         }'
```


The following endpoint will keep track of when a pump is restocked.

```bash
curl -X POST "http://localhost:5001/restockFuel" \
     -H "Content-Type: application/json" \
     -d '{
           "pump_id": 1,
           "amount": 500.0
         }'
```

The following endpoint will assess current fuel levels, looks at the average consumption and the future prices and determines if it is better to wait out for lower prices, or if the current fuels levels won't permit that.

```bash
curl -X POST "http://localhost:5001/assessFuel" \
     -H "Content-Type: application/json" \
     -d '{
           "pump_id": 1,
           "predictions": [
             {"ds": "Tue, 21 May 2024 00:00:00 GMT", "yhat": 1.76397585647508},
             {"ds": "Wed, 22 May 2024 00:00:00 GMT", "yhat": 1.76649328681331},
             {"ds": "Thu, 23 May 2024 00:00:00 GMT", "yhat": 1.76919776648663},
             {"ds": "Fri, 24 May 2024 00:00:00 GMT", "yhat": 1.77131522456402},
             {"ds": "Sat, 25 May 2024 00:00:00 GMT", "yhat": 1.77020828899238},
             {"ds": "Sun, 26 May 2024 00:00:00 GMT", "yhat": 1.77307277228299},
             {"ds": "Mon, 27 May 2024 00:00:00 GMT", "yhat": 1.77994033779222},
             {"ds": "Tue, 28 May 2024 00:00:00 GMT", "yhat": 1.78269360519984},
             {"ds": "Wed, 29 May 2024 00:00:00 GMT", "yhat": 1.7846804267302},
             {"ds": "Thu, 30 May 2024 00:00:00 GMT", "yhat": 1.786666361541},
             {"ds": "Fri, 31 May 2024 00:00:00 GMT", "yhat": 1.78789961639956},
             {"ds": "Sat, 01 Jun 2024 00:00:00 GMT", "yhat": 1.78576741266683},
             {"ds": "Sun, 02 Jun 2024 00:00:00 GMT", "yhat": 1.7874918211277},
             {"ds": "Mon, 03 Jun 2024 00:00:00 GMT", "yhat": 1.79313176412767},
             {"ds": "Tue, 04 Jun 2024 00:00:00 GMT", "yhat": 1.79459746084505}
           ]
         }'
```

returns in the following format:
```bash
{"average_daily_consumption":number,"current_stock":number,"decision":"Wait"}
or
{"average_daily_consumption":number,"current_stock":number,"decision":"Buy Now"}
```