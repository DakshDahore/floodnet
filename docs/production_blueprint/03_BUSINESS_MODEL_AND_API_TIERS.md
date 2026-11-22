# 💼 FLOODLOCK BUSINESS MODEL & COMMERCIAL API TIERS
**Market Target**: Urban Planners, Infrastructure Engineers, IoT Logistics, Independent Developers, Coastal Municipalities.  
**Currency Strategy**: Ultra-Accessible Double-Digit Indian Rupee (INR) Pricing + Frictionless UPI / GPay Flow.

---

## 1. Commercial Tier Matrix

| Feature | Free Tier (`Community`) | Premium Tier (`Pro Hydrology`) | Ultra Tier (`Enterprise Edge`) | Custom Enterprise |
| :--- | :--- | :--- | :--- | :--- |
| **Monthly Price** | **₹0 / Free Forever** | **₹49 / month** | **₹149 / month** | Custom Quote |
| **Daily API Quota** | 50 requests / day | 2,500 requests / day | 15,000 requests / day | Unlimited Dedicated |
| **Active API Keys** | 1 Key | 3 Keys | 10 Keys | Custom Provisioning |
| **Quota Refresh** | Midnight UTC | Midnight UTC | Midnight UTC | Rolling Window |
| **Tactical Map Access** | Standard Layers | All Layers + Contours | All Layers + Raw GeoJSON | Dedicated Sub-basin Tiles |
| **AI Tactical Assistant** | Read-Only Summary | 50 Interactive Queries / Day | 300 Interactive Queries / Day | Dedicated Model Instance |
| **Evacuation Webhooks** | ❌ None | ❌ None | ✅ Included (Telegram/Email) | Dedicated M2M / SMS Gateway |
| **Support SLA** | Community Forum | 48-Hour Email Support | 12-Hour Priority Email | 24/7 Phone & Slack Bridge |

---

## 2. Indian UPI / GPay Payment & Verification Pipeline

```
  [User Selects Plan (₹49)] 
            │
            ▼
  [Luxury Modal Displays Dynamic UPI QR Code]
  ↳ Encoded with Merchant/Mom's GPay UPI ID + Amount (₹49) + Dynamic Order Ref
            │
            ▼
  [User Scans & Pays in GPay / PhonePe / BHIM]
            │
            ▼
  [User Enters 12-Digit UTR / UPI Reference Number]
            │
            ▼
  [Supabase Secure API Logs Transaction]
  ↳ Table: `purchases`
  ↳ Status: `verified_provisional` (Instant Tier Unlock for 24 Hours)
  ↳ Auto-Email Alert Dispatched to Founder (Daksh) for Final Reconciliation
```

---

## 3. 5-Day 50% Partial Refund Governance

To eliminate frivolous exploitation while providing consumer reassurance:
1. **The 5-Day 50% Rule**: Every paid plan is eligible for a **50% partial refund within 5 calendar days** of purchase. 50% is retained to cover instant upfront edge compute, database indexing, and real-time weather API provisioning.
2. **Eligibility Criteria**:
   * Request filed through user dashboard within 120 hours of transaction timestamp.
   * Total API quota consumed during the period is under 20% of tier allocation.
3. **Execution & Founder Alert**:
   * User clicks *"Request Refund"* in Dashboard.
   * Automated email is instantly dispatched to `lantern.mech@gmail.com` with user ID, original UPI UTR, and 50% refund calculation.
   * 50% refund is returned directly to the originating UPI ID within 24–48 hours.
   * Plan automatically reverts to Free Community Tier upon refund dispatch.

---

## 4. Custom & Pay-As-You-Go Inquiries
* For logistics companies, maritime operators, or universities needing millions of queries:
* A sleek modal triggers an automated inquiry form directly to Daksh's founder inbox (`dakshdahore.d@gmail.com`) with project scope, expected volume, and custom SLA requirements.

