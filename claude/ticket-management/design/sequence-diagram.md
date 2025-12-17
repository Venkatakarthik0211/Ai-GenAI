# Sequence Diagram - Ticket Management System

## Overview
This document describes the sequence diagrams showing interactions between different components and actors in the ticket management system.

## 1. Create Ticket Sequence

```
User          Web UI        API Gateway    Ticket Service    Database    Notification Service
 │               │               │                │              │                │
 │──Submit Form─>│               │                │              │                │
 │               │               │                │              │                │
 │               │──POST /api───>│                │              │                │
 │               │   /tickets    │                │              │                │
 │               │               │                │              │                │
 │               │               │──Validate──────>│              │                │
 │               │               │   Request      │              │                │
 │               │               │                │              │                │
 │               │               │<──Validation────│              │                │
 │               │               │     OK         │              │                │
 │               │               │                │              │                │
 │               │               │──Create─────────>│              │                │
 │               │               │   Ticket       │              │                │
 │               │               │                │              │                │
 │               │               │                │──INSERT────>│                │
 │               │               │                │              │                │
 │               │               │                │<──Ticket ID──│                │
 │               │               │                │              │                │
 │               │               │<──Ticket Created│              │                │
 │               │               │                │              │                │
 │               │               │──Send Event────────────────────>│                │
 │               │               │   (Ticket Created)             │                │
 │               │               │                │              │                │
 │               │<──201 Created─│                │              │──Send Email──>│
 │               │   (Ticket)    │                │              │   & SMS       │
 │               │               │                │              │                │
 │<──Display─────│               │                │              │                │
 │   Success     │               │                │              │                │
 │               │               │                │              │                │
```

## 2. Assign Ticket Sequence

```
DevOps Eng    Web UI     API Gateway    Ticket Service    Database    Assignment Service
   │            │              │               │              │                │
   │──View───>│              │               │              │                │
   │  Ticket   │              │               │              │                │
   │            │              │               │              │                │
   │            │──GET /api────>│               │              │                │
   │            │   /tickets/:id│               │              │                │
   │            │              │               │              │                │
   │            │              │──Fetch Ticket─>│              │                │
   │            │              │               │              │                │
   │            │              │               │──SELECT────>│                │
   │            │              │               │              │                │
   │            │              │<──Ticket Data──│<──Result────│                │
   │            │              │               │              │                │
   │            │<──200 OK──────│               │              │                │
   │<──Display──│  (Ticket)    │               │              │                │
   │  Ticket    │              │               │              │                │
   │            │              │               │              │                │
   │──Assign───>│              │               │              │                │
   │  to Self   │              │               │              │                │
   │            │              │               │              │                │
   │            │──PUT /api─────>│               │              │                │
   │            │   /tickets/:id│               │              │                │
   │            │   /assign     │               │              │                │
   │            │              │               │              │                │
   │            │              │──Check──────────────────────────>│                │
   │            │              │   Availability│              │                │
   │            │              │               │              │                │
   │            │              │<──Available────────────────────│                │
   │            │              │               │              │                │
   │            │              │──Update────────>│              │                │
   │            │              │   Assignment  │              │                │
   │            │              │               │              │                │
   │            │              │               │──UPDATE────>│                │
   │            │              │               │              │                │
   │            │              │<──Updated──────│<──Success────│                │
   │            │              │               │              │                │
   │            │<──200 OK──────│               │              │                │
   │<──Confirm──│              │               │              │                │
   │  Assignment│              │               │              │                │
   │            │              │               │              │                │
```

## 3. Update Ticket Status Sequence

```
DevOps Eng    Web UI     API Gateway    Ticket Service    Database    Notification Service    User
   │            │              │               │              │                │              │
   │──Update───>│              │               │              │                │              │
   │  Status    │              │               │              │                │              │
   │            │              │               │              │                │              │
   │            │──PATCH /api──>│               │              │                │              │
   │            │   /tickets/:id│               │              │                │              │
   │            │   /status     │               │              │                │              │
   │            │              │               │              │                │              │
   │            │              │──Validate──────>│              │                │              │
   │            │              │   Transition  │              │                │              │
   │            │              │               │              │                │              │
   │            │              │<──Valid────────│              │                │              │
   │            │              │   Transition  │              │                │              │
   │            │              │               │              │                │              │
   │            │              │──Update────────>│              │                │              │
   │            │              │   Status      │              │                │              │
   │            │              │               │              │                │              │
   │            │              │               │──UPDATE────>│                │              │
   │            │              │               │              │                │              │
   │            │              │               │──INSERT────>│                │              │
   │            │              │               │  (History)  │                │              │
   │            │              │               │              │                │              │
   │            │              │<──Updated──────│<──Success────│                │              │
   │            │              │               │              │                │              │
   │            │              │──Publish Event───────────────────>│              │
   │            │              │   (Status Changed)               │              │
   │            │              │               │              │                │              │
   │            │<──200 OK──────│               │              │──Notify────────────────>│
   │            │              │               │              │   Requestor    │              │
   │<──Confirm──│              │               │              │                │              │
   │  Update    │              │               │              │                │              │
   │            │              │               │              │                │              │
```

## 4. Escalation Sequence

```
System       SLA Monitor   Ticket Service   Escalation Service   Notification Service   Manager
  │               │               │                  │                    │                │
  │──Cron Job────>│               │                  │                    │                │
  │  (Every 5min) │               │                  │                    │                │
  │               │               │                  │                    │                │
  │               │──Check SLA────>│                  │                    │                │
  │               │  Breaches     │                  │                    │                │
  │               │               │                  │                    │                │
  │               │               │──Query Overdue──>│                    │                │
  │               │               │   Tickets        │                    │                │
  │               │               │                  │                    │                │
  │               │<──SLA Breach──│<──Breach List────│                    │                │
  │               │   Detected    │                  │                    │                │
  │               │               │                  │                    │                │
  │               │──Trigger──────────────────────────>│                    │                │
  │               │  Escalation   │                  │                    │                │
  │               │               │                  │                    │                │
  │               │               │                  │──Determine────────>│                │
  │               │               │                  │  Escalation Path  │                │
  │               │               │                  │                    │                │
  │               │               │                  │──Send Alert────────────────────────>│
  │               │               │                  │                    │                │
  │               │               │                  │──Update Ticket────>│                │
  │               │               │                  │  (Add Escalation) │                │
  │               │               │                  │                    │                │
  │               │               │<──Escalated──────│<──Updated──────────│                │
  │               │               │                  │                    │                │
```

## 5. Close Ticket Sequence

```
DevOps Eng    Web UI     API Gateway    Ticket Service    Database    Notification Service    User
   │            │              │               │              │                │              │
   │──Mark as──>│              │               │              │                │              │
   │  Resolved  │              │               │              │                │              │
   │            │              │               │              │                │              │
   │            │──PATCH /api──>│               │              │                │              │
   │            │   /tickets/:id│               │              │                │              │
   │            │   /resolve    │               │              │                │              │
   │            │              │               │              │                │              │
   │            │              │──Update────────>│              │                │              │
   │            │              │   to Resolved │              │                │              │
   │            │              │               │              │                │              │
   │            │              │               │──UPDATE────>│                │              │
   │            │              │               │              │                │              │
   │            │              │<──Updated──────│<──Success────│                │              │
   │            │              │               │              │                │              │
   │            │              │──Notify────────────────────────────>│              │
   │            │              │   Requestor   │              │                │              │
   │            │              │               │              │                │              │
   │            │<──200 OK──────│               │              │──Send──────────────────>│
   │            │              │               │              │  Verification │              │
   │            │              │               │              │  Request      │              │
   │            │              │               │              │                │              │
   │            │              │               │              │                │──Verify─────>│
   │            │              │               │              │                │  Resolution │
   │            │              │               │              │                │              │
   │            │              │               │              │                │<──Approve────│
   │            │              │               │              │                │              │
   │            │              │<──PATCH /api──────────────────────────────────│              │
   │            │              │   /tickets/:id│              │                │              │
   │            │              │   /close      │              │                │              │
   │            │              │               │              │                │              │
   │            │              │──Close────────>│              │                │              │
   │            │              │   Ticket      │              │                │              │
   │            │              │               │              │                │              │
   │            │              │               │──UPDATE────>│                │              │
   │            │              │               │  (CLOSED)   │                │              │
   │            │              │               │              │                │              │
   │            │              │<──Closed───────│<──Success────│                │              │
   │            │              │               │              │                │              │
```

## Key Interactions

1. **Synchronous Operations**: User actions, CRUD operations, validations
2. **Asynchronous Operations**: Notifications, SLA monitoring, escalations
3. **Event-Driven**: Status changes trigger notifications and workflow updates
4. **Validation Points**: Request validation, state transition validation, permission checks
5. **Audit Trail**: All state changes recorded in history table
