# Flow Diagram - Ticket Management System

## Overview
This document describes the workflow and flow diagrams for the DevOps ticket management system.

## Main Ticket Flow

```
┌─────────────────┐
│  User Submits   │
│  Request/Issue  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Ticket  │
│  (Auto-assign   │
│   Ticket ID)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ticket Triage  │
│  (Priority &    │
│   Category)     │
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │ Routing │
    └────┬────┘
         │
    ┌────┴────────────────┬──────────────────┬─────────────────┐
    ▼                     ▼                  ▼                 ▼
┌─────────┐         ┌─────────┐       ┌──────────┐     ┌──────────┐
│   VM    │         │ Network │       │ Storage  │     │  Other   │
│ Issues  │         │ Issues  │       │ Issues   │     │ Issues   │
└────┬────┘         └────┬────┘       └────┬─────┘     └────┬─────┘
     │                   │                  │                │
     └───────────────────┴──────────────────┴────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Assign to DevOps │
                    │    Engineer      │
                    └─────────┬────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Investigation   │
                    │  & Resolution    │
                    └─────────┬────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            ┌──────────────┐    ┌──────────────┐
            │   Resolved   │    │   Escalate   │
            └──────┬───────┘    └──────┬───────┘
                   │                   │
                   │                   ▼
                   │         ┌──────────────────┐
                   │         │ Senior Engineer/ │
                   │         │  Team Lead       │
                   │         └──────┬───────────┘
                   │                │
                   │                ▼
                   │         ┌──────────────┐
                   │         │   Resolved   │
                   │         └──────┬───────┘
                   │                │
                   └────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Verification by │
                   │   Requestor     │
                   └────────┬────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
            ┌──────────┐      ┌──────────┐
            │  Closed  │      │ Reopen   │
            └──────────┘      └─────┬────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │ Back to Engineer │
                          └──────────────────┘
```

## Notification Flow

```
┌─────────────────┐
│  Ticket Event   │
│   (Create,      │
│  Update, etc)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Notification   │
│    Service      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Email │ │  SMS  │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         ▼
   ┌──────────┐
   │   User   │
   └──────────┘
```

## Emergency Ticket Flow

```
┌──────────────────┐
│ Critical/P1      │
│ Incident         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Auto-escalate to │
│ On-call Engineer │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Immediate        │
│ Notification     │
│ (SMS + Email)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Acknowledge      │
│ within 15 min    │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────────┐
│  Ack    │ │  No Ack?     │
└────┬────┘ │  Escalate to │
     │      │  Manager     │
     │      └──────────────┘
     │
     ▼
┌──────────────────┐
│ Begin Resolution │
└──────────────────┘
```

## Key Decision Points

1. **Priority Assignment**: Automatic or manual based on keywords and impact
2. **Routing Logic**: Based on ticket category and current team workload
3. **Escalation Trigger**: SLA breach, engineer request, or complexity
4. **Verification**: Required before closing to ensure quality
5. **Reopen Logic**: If verification fails or issue resurfaces
