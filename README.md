# Fetch
# Receipt Processor API

A FastAPI service that processes receipts and calculates reward points.

## Setup

1. Clone repository:
```bash
2.docker build -t receipt-processor .
docker run -p 8000:8000 receipt-processor


# API ENDPOINTS
submit  a receipt:

curl -X POST http://localhost:8000/receipts/process \
  -H "Content-Type: application/json" \
  -d '{
    "retailer": "M&M Corner Market",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "14:30",
    "items": [
      {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
      {"shortDescription": "Emils Cheese Pizza", "price": "12.25"}
    ],
    "total": "18.74"
  }'

Get points for a receipt:
curl http://localhost:8000/receipts/<id>/points
