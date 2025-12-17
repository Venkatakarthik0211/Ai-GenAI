# Documentation Generation Prompt Template

## Purpose
This document provides a comprehensive, reusable prompt template for generating complete technical documentation for software projects. Use this template to create consistent, high-quality documentation across all your projects.

---

## Master Prompt Template

Copy and customize the prompt below by replacing the placeholders with your project-specific details:

---

### PROMPT START

```
# COMPREHENSIVE TECHNICAL DOCUMENTATION REQUEST

## Project Context
**Project Name**: [YOUR_PROJECT_NAME]
**Project Type**: [e.g., MLOps Pipeline, Web Application, Microservices Architecture, Data Platform]
**Technology Stack**:
- **Primary Language**: [e.g., Python 3.11]
- **Frameworks**: [e.g., LangGraph, FastAPI, React, Django]
- **Infrastructure**: [e.g., AWS, Kubernetes, Docker]
- **Database**: [e.g., PostgreSQL, MongoDB, Redis]
- **Key Libraries**: [e.g., scikit-learn, pandas, MLflow]
- **UI Framework**: [e.g., Streamlit, React, Vue.js]

**Core Functionality**:
[Describe in 2-3 sentences what the system does]
Example: "An automated MLOps pipeline that uses LangGraph for orchestration, AWS Bedrock for AI-powered decision-making, and MLflow for experiment tracking. The system handles end-to-end ML workflow from data preprocessing to model deployment with intelligent retraining capabilities."

**Key Features**:
1. [Feature 1 - e.g., Automated hyperparameter tuning with GridSearchCV]
2. [Feature 2 - e.g., AI-powered algorithm selection using AWS Bedrock]
3. [Feature 3 - e.g., Real-time drift detection and performance monitoring]
4. [Feature 4 - e.g., Interactive Streamlit UI for visualization and control]
5. [Feature 5 - e.g., Comprehensive MLflow integration for experiment tracking]

**Architecture Pattern**: [e.g., Event-driven, Microservices, Layered, Graph-based state machine]

---

## DOCUMENTATION REQUIREMENTS

Please create the following comprehensive documentation with the specified structure and level of detail:

---

### 1. HIGH-LEVEL DESIGN (HLD) DOCUMENT

**File Name**: `HLD_[PROJECT_NAME].md`

**Required Sections**:

#### 1.1 Executive Summary
- Purpose and scope
- Key innovations
- System overview (2-3 paragraphs)
- Target audience

#### 1.2 System Overview
- Context diagram showing external systems
- Key stakeholders
- System boundaries

#### 1.3 Design Goals and Principles
- **Design Goals** (G1, G2, G3, etc.):
  - Automation
  - Scalability
  - Reliability
  - Performance
  - Security
  - [Add project-specific goals]

- **Design Principles** (P1, P2, P3, etc.):
  - Modularity
  - State management
  - Fail-safe mechanisms
  - Extensibility
  - [Add project-specific principles]

#### 1.4 System Architecture
- Layered architecture diagram showing:
  - Presentation layer
  - API/Gateway layer
  - Business logic layer
  - Data access layer
  - External services layer
- Communication patterns
- Data flow overview

#### 1.5 Component Design
For each major component:
- **Component Name**
- **Responsibility**: What it does
- **Key Features**: List of capabilities
- **Sub-components**: Break down into smaller pieces
- **Interfaces**: APIs, events, data contracts
- **Dependencies**: What it depends on

Example components to document:
- [Component 1 - e.g., UI Layer with Streamlit]
- [Component 2 - e.g., Orchestration Engine with LangGraph]
- [Component 3 - e.g., AI Decision Layer with agents]
- [Component 4 - e.g., Data Processing Layer]
- [Component 5 - e.g., Integration Layer]

#### 1.6 Data Design
- Data models (TypedDicts, Classes, Database schemas)
- State management approach
- Data flow between components
- Persistence strategy

#### 1.7 Interface Design
- External APIs
- Internal interfaces
- Event schemas
- Message formats

#### 1.8 Security Design
- Authentication & authorization
- Data encryption (transit & rest)
- Secrets management
- Audit logging
- Compliance requirements

#### 1.9 Deployment Architecture
- Container architecture (Docker Compose or Kubernetes)
- Infrastructure components
- Network topology
- Resource allocation
- Scalability approach

#### 1.10 Non-Functional Requirements
Tables for:
- Performance requirements (latency, throughput, etc.)
- Scalability requirements (concurrent users, data volume, etc.)
- Availability requirements (uptime, RTO, RPO)
- Security requirements
- Maintainability requirements
- Compliance requirements

#### 1.11 Technology Stack Details
Detailed breakdown of all technologies with justification

---

### 2. SYSTEM ARCHITECTURE DOCUMENT

**File Name**: `SYSTEM_ARCHITECTURE.md`

**Required Sections**:

#### 2.1 Overview
- System purpose
- Architecture overview diagram
- Design principles recap

#### 2.2 High-Level Architecture Diagram
ASCII art diagram showing:
```
┌─────────────────────────────────────┐
│        Layer 1: UI/Presentation     │
├─────────────────────────────────────┤
│        Layer 2: API Gateway         │
├─────────────────────────────────────┤
│        Layer 3: Business Logic      │
├─────────────────────────────────────┤
│        Layer 4: Data Access         │
├─────────────────────────────────────┤
│        Layer 5: External Services   │
└─────────────────────────────────────┘
```

#### 2.3 Component Breakdown
For each component:
- Detailed responsibility description
- Internal structure
- Key classes/modules
- Configuration options
- Performance characteristics

#### 2.4 Data Flow Architecture
Reference to DATA_FLOW_ARCHITECTURE.md with:
- Stage-by-stage data transformations
- Data structures at each stage
- Logging/tracking points

#### 2.5 Technology Stack
Organized by:
- User Interface
- Backend Framework
- Orchestration
- AI/ML
- Data Processing
- Storage
- Monitoring
- Deployment

#### 2.6 Deployment Architecture
Detailed deployment diagrams with:
- Container/pod specifications
- Resource requirements
- Network configuration
- Service dependencies

#### 2.7 Integration Points
- External service integrations
- API endpoints
- Event subscriptions
- Webhooks

---

### 3. DATA FLOW ARCHITECTURE

**File Name**: `DATA_FLOW_ARCHITECTURE.md`

**Required Sections**:

#### 3.1 Overview
- Purpose of data flow documentation
- Scope

#### 3.2 End-to-End Data Flow Diagram
Large ASCII diagram showing:
```
Input Data
    │
    ▼
Stage 1: [Name]
    │ (transformation details)
    ▼
Stage 2: [Name]
    │
    ▼
[Continue for all stages]
    │
    ▼
Output/Artifacts
```

#### 3.3 Stage-by-Stage Breakdown
For each stage:
```markdown
### Stage N: [Stage Name]

**Input**: [Data structure/format]
**Output**: [Data structure/format]

**Processing**:
- Step 1: [Description]
- Step 2: [Description]
- Step N: [Description]

**Data Structure**:
```python
{
    "field1": value,
    "field2": value,
    ...
}
```

**Logging/Tracking**:
- Parameters logged
- Metrics logged
- Artifacts saved

**Example**:
[Show concrete example with sample data]
```

#### 3.4 Data Transformations
- Input → Output mappings
- Data quality checks
- Validation rules

#### 3.5 Decision Points
For AI/conditional logic:
```
INPUT DATA PACKAGE:
{
  "context": {...}
}
    │
    ▼
[DECISION LOGIC/AGENT]
    │
    ▼
OUTPUT DATA PACKAGE:
{
  "decision": {...}
}
```

---

### 4. SEQUENCE DIAGRAMS

**File Name**: `SEQUENCE_DIAGRAMS.md`

**Required Sections**:

#### 4.1 Complete System Flow Sequence
End-to-end sequence showing all actors:
```
User    UI    API    Component1    Component2    Database
 │       │      │          │             │            │
 │       │      │          │             │            │
```

#### 4.2 Key Workflow Sequences
Create sequence diagrams for:
- Main user workflow
- Background processing workflow
- Error handling workflow
- Integration workflows (at least 3-5)

For each sequence:
- All participating components
- Message/method calls
- Data passed
- Return values
- Error paths

#### 4.3 API Interaction Sequences
- External API calls
- Retry logic
- Rate limiting
- Authentication flow

#### 4.4 Data Processing Sequences
- Step-by-step processing flow
- Parallel processing paths
- Aggregation points

---

### 5. UML DIAGRAMS

**File Name**: `UML_DIAGRAMS.md`

**Required Sections**:

#### 5.1 Component Diagram
High-level component view showing:
- All major components as boxes
- Dependencies as arrows
- Interfaces as lollipops
- Provided/required interfaces

#### 5.2 Class Diagrams
Organized by module/package:

**5.2.1 Core Classes**
```
┌─────────────────────────────┐
│     ClassName               │
├─────────────────────────────┤
│ - private_field: type       │
│ + public_field: type        │
├─────────────────────────────┤
│ + public_method(): return   │
│ # protected_method(): return│
│ - private_method(): return  │
└─────────────────────────────┘
```

Include:
- State/Data classes
- Orchestrator/Controller classes
- Service classes
- Repository/DAO classes
- Utility classes

**5.2.2 Relationships**
- Inheritance (△ arrow)
- Composition (◆ arrow)
- Aggregation (◇ arrow)
- Association (→ arrow)
- Dependency (- - →)

#### 5.3 State Machine Diagrams
For stateful components:
```
    ┌─────────┐
    │  STATE1 │
    └────┬────┘
         │ event1
         ▼
    ┌─────────┐
    │  STATE2 │
    └─────────┘
```

#### 5.4 Deployment Diagram
Physical/logical deployment view:
- Nodes (servers, containers)
- Artifacts deployed on each node
- Communication paths
- Protocols used

---

### 6. FLOW DIAGRAMS (1LD, 2LD, 3LD)

**File Name**: `FLOW_DIAGRAMS.md`

**Required Structure**:

#### 6.1 LEVEL 1 DESIGN (1LD) - High-Level Overview
**Audience**: Executives, Product Managers, Non-technical stakeholders

**Content**:
- 5-7 major functional blocks
- High-level flow between blocks
- Key decision points
- Start and end points

**Format**:
```
╔═══════════╗
║  PHASE 1  ║
║  [Name]   ║
╚═════╦═════╝
      ║
      ▼
╔═══════════╗
║  PHASE 2  ║
╚═══════════╝
```

**Include**:
- User interaction flow (simplified)
- System response flow
- Key stakeholders view

#### 6.2 LEVEL 2 DESIGN (2LD) - Detailed Component Interactions
**Audience**: Architects, Senior Engineers, Technical Leads

**Content**:
- 20-30 components/modules
- Component interactions
- Data flow between components
- Integration points
- Conditional flows

**Format**:
```
┌────────────────────────────────┐
│  PHASE 1: [Name]               │
│                                │
│  ┌──────────────┐              │
│  │ Component A  │──────────┐   │
│  └──────┬───────┘          │   │
│         │                  ▼   │
│         ▼            ┌──────────┐
│  ┌──────────────┐   │Component│
│  │ Component B  │   │    C    │
│  └──────────────┘   └─────────┘
└────────────────────────────────┘
```

**Include**:
- Data structures passed between components
- API calls
- Database operations
- External service calls

#### 6.3 LEVEL 3 DESIGN (3LD) - Implementation Details
**Audience**: Developers, QA Engineers, Implementation Team

**Content**:
- Code-level logic flow
- Algorithm details
- Function calls with parameters
- Error handling
- Edge cases
- Detailed decision trees

**Format**:
```
class ClassName:
    def method_name(params) -> return_type:
        │
        ├─> 1. VALIDATION
        │   ├─> Check param1
        │   ├─> Check param2
        │   └─> Raise error if invalid
        │
        ├─> 2. PROCESSING
        │   ├─> Step 1: [description]
        │   │   ├─> Sub-step 1a
        │   │   └─> Sub-step 1b
        │   │
        │   ├─> Step 2: [description]
        │   │
        │   └─> Step N: [description]
        │
        ├─> 3. RESULT CONSTRUCTION
        │   └─> return result
        │
        └─> 4. ERROR HANDLING
            └─> try/except logic
```

**Include**:
- Variable assignments
- Loop logic
- Conditional branches
- Function signatures
- Data type conversions

---

### 7. MODULE INTERFACES

**File Name**: `MODULE_INTERFACES.md`

**Required Sections**:

#### 7.1 Interface Definitions
For each module interface:

```markdown
### Module: [ModuleName]

**Public Interface**:

#### Function/Method: `function_name`
```python
def function_name(
    param1: Type1,
    param2: Type2,
    optional_param: Type3 = default
) -> ReturnType:
    """
    Brief description.

    Args:
        param1: Description of param1
        param2: Description of param2
        optional_param: Description of optional param

    Returns:
        Description of return value

    Raises:
        ExceptionType: When this happens

    Example:
        >>> result = function_name(val1, val2)
        >>> print(result)
        expected_output
    """
```

**Input Contract**:
- Required fields
- Optional fields
- Validation rules
- Default values

**Output Contract**:
- Return type structure
- Success response format
- Error response format

**Side Effects**:
- Database changes
- File I/O
- External API calls
- State modifications
```

#### 7.2 Data Contracts
Define all data transfer objects:

```python
@dataclass
class DataContractName:
    """Description"""
    field1: Type1
    field2: Type2
    optional_field: Optional[Type3] = None

    def validate(self) -> bool:
        """Validation logic"""
```

#### 7.3 Event/Message Schemas
For event-driven systems:

```json
{
  "event_type": "EventName",
  "version": "1.0",
  "timestamp": "ISO8601",
  "payload": {
    "field1": "type",
    "field2": "type"
  }
}
```

---

### 8. ERROR HANDLING STRATEGY

**File Name**: `ERROR_HANDLING_STRATEGY.md`

**Required Sections**:

#### 8.1 Error Categories
Define error types:
- User errors (4xx)
- System errors (5xx)
- External service errors
- Data errors

#### 8.2 Exception Hierarchy
```
BaseException
├── UserError
│   ├── ValidationError
│   └── AuthenticationError
├── SystemError
│   ├── ConfigurationError
│   └── ResourceError
└── ExternalServiceError
    ├── APIError
    └── TimeoutError
```

#### 8.3 Error Handling Patterns
For each pattern:
- Try/except blocks
- Retry logic
- Fallback mechanisms
- Circuit breakers
- Dead letter queues

#### 8.4 Logging Strategy
- Error logging levels
- Log format
- Context information
- Correlation IDs

---

### 9. PROJECT STRUCTURE

**File Name**: `PROJECT_STRUCTURE.md`

**Required Content**:

#### 9.1 Directory Tree
```
project_root/
├── src/
│   ├── [module1]/
│   │   ├── __init__.py
│   │   ├── [component].py
│   │   └── tests/
│   ├── [module2]/
│   └── [moduleN]/
├── docs/
│   ├── HLD.md
│   ├── SEQUENCE_DIAGRAMS.md
│   └── [other docs]
├── config/
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

#### 9.2 Module Descriptions
For each module/directory:
- Purpose
- Key files
- Dependencies
- Testing strategy

#### 9.3 Configuration Files
- Location
- Format
- Required fields
- Environment-specific configs

---

## FORMATTING REQUIREMENTS

### 1. Use ASCII Art for Diagrams
- Boxes: `┌─┐ └─┘ ├─┤ │`
- Arrows: `→ ↓ ← ↑ ▼ ▲`
- Bold boxes: `╔═╗ ╚═╝ ║ ═`
- Clear, readable layouts

### 2. Code Blocks
- Use triple backticks with language identifier
- Include syntax highlighting
- Provide complete, runnable examples where possible

### 3. Tables
Use markdown tables for:
- Non-functional requirements
- Comparison matrices
- Configuration options
- API endpoints

### 4. Consistent Structure
- Use numbered sections
- Consistent heading levels
- Table of contents for long documents
- Cross-references between documents

### 5. Examples
Include concrete examples for:
- Data structures
- API calls
- Configuration
- Usage scenarios

---

## LEVEL OF DETAIL GUIDELINES

### High-Level Design (HLD)
- **Depth**: Architectural decisions and rationale
- **Audience**: Architects, stakeholders
- **Focus**: "What" and "Why"
- **Length**: 50-100 pages equivalent

### System Architecture
- **Depth**: Component relationships and interactions
- **Audience**: Senior engineers, tech leads
- **Focus**: "How" components work together
- **Length**: 30-50 pages

### Flow Diagrams
- **1LD**: 1-2 pages (high-level overview)
- **2LD**: 5-10 pages (component interactions)
- **3LD**: 20-30 pages (implementation details)

### Sequence Diagrams
- **Depth**: Message-level interactions
- **Audience**: Developers
- **Focus**: Temporal ordering of operations
- **Length**: 10-20 key sequences

### UML Diagrams
- **Depth**: Class-level design
- **Audience**: Developers
- **Focus**: Code structure and relationships
- **Length**: Complete class hierarchy

---

## OUTPUT FORMAT

Please generate all documents as markdown files with:
1. Clear, descriptive filenames
2. Proper markdown formatting
3. ASCII art diagrams
4. Code examples with syntax highlighting
5. Table of contents for documents > 5 pages
6. Cross-references using relative links
7. Version information and date

---

## QUALITY CHECKLIST

Before considering the documentation complete, verify:

- [ ] All major components are documented
- [ ] Data flow is clear at all levels (1LD, 2LD, 3LD)
- [ ] Sequence diagrams cover main workflows
- [ ] UML class diagrams include all core classes
- [ ] Error handling is documented
- [ ] Security considerations are addressed
- [ ] Deployment architecture is complete
- [ ] Non-functional requirements are specified
- [ ] Examples are provided for complex concepts
- [ ] All diagrams are readable and consistent
- [ ] Cross-references are accurate
- [ ] Technology stack is fully documented
- [ ] Integration points are clear

---

## CUSTOMIZATION NOTES

### For Different Project Types:

**Web Application**:
- Add: API documentation section
- Add: Frontend component hierarchy
- Add: State management flow

**Data Pipeline**:
- Add: Data quality checks section
- Add: Transformation logic details
- Add: Data lineage diagrams

**Microservices**:
- Add: Service mesh diagram
- Add: Inter-service communication patterns
- Add: Service discovery mechanism

**ML/AI System**:
- Add: Model training flow
- Add: Inference pipeline
- Add: Experiment tracking
- Add: Model monitoring

---

## EXAMPLE USAGE

When using this template, replace all placeholders:

```
[YOUR_PROJECT_NAME] → "E-commerce Recommendation Engine"
[e.g., Python 3.11] → "Python 3.11"
[Component 1] → "Product Catalog Service"
```

Then feed the customized prompt to your documentation generation process (AI assistant, documentation tool, or manual creation).

---

## MAINTENANCE

This template should be:
- **Updated**: When new best practices emerge
- **Versioned**: Track changes over time
- **Customized**: Per project needs
- **Reviewed**: Regularly for completeness

---

**Template Version**: 1.0
**Last Updated**: 2025-11-30
**Maintained By**: [Your Team/Organization]

```

---

## QUICK START GUIDE FOR USING THIS TEMPLATE

### Step 1: Gather Project Information
Before using the template, collect:
- Technology stack details
- Architecture decisions
- Key components list
- External dependencies
- Non-functional requirements

### Step 2: Customize the Template
1. Copy the "PROMPT START" section
2. Replace all `[PLACEHOLDERS]` with your project specifics
3. Remove sections not applicable to your project
4. Add project-specific sections if needed

### Step 3: Generate Documentation
1. Use the customized prompt with your documentation tool
2. Review generated output for accuracy
3. Fill in any gaps with project-specific details
4. Have technical leads review

### Step 4: Maintain Documentation
1. Update when architecture changes
2. Version control all documentation
3. Keep in sync with codebase
4. Regular review cycles (quarterly recommended)

---

## EXAMPLE: MLOps Pipeline (What We Just Created)

Here's how we used this template for your MLOps project:

**Customizations Made**:
- Project Name: "MLOps Pipeline Automation"
- Tech Stack: LangGraph, AWS Bedrock, MLflow, Streamlit, Python
- Added: AI Agent sections (3 decision agents)
- Added: Model training with GridSearchCV
- Added: Drift detection details
- Added: Monitoring and retraining logic

**Documents Generated**:
1. ✅ HLD_MLOPS_AUTOMATION.md
2. ✅ SYSTEM_ARCHITECTURE.md (updated with Streamlit UI)
3. ✅ DATA_FLOW_ARCHITECTURE.md (existing)
4. ✅ SEQUENCE_DIAGRAMS.md
5. ✅ UML_DIAGRAMS.md
6. ✅ FLOW_DIAGRAMS.md (1LD, 2LD, 3LD)

**Time Saved**: Using this template approach, consistent documentation was generated in minutes rather than days of manual writing.

---

## TIPS FOR BEST RESULTS

1. **Be Specific**: The more detailed your customization, the better the output
2. **Iterate**: Generate → Review → Refine → Regenerate
3. **Use Examples**: Provide sample data structures and flows
4. **Cross-Reference**: Link related sections across documents
5. **Visual First**: Start with diagrams, then add text explanations
6. **Keep Updated**: Documentation is living; update with code changes
7. **Peer Review**: Have team members validate technical accuracy
8. **Accessibility**: Ensure diagrams are readable in plain text/markdown viewers

---

**End of Documentation Prompt Template**
