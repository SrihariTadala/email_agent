# Freight Quote Agent - Complete Documentation 
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

**1. How would you scale this to 1000 emails/day?**


Queue-Based - 100-300 emails/day

```


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

                    
```


Event-Driven - 1000+ emails/day

```

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


```



### **2. What happens if the LLM hallucinates data?**

Multi-Layer Defense Strategy:
- **Layer 1:** Ensemble methods (multiple models)
- **Layer 2:** Human-in-the-Loop Verification
- **Layer 3:** Structured Output Validation
- **Layer 4:** Confidence Scoring




### **3. How do you handle rate limits (Gmail API, LLM API)?**

**Rate Limits:**
- Gmail API limiter *(100/day free, 2000/day Workspace)*
- Groq API limiter *(30/min, 14,400/day free)*
- Redis-based token bucket algorithm
- Fallback provider strategies
- Monitoring & alerts


### **4. What's your strategy for improving extraction accuracy?**

1. **Handle invalid or missing data**
   - Detect impossible or non-existent ZIP codes
   - Ask user for clarification via chatbot/email
   - Send reminder emails if customer hasn’t booked in 7 or 14 days

2. **Fine-tuning with human corrections**
   - Every dispatcher correction becomes a training example  
   - After ~200 corrections (≈1 month at 50 reviews/day) → fine-tune the model for your domain  
   - This gradually eliminates recurring extraction errors

3. **Focus on High-Value Routes First (Risk-Based Prioritization)**
   - Losing a \$10K quote due to extraction error is far more expensive than a \$500 quote  
   - Add **5 real freight request examples** to every LLM prompt  
   - Include scenarios: pallets, LTL, hazmat, cross-country loads  
   - Ensure correct **city/state/ZIP** combinations  
   - Identify your **top 20 routes** (LA–Chicago, NY–Miami, etc.) and build specialized prompts  
   - Add custom validation for major customer ZIP codes

4. **Implement Confidence Thresholds by Quote Value**
   - Low confidence + high quote amount → send to human review  
   - High confidence + low quote amount → auto-approve  
   - Avoid automation on ambiguous high-risk freight

5. **Build Ensemble System for Critical Lanes**
   - Use multiple models (Groq Llama 3.1, OpenAI, Claude)  
   - Compare outputs — disagreements are flagged for review  
   - Useful for high-volume business lanes

6. **Create Feedback Loop with Sales Team**
   - Sales knows industry-specific terminology:  
     - “reefer” = refrigerated  
     - “LTL” = less-than-truckload  
     - “container drayage”, “air freight”, etc.  
   - Add their corrections into the fine-tuning dataset

7. **Dynamic Pricing Engine (Optional Enhancement)**
   - Calculate optimal quote using:  
     - market demand  
     - lane seasonality  
     - fuel prices  
     - supply/demand imbalance  
   - Can increase margins by **8–18%**  
   - Add cheapest fuel stops along the route to optimize cost

8. **Smart Margin Adjustment**
   - Minimum margin thresholds  
   - Discounts for repeat customers  
   - Higher margin for urgent loads  
   - Lower margin when capacity is high  
   - Premium pricing for hazmat/high-risk freight

9. **High-Value Customer Dashboard**
   - Top customers  
   - Top drivers  
   - Top dispatchers  
   - Frequently booked lanes  
   - Quote conversion rate  

10. **Driver Performance Insights**
    - Track on-time %  
    - Fuel efficiency  
    - Driving style  
    - Delay patterns  
    - Reward high performers  

****
** 5. How would you add human review for high-value quotes?**


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


****


Test Cases- 



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

 4. Hazmat Scenarios

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


