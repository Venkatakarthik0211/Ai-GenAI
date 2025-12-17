# State Diagram - Ticket Management System

## Overview
This document describes the state transitions and lifecycle of tickets in the ticket management system.

## Ticket State Diagram

```
                              ┌─────────┐
                              │   NEW   │
                              └────┬────┘
                                   │
                                   │ [Auto-assign or Manual Review]
                                   │
                                   ▼
                              ┌─────────┐
                         ┌────│  OPEN   │────┐
                         │    └────┬────┘    │
                         │         │         │
                         │         │         │
            [Cancel]     │         │ [Accept & Start Work]
                         │         │         │
                         │         ▼         │
                         │    ┌─────────────┐│
                         │    │ IN_PROGRESS ││
                         │    └──────┬──────┘│
                         │           │       │
                         │           │       │
                         │  [Need More Info] │
                         │           │       │
                         │           ▼       │
                         │    ┌──────────────┐
                         │    │ PENDING_INFO │
                         │    └──────┬───────┘
                         │           │
                         │           │ [Info Provided]
                         │           │
                         │           └───────┐
                         │                   │
                         ▼                   ▼
                    ┌─────────┐       ┌─────────────┐
                    │ CLOSED  │       │ IN_PROGRESS │
                    │(Cancelled)│     └──────┬──────┘
                    └─────────┘              │
                                             │
                                             │ [Fix Applied]
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │  RESOLVED   │
                                      └──────┬──────┘
                                             │
                                   ┌─────────┴─────────┐
                                   │                   │
                        [Verified OK]        [Not Fixed/Issue Persists]
                                   │                   │
                                   ▼                   ▼
                              ┌─────────┐       ┌─────────────┐
                              │ CLOSED  │       │  REOPENED   │
                              └────┬────┘       └──────┬──────┘
                                   │                   │
                                   │                   │
                                   │                   └──────────┐
                                   │                              │
                                   │            [Reassign & Investigate]
                                   │                              │
                                   │                              ▼
                                   │                       ┌─────────────┐
                                   │                       │ IN_PROGRESS │
                                   │                       └─────────────┘
                                   │
                                   │ [Issue Resurfaces after closure]
                                   │
                                   └──────────────────────────────┐
                                                                  │
                                                                  ▼
                                                          ┌─────────────┐
                                                          │  REOPENED   │
                                                          └─────────────┘
```

## Escalation State Overlay

```
                    ┌──────────────────────────┐
                    │     NORMAL STATE         │
                    │  (Any non-terminal)      │
                    └───────────┬──────────────┘
                                │
                    [SLA Breach OR Manual Escalation]
                                │
                                ▼
                    ┌──────────────────────────┐
                    │     ESCALATED            │
                    │  (Overlay State)         │
                    └───────────┬──────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            [Acknowledged]          [Not Acknowledged]
                    │                       │
                    │                       │
                    ▼                       ▼
         ┌─────────────────────┐   ┌──────────────────┐
         │  Return to Work     │   │  Further         │
         │  (Original State)   │   │  Escalation      │
         └─────────────────────┘   └──────────────────┘
```

## Detailed State Descriptions

### 1. NEW
**Description**: Ticket has been created but not yet reviewed or assigned.

**Entry Conditions**:
- User submits a new ticket
- System auto-generates ticket ID

**Valid Transitions**:
- → OPEN (after triage/assignment)
- → CLOSED (if duplicate or invalid)

**Actions on Entry**:
- Generate ticket number
- Apply default priority if not specified
- Send creation notification to requestor
- Add to assignment queue

**Exit Conditions**:
- Ticket assigned to engineer
- Ticket marked as invalid/duplicate

---

### 2. OPEN
**Description**: Ticket has been assigned and is awaiting work to begin.

**Entry Conditions**:
- Ticket assigned to DevOps engineer
- Engineer has not yet started work

**Valid Transitions**:
- → IN_PROGRESS (engineer starts work)
- → PENDING_INFO (need clarification before starting)
- → CLOSED (cancelled or duplicate)
- → ESCALATED (urgent or SLA breach)

**Actions on Entry**:
- Notify assigned engineer
- Start SLA timer
- Update assignment records

**Exit Conditions**:
- Engineer accepts and starts work
- Ticket cancelled
- Need more information

---

### 3. IN_PROGRESS
**Description**: Engineer is actively working on the ticket.

**Entry Conditions**:
- Engineer has accepted the ticket
- Work has commenced

**Valid Transitions**:
- → PENDING_INFO (need requestor input)
- → RESOLVED (issue fixed)
- → ESCALATED (complexity or SLA breach)
- → CLOSED (cancelled by requestor)

**Actions on Entry**:
- Log start time
- Update ticket status
- Notify requestor work has begun

**Exit Conditions**:
- Resolution achieved
- Blocked by external dependency
- Cancellation requested

---

### 4. PENDING_INFO
**Description**: Work is paused waiting for additional information from requestor or third party.

**Entry Conditions**:
- Engineer requires clarification
- Waiting for access/permissions
- Awaiting external input

**Valid Transitions**:
- → IN_PROGRESS (information received)
- → CLOSED (timeout or cancellation)
- → ESCALATED (information not provided in time)

**Actions on Entry**:
- Notify requestor of information needed
- Pause SLA timer (optional based on policy)
- Set follow-up reminder

**Exit Conditions**:
- Required information provided
- Timeout period exceeded
- Requestor cancels

---

### 5. RESOLVED
**Description**: Engineer has completed the fix and ticket is awaiting verification.

**Entry Conditions**:
- Engineer has applied fix/solution
- Resolution documented

**Valid Transitions**:
- → CLOSED (requestor verifies fix)
- → REOPENED (fix didn't work or issue persists)
- → IN_PROGRESS (additional work needed)

**Actions on Entry**:
- Log resolution time
- Notify requestor for verification
- Document solution
- Pause SLA timer

**Exit Conditions**:
- Requestor verifies resolution
- Issue resurfaces
- Verification timeout

---

### 6. REOPENED
**Description**: Previously resolved ticket that requires additional work.

**Entry Conditions**:
- Requestor reports issue not resolved
- Issue resurfaces after closure
- Incomplete fix identified

**Valid Transitions**:
- → IN_PROGRESS (engineer re-investigates)
- → ESCALATED (recurring issue)
- → CLOSED (false alarm)

**Actions on Entry**:
- Notify assigned engineer
- Log reopen reason
- Restart SLA timer
- Increment reopen counter

**Exit Conditions**:
- Work restarts
- Issue escalated
- Determined to be different issue

---

### 7. CLOSED
**Description**: Terminal state - ticket lifecycle complete.

**Entry Conditions**:
- Resolution verified by requestor
- Ticket cancelled
- Marked as duplicate
- Invalid ticket

**Valid Transitions**:
- → REOPENED (only if closed < 30 days and issue resurfaces)

**Actions on Entry**:
- Log closure time
- Calculate metrics (resolution time, etc.)
- Archive ticket data
- Send closure notification
- Update performance metrics

**Exit Conditions**:
- Issue resurfaces within reopen window

---

### 8. ESCALATED (Overlay State)
**Description**: Special state that overlays existing state when escalation is needed.

**Entry Conditions**:
- SLA breach detected
- Manual escalation by engineer
- Critical priority ticket
- Multiple reopens

**Valid Transitions**:
- → Original state (after escalation handled)
- → CLOSED (if escalation determines invalid)

**Actions on Entry**:
- Notify manager/senior engineer
- Assign higher priority resources
- Update escalation level
- Send urgent notifications

**Exit Conditions**:
- Escalation acknowledged and addressed
- Resolved or closed

---

## State Transition Rules

### Automatic Transitions
1. **NEW → OPEN**: Auto-trigger after assignment
2. **Any → ESCALATED**: SLA breach detection
3. **PENDING_INFO → CLOSED**: After timeout period (configurable)
4. **RESOLVED → CLOSED**: After verification timeout (auto-approve)

### Manual Transitions
1. **OPEN → IN_PROGRESS**: Engineer action
2. **IN_PROGRESS → RESOLVED**: Engineer completes work
3. **RESOLVED → CLOSED**: Requestor verification
4. **RESOLVED → REOPENED**: Requestor reports issue
5. **Any → CLOSED**: Admin/Manager override

### Restricted Transitions
1. **CLOSED → Any state**: Only allow REOPENED within 30 days
2. **Cannot skip**: Must go through proper workflow (e.g., cannot go directly from OPEN to CLOSED without RESOLVED)

## State Metrics

### Per State Tracking
- **Time in State**: Duration ticket remained in each state
- **Entry Count**: Number of times ticket entered each state
- **Exit Reasons**: Why ticket left each state

### Key Performance Indicators
1. **Time to First Response**: NEW → OPEN duration
2. **Time to Resolution**: Created → RESOLVED duration
3. **Time to Closure**: Created → CLOSED duration
4. **Reopen Rate**: Percentage of tickets reopened
5. **Escalation Rate**: Percentage of tickets escalated
6. **SLA Compliance**: Percentage meeting SLA by state

## Business Rules by State

### Priority-based Rules
- **P1 (Critical)**: Cannot stay in NEW > 5 minutes
- **P2 (High)**: Cannot stay in NEW > 30 minutes
- **P3 (Medium)**: Cannot stay in NEW > 2 hours
- **P4 (Low)**: Cannot stay in NEW > 1 day

### SLA-based State Rules
- **IN_PROGRESS**: Must have update every 4 hours for P1/P2
- **PENDING_INFO**: Auto-close after 7 days no response
- **RESOLVED**: Auto-close after 3 days no feedback
- **REOPENED**: Auto-escalate after 2nd reopen

### Permission Rules by State
- **NEW**: Any authenticated user can create
- **OPEN/IN_PROGRESS**: Only assigned engineer can update
- **RESOLVED**: Only assigned engineer can mark resolved
- **CLOSED**: Requestor or engineer can close
- **REOPENED**: Only requestor can reopen (within 30 days)
- **ESCALATED**: Manager+ can escalate/de-escalate

## State Notifications

### Notification Matrix

| State Change | Notify Requestor | Notify Engineer | Notify Manager |
|-------------|------------------|-----------------|----------------|
| NEW → OPEN | Yes | Yes | No |
| OPEN → IN_PROGRESS | Yes | No | No |
| IN_PROGRESS → PENDING_INFO | Yes | No | No |
| PENDING_INFO → IN_PROGRESS | Yes | Yes | No |
| IN_PROGRESS → RESOLVED | Yes | No | No |
| RESOLVED → CLOSED | Yes | Yes | No |
| RESOLVED → REOPENED | Yes | Yes | Yes (P1/P2) |
| Any → ESCALATED | Yes | Yes | Yes |
| ESCALATED → Resolved | Yes | Yes | Yes |

## State Validation

### Entry Validations
- Verify user has permission to transition
- Check required fields are populated
- Validate business rules are met
- Ensure previous state allows transition

### Exit Validations
- Verify work is documented
- Check required comments/notes added
- Validate attachments if required
- Ensure follow-up actions created

## Concurrency Handling

### Optimistic Locking
- Version number on each state change
- Conflict detection on concurrent updates
- Last-write-wins with notification to losers

### State Change Queue
- Queue state changes during high load
- Process in order of submission
- Maintain audit trail of all attempts
