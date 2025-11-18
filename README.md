# Freight Quote Agent - Complete Documentation 📚
**Built with:** Python, FastAPI, Gmail API, Groq (Llama 3.1), Mapbox, ReportLab


##  System Architecture

```
┌─────────────┐
│   Gmail     │ ← OAuth2 Authentication
│   Inbox     │ ← Monitors unread emails (60s polling)
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Email Filter       │ ← is_quote_request() 
│  (Keyword matching) │ 
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  LLM Extractor      │ ← Groq + Llama 3.1 8B
│  (Shipment Details) │ ← Structured JSON output
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Quote API          │ ← FastAPI + Mapbox
│  (Calculate Price)  │ ← Real distance calculation
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  PDF Generator      │ ← ReportLab + Route Maps
│  (Professional Doc) │ ← Route visualization
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Gmail Reply        │ ← Threaded responses
│  (Send w/Attach)    │ ← Mark as read
└─────────────────────┘
```

---

## Key Features


- **Gmail Integration** (OAuth2)
  - Secure authentication
  - Read unread emails
  - Send threaded replies with attachments
  - Mark emails as read

- **LLM Extraction** (Groq + Llama 3.1)
  - Structured JSON output
  - Validation & error handling
  - Confidence scoring
  - Hallucination mitigation

- **Quote API** (FastAPI)
  - Real distance calculation (Mapbox)
  - Complex pricing logic
  - Route map generation
  - Input validation
  - **Swagger docs**: http://localhost:8000/docs

- **PDF Generation** (ReportLab)
  - Professional quote documents
  - Route map visualization
  - Itemized cost breakdown
  - Company branding




Overview of entire system

<span style="font-size:26px; font-weight:600;">
1. How would you scale this to 1000 emails/day?
</span>
Queue-Based - 100-300 emails/day


┌──────────────┐
│ Gmail Monitor│ ← Polls every 30s
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Redis Queue  │ ← Stores email IDs
└──────┬───────┘
       │
   ┌───┴────┬────────┬────────┐
   ▼        ▼        ▼        ▼
[Worker1][Worker2][Worker3][Worker4]
   │        │        │        │
   └────────┴────────┴────────┘
              ▼
       ┌──────────────┐
       │ PostgreSQL   │ ← Track processed emails

                    

Event-Driven - 1000+ emails/day

┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Gmail Inbox  │
│ (Push Mode)  │────► Gmail Pub/Sub Notifications
└──────────────┘              │
                              ▼
                    ┌──────────────────┐
                    │   Message Queue  │
                    │   (Redis/RabbitMQ)│
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          ┌─────────┐   ┌─────────┐   ┌─────────┐
          │Worker 1 │   │Worker 2 │   │Worker N │
          │(Extract)│   │(Extract)│   │(Extract)│
          └─────────┘   └─────────┘   └─────────┘
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL DB  │
                    │   (Persistent)   │
                    └──────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          ┌─────────┐   ┌─────────┐   ┌─────────┐
          │Worker 3 │   │Worker 4 │   │Worker N │
          │(Quote)  │   │(Quote)  │   │(Quote)  │
          └─────────┘   └─────────┘   └─────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Email Sender   │
                    │   (Rate Limited) │
                    └──────────────────┘





<span style="font-size:26px; font-weight:600;">
2. What happens if the LLM hallucinates data?
</span>

Multi-Layer Defense Strategy
Layer 1: Ensemble methods (multiple models)
Layer 2: Human-in-the-Loop Verification
Layer 3: Structured Output Validation
Layer 4: Confidence Scoring


<span style="font-size:26px; font-weight:600;">
3. How do you handle rate limits (Gmail API, LLM API)?
</span>
How do you handle rate limits (Gmail API, LLM API)?

Rate Limits:

Gmail API limiter (100/day free, 2000/day Workspace)
Groq API limiter (30/min, 14,400/day free)
Redis-based token bucket algorithm
Fallback provider strategies
Monitoring & alerts

<span style="font-size:26px; font-weight:600;">
4. What's your strategy for improving extraction accuracy?
</span>



1. Make up zip codes that don't exist , and invent chatbot


If customer hasn’t booked in 7,14 days: reaminder mails . Autoreply is the most aspect i believe
system sends personalized offer.

2. Fine-tuning with human corrections
Every time dispatcher corrects an extraction = training example
After 200 corrections (1 month at 50 reviews/day) → fine-tune model


3. Focus on High-Value Routes First (Risk-Based Prioritization)

Add 5 real freight request examples to every prompt
Include common scenarios: pallets, LTL, hazmat, cross-country routes
Show correct city/state/zip combinations


Losing a $10K quote due to error is worse than a $500 one

Route patterns matter: Identify your top 20 routes (LA-Chicago, NY-Miami, etc.)
Create specialized prompts for high-volume lanes
Build custom validation for major customer zip codes


4. Implement Confidence Thresholds by Quote Value (Smart Automation)

5. Build Ensemble System for Critical Lanes (Multi-Model Validation)

6. Create Feedback Loop with Sales Team (Domain Expertise)

Sales provides industry-specific terminology ("reefer" = refrigerated, "LTL" = less-than-truckload)

7.  Dynamic Pricing Engine
Calculate the optimal quote price using:
market demand
lane seasonality
fuel prices
supply/demand imbalance
This increases margin by 8–18%
add cheapest gas stations to the driver along the route so that the cost is opttimized.

8. Smart Margin Adjustment
Automatically apply: minimum margin thresholds discount for exisiting custoemrs higher margins for “urgent”
lower margins when capacity is high premium pricing for high-risk freight

High-Value Customer Dashboard
top customers
top drivers
top dispatchers

Driver Performance Insights
Track:
on-time %
fuel efficiency
driving style
delays
Reward high performers



<span style="font-size:26px; font-weight:600;">
5. How would you add human review for high-value quotes?
</span>

Human Review System:
Priority-based review queue (urgent/high/normal) if amt is greater , slack 
FastAPI review dashboard with React frontend
Slack notifications for new reviews
One-click approve/edit/reject
Training dataset from corrections

Prometheus metrics
Grafana dashboards
Alert rules (failure rate, queue backlog, slow processing)
Health check endpoints
Slack daily summaries









class QuoteRequest(BaseModel):
    origin_zip: str
    destination_zip: str
    weight_lbs: float
    pieces: int
    dimensions: DimensionsModel
    commodity: str
    special_services: List[str]
    equipment_type: str
    pickup_date: date   # REQUIRED
    hazmat: bool        # REQUIRED
    value_usd: float    # REQUIRED


base example

{
  "origin_zip": "90021",
  "destination_zip": "60601",
  "weight_lbs": 800,
  "pieces": 2,
  "dimensions": { "length": 48, "width": 40, "height": 60 },
  "commodity": "electronics",
  "special_services": ["liftgate"],
  "equipment_type": "dry_van",
  "pickup_date": "2025-11-19",
  "hazmat": false,
  "value_usd": 50000
}


Test Case A2 — Simple furniture shipment

{
  "origin_zip": "10001",
  "destination_zip": "77001",
  "weight_lbs": 1200,
  "pieces": 3,
  "dimensions": { "length": 60, "width": 48, "height": 55 },
  "commodity": "furniture",
  "special_services": [],
  "equipment_type": "dry_van",
  "pickup_date": "2025-11-22",
  "hazmat": false,
  "value_usd": 15000
}

Test Case B2 — Medical/Pharma with inside delivery

{
  "origin_zip": "90021",
  "destination_zip": "30301",
  "weight_lbs": 500,
  "pieces": 1,
  "dimensions": { "length": 48, "width": 36, "height": 40 },
  "commodity": "medical_equipment",
  "special_services": ["inside_delivery"],
  "equipment_type": "box_truck",
  "pickup_date": "2025-12-05",
  "hazmat": false,
  "value_usd": 120000
}

Test Case C1 — Oversized machinery


{
  "origin_zip": "77001",
  "destination_zip": "90001",
  "weight_lbs": 4500,
  "pieces": 1,
  "dimensions": { "length": 120, "width": 48, "height": 70 },
  "commodity": "industrial_machinery",
  "special_services": ["liftgate"],
  "equipment_type": "flatbed",
  "pickup_date": "2025-11-30",
  "hazmat": false,
  "value_usd": 90000
}

⭐ 4. Hazmat Scenarios

{
  "origin_zip": "90021",
  "destination_zip": "85001",
  "weight_lbs": 1500,
  "pieces": 2,
  "dimensions": { "length": 48, "width": 40, "height": 55 },
  "commodity": "flammable_liquid_class_3",
  "special_services": [],
  "equipment_type": "dry_van",
  "pickup_date": "2025-12-02",
  "hazmat": true,
  "value_usd": 25000
}


