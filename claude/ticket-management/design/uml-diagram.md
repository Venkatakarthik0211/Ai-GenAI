# UML Diagram - Ticket Management System

## Overview
This document describes the UML class diagrams and entity relationships for the ticket management system.

## Class Diagram

### Core Entities

```
┌─────────────────────────────────┐
│          Ticket                 │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - ticketNumber: String          │
│ - title: String                 │
│ - description: String           │
│ - category: TicketCategory      │
│ - priority: Priority            │
│ - status: TicketStatus          │
│ - requestorId: UUID             │
│ - assigneeId: UUID              │
│ - createdAt: DateTime           │
│ - updatedAt: DateTime           │
│ - resolvedAt: DateTime          │
│ - closedAt: DateTime            │
│ - dueDate: DateTime             │
│ - tags: String[]                │
├─────────────────────────────────┤
│ + create()                      │
│ + assign(userId: UUID)          │
│ + updateStatus(status)          │
│ + escalate(reason)              │
│ + resolve(resolution)           │
│ + close()                       │
│ + reopen(reason)                │
│ + addComment(comment)           │
│ + getHistory()                  │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│            User                 │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - username: String              │
│ - email: String                 │
│ - firstName: String             │
│ - lastName: String              │
│ - role: UserRole                │
│ - department: String            │
│ - phoneNumber: String           │
│ - isActive: Boolean             │
│ - createdAt: DateTime           │
│ - lastLogin: DateTime           │
├─────────────────────────────────┤
│ + authenticate(password)        │
│ + createTicket(ticketData)      │
│ + assignTicket(ticketId)        │
│ + updateProfile()               │
│ + getAssignedTickets()          │
│ + getCreatedTickets()           │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│          Comment                │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - ticketId: UUID                │
│ - userId: UUID                  │
│ - content: String               │
│ - isInternal: Boolean           │
│ - createdAt: DateTime           │
│ - updatedAt: DateTime           │
│ - attachments: Attachment[]     │
├─────────────────────────────────┤
│ + create()                      │
│ + update(content)               │
│ + delete()                      │
│ + addAttachment(file)           │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│        Attachment               │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - fileName: String              │
│ - fileType: String              │
│ - fileSize: Integer             │
│ - filePath: String              │
│ - uploadedBy: UUID              │
│ - uploadedAt: DateTime          │
│ - commentId: UUID               │
│ - ticketId: UUID                │
├─────────────────────────────────┤
│ + upload(file)                  │
│ + download()                    │
│ + delete()                      │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│       TicketHistory             │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - ticketId: UUID                │
│ - userId: UUID                  │
│ - action: String                │
│ - fieldChanged: String          │
│ - oldValue: String              │
│ - newValue: String              │
│ - timestamp: DateTime           │
├─────────────────────────────────┤
│ + log(action, changes)          │
│ + getTimeline(ticketId)         │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│        Notification             │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - userId: UUID                  │
│ - ticketId: UUID                │
│ - type: NotificationType        │
│ - channel: Channel              │
│ - message: String               │
│ - status: DeliveryStatus        │
│ - sentAt: DateTime              │
│ - readAt: DateTime              │
├─────────────────────────────────┤
│ + send()                        │
│ + markAsRead()                  │
│ + retry()                       │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│       SLAPolicy                 │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - name: String                  │
│ - priority: Priority            │
│ - category: TicketCategory      │
│ - responseTime: Integer (mins)  │
│ - resolutionTime: Integer (hrs) │
│ - escalationThreshold: Integer  │
│ - isActive: Boolean             │
├─────────────────────────────────┤
│ + apply(ticket)                 │
│ + checkBreach(ticket)           │
│ + calculateDueDate(ticket)      │
└─────────────────────────────────┘
```

```
┌─────────────────────────────────┐
│        Escalation               │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - ticketId: UUID                │
│ - fromUserId: UUID              │
│ - toUserId: UUID                │
│ - reason: String                │
│ - escalatedAt: DateTime         │
│ - acknowledgedAt: DateTime      │
│ - level: Integer                │
├─────────────────────────────────┤
│ + create(ticket, reason)        │
│ + acknowledge()                 │
│ + getEscalationPath()           │
└─────────────────────────────────┘
```

## Enumerations

```
┌─────────────────────┐
│  TicketCategory     │
├─────────────────────┤
│ VM_ISSUE            │
│ NETWORK_ISSUE       │
│ STORAGE_ISSUE       │
│ DATABASE_ISSUE      │
│ SECURITY_ISSUE      │
│ ACCESS_REQUEST      │
│ INFRASTRUCTURE      │
│ MONITORING_ALERT    │
│ OTHER               │
└─────────────────────┘

┌─────────────────────┐
│     Priority        │
├─────────────────────┤
│ P1_CRITICAL         │
│ P2_HIGH             │
│ P3_MEDIUM           │
│ P4_LOW              │
└─────────────────────┘

┌─────────────────────┐
│   TicketStatus      │
├─────────────────────┤
│ NEW                 │
│ OPEN                │
│ IN_PROGRESS         │
│ PENDING_INFO        │
│ RESOLVED            │
│ CLOSED              │
│ REOPENED            │
│ ESCALATED           │
└─────────────────────┘

┌─────────────────────┐
│     UserRole        │
├─────────────────────┤
│ ADMIN               │
│ DEVOPS_ENGINEER     │
│ SENIOR_ENGINEER     │
│ TEAM_LEAD           │
│ END_USER            │
│ MANAGER             │
└─────────────────────┘

┌─────────────────────┐
│ NotificationType    │
├─────────────────────┤
│ TICKET_CREATED      │
│ TICKET_ASSIGNED     │
│ STATUS_CHANGED      │
│ COMMENT_ADDED       │
│ ESCALATED           │
│ SLA_BREACH          │
│ RESOLUTION_REQUEST  │
└─────────────────────┘

┌─────────────────────┐
│      Channel        │
├─────────────────────┤
│ EMAIL               │
│ SMS                 │
│ IN_APP              │
│ SLACK               │
└─────────────────────┘
```

## Relationships

```
User (1) ──creates──> (*) Ticket
            "requestor"

User (1) ──assigned to──> (*) Ticket
            "assignee"

Ticket (1) ──has──> (*) Comment
            "comments"

Ticket (1) ──has──> (*) Attachment
            "attachments"

Ticket (1) ──has──> (*) TicketHistory
            "history"

User (1) ──writes──> (*) Comment
            "author"

Comment (1) ──has──> (*) Attachment
            "attachments"

Ticket (1) ──has──> (*) Notification
            "notifications"

User (1) ──receives──> (*) Notification
            "recipient"

SLAPolicy (1) ──applies to──> (*) Ticket
            "sla"

Ticket (1) ──has──> (*) Escalation
            "escalations"

User (1) ──escalates to──> (*) User
            "escalation path"
```

## Detailed Relationship Diagram

```
┌───────────┐
│   User    │
└─────┬─────┘
      │
      │ creates (1:*)
      │
      ▼
┌───────────┐        has (1:*)      ┌──────────────┐
│  Ticket   │─────────────────────> │   Comment    │
└─────┬─────┘                       └──────┬───────┘
      │                                    │
      │ has (1:*)                          │ has (1:*)
      │                                    │
      ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│TicketHistory │                    │ Attachment   │
└──────────────┘                    └──────────────┘
      │                                    ▲
      │                                    │
      └────────────────────────────────────┘
                                     has (1:*)

┌───────────┐         applies to      ┌───────────┐
│SLAPolicy  │────────────────────────>│  Ticket   │
└───────────┘         (1:*)           └─────┬─────┘
                                            │
                                            │ has (1:*)
                                            │
                                            ▼
                                      ┌──────────────┐
                                      │ Escalation   │
                                      └──────────────┘
                                            │
                                            │ involves (2:1)
                                            │
                                            ▼
                                      ┌──────────────┐
                                      │    User      │
                                      └──────────────┘
```

## Use Case Diagram

```
                    ┌────────────────────────────────────┐
                    │  Ticket Management System          │
                    │                                    │
┌──────────┐        │  ┌──────────────────────────┐    │
│          │        │  │  Create Ticket           │    │
│ End User │───────────┤                          │    │
│          │        │  └──────────────────────────┘    │
└──────────┘        │                                    │
                    │  ┌──────────────────────────┐    │
                    │  │  View Ticket Status      │    │
                    │  └──────────────────────────┘    │
                    │                                    │
                    │  ┌──────────────────────────┐    │
┌──────────┐        │  │  Assign Ticket           │    │
│          │        │  └──────────────────────────┘    │
│ DevOps   │───────────                                │
│ Engineer │        │  ┌──────────────────────────┐    │
│          │        │  │  Update Status           │    │
└──────────┘        │  └──────────────────────────┘    │
                    │                                    │
                    │  ┌──────────────────────────┐    │
                    │  │  Add Comments            │    │
                    │  └──────────────────────────┘    │
                    │                                    │
┌──────────┐        │  ┌──────────────────────────┐    │
│          │        │  │  Escalate Ticket         │    │
│  Manager │───────────                                │
│          │        │  └──────────────────────────┘    │
└──────────┘        │                                    │
                    │  ┌──────────────────────────┐    │
                    │  │  Generate Reports        │    │
                    │  └──────────────────────────┘    │
┌──────────┐        │                                    │
│          │        │  ┌──────────────────────────┐    │
│ System   │───────────  Monitor SLA              │    │
│          │        │  └──────────────────────────┘    │
└──────────┘        │                                    │
                    │  ┌──────────────────────────┐    │
                    │  │  Send Notifications      │    │
                    │  └──────────────────────────┘    │
                    └────────────────────────────────────┘
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Web UI     │  │  Mobile App  │  │  REST API    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                    API Gateway                                │
│                            │                                  │
│  ┌─────────────────────────┼─────────────────────────────┐  │
│  │          Authentication & Authorization                │  │
│  └─────────────────────────┼─────────────────────────────┘  │
└────────────────────────────┼─────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          │                                     │
┌─────────┼─────────────────────┐ ┌─────────────┼──────────────┐
│  Business Logic Layer         │ │   Service Layer            │
│                               │ │                            │
│  ┌────────────────────┐      │ │  ┌──────────────────┐     │
│  │ Ticket Service     │      │ │  │ Notification     │     │
│  └────────────────────┘      │ │  │ Service          │     │
│                               │ │  └──────────────────┘     │
│  ┌────────────────────┐      │ │                            │
│  │ User Service       │      │ │  ┌──────────────────┐     │
│  └────────────────────┘      │ │  │ SLA Monitor      │     │
│                               │ │  └──────────────────┘     │
│  ┌────────────────────┐      │ │                            │
│  │ Assignment Service │      │ │  ┌──────────────────┐     │
│  └────────────────────┘      │ │  │ Escalation       │     │
│                               │ │  │ Service          │     │
└───────────┬───────────────────┘ │  └──────────────────┘     │
            │                     └─────────────┬──────────────┘
            │                                   │
            └───────────────────┬───────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────┐
│                      Data Access Layer                       │
│  ┌──────────────┐  ┌──────────┴─────┐  ┌──────────────┐   │
│  │ Repositories │  │  ORM/Query     │  │  Cache       │   │
│  └──────────────┘  └────────────────┘  └──────────────┘   │
└───────────────────────────────┼─────────────────────────────┘
                                │
┌───────────────────────────────┼─────────────────────────────┐
│                        Database Layer                        │
│  ┌──────────────┐  ┌──────────┴─────┐  ┌──────────────┐   │
│  │ PostgreSQL   │  │  Redis Cache   │  │  File Store  │   │
│  └──────────────┘  └────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

1. **Repository Pattern**: Data access abstraction
2. **Service Layer Pattern**: Business logic encapsulation
3. **Observer Pattern**: Event-driven notifications
4. **Strategy Pattern**: SLA policy application
5. **Factory Pattern**: Ticket creation with different types
6. **Chain of Responsibility**: Escalation handling
