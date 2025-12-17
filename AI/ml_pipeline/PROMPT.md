# Enhanced ML Pipeline - Implementation Guide

## Overview

This document serves as the master implementation guide for the Enhanced ML Pipeline project. It provides instructions for implementing features incrementally while maintaining consistency with the project's design documentation.

---

## Project Structure

**IMPORTANT**: The ml_pipeline project is **self-contained**. All code, configuration, and dependencies are located within the `ml_pipeline/` directory.

### Directory Layout

```
ml_pipeline/
├── agents/                          # AI Decision Agents (AWS Bedrock)
│   ├── algorithm_category_predictor.py    # Agent 1A: Algorithm category prediction
│   ├── preprocessing_question_generator.py # Agent 1B: Dynamic question generation
│   └── base_agent.py                # Base class for all AI agents (in parent ../agents/)
├── api/                             # FastAPI Backend
│   ├── main.py                      # FastAPI application entry point
│   └── routers/
│       └── pipeline.py              # Pipeline execution endpoints
├── core/                            # LangGraph Workflow
│   ├── graph.py                     # Workflow graph construction
│   └── state.py                     # PipelineState TypedDict
├── nodes/                           # LangGraph Nodes
│   ├── preprocessing/
│   │   ├── analyze_prompt.py        # Agent 0: Natural language config extraction
│   │   ├── load_data.py             # Data loading node
│   │   ├── supervised/              # Supervised learning preprocessing (with target)
│   │   │   ├── clean_data.py        # Outlier handling (8 techniques)
│   │   │   ├── handle_missing.py    # Missing value imputation (7 techniques)
│   │   │   ├── encode_features.py   # Categorical encoding (7 techniques, includes target_encoding)
│   │   │   └── scale_features.py    # Feature scaling (7 techniques, optional)
│   │   ├── unsupervised/            # Unsupervised learning preprocessing (no target)
│   │   │   ├── clean_outliers.py    # Data quality validation (PRESERVE outliers!)
│   │   │   ├── handle_missing.py    # Simple imputation only (3 techniques)
│   │   │   ├── encode_features.py   # Label/ordinal encoding (4 techniques, NO target_encoding)
│   │   │   └── scale_features.py    # Feature scaling (4 techniques, MANDATORY!)
│   │   ├── review_config.py         # HITL review orchestration (Agent 1A + 1B)
│   │   └── techniques/              # Preprocessing technique registries
│   ├── feature_engineering/
│   ├── classification/
│   ├── regression/
│   ├── evaluation/
│   └── reporting/
├── database/                        # PostgreSQL Storage
│   ├── pipeline_runs_db.py          # Run state persistence
│   └── review_storage.py            # Human review session storage
├── config/                          # Configuration Files
├── utils/                           # Utility Functions
│   └── bedrock_client.py            # AWS Bedrock client wrapper
├── mlflow_utils/                    # MLflow Utilities
├── tuning/                          # Hyperparameter Tuning
├── monitoring/                      # Model Monitoring
├── retraining/                      # Retraining Logic
├── scripts/                         # Helper Scripts
├── frontend/                        # Vue.js Frontend (Vite)
├── data/                            # Data Storage (mounted volume)
├── outputs/                         # Output Artifacts (mounted volume)
├── mlruns/                          # MLflow Tracking (mounted volume)
├── docker-compose.yml               # Docker Compose Configuration
├── Dockerfile.backend               # Backend Dockerfile
├── Dockerfile.frontend              # Frontend Dockerfile
├── Dockerfile.mlflow                # MLflow Dockerfile
├── requirements.txt                 # Python Dependencies
├── .env                             # Environment Variables
└── PROMPT.md                        # This File
```

### Key Components

#### 1. AI Agents (`agents/`)
- **Agent 0** (`nodes/preprocessing/analyze_prompt.py`): Extracts pipeline configuration from natural language prompts
- **Agent 1A** (`agents/algorithm_category_predictor.py`): Predicts **learning paradigm** (supervised/unsupervised) and optimal algorithm category
  - **Supervised**: linear_models, tree_models, neural_networks, ensemble, time_series
  - **Unsupervised**: clustering, dimensionality_reduction, anomaly_detection
- **Agent 1B** (`agents/preprocessing_question_generator.py`): Generates 4-20 **paradigm-aware** preprocessing questions
  - **Supervised**: Full technique set (target_encoding, complex imputation, optional scaling)
  - **Unsupervised**: Restricted techniques (NO target_encoding, simple imputation, MANDATORY scaling)
- **Base Agent** (from parent `../agents/base_agent.py`): Shared Bedrock client and retry logic

#### 2. LangGraph Workflow (`core/`)
- **graph.py**: Defines the complete workflow with nodes and edges, including:
  - Conditional entry point (analyze_prompt vs load_data)
  - Three-stage HITL review (agent_1a → agent_1b → await_review_approval)
  - **Dual preprocessing paths** based on learning_paradigm:
    - **Supervised Path**: clean_data_supervised → handle_missing_supervised → encode_features_supervised → scale_features_supervised
    - **Unsupervised Path**: clean_outliers_unsupervised → handle_missing_unsupervised → encode_features_unsupervised → scale_features_unsupervised
  - Conditional retry loop (await_review_approval → analyze_prompt if rejected)
  - Second HITL checkpoint (await_preprocessing_review) with paradigm-aware retry routing
- **state.py**: PipelineState TypedDict with 100+ fields for state management (includes learning_paradigm, algorithm_category, etc.)

#### 3. Preprocessing Nodes (`nodes/preprocessing/`)
- **Two separate preprocessing subtrees** based on learning paradigm:
  - **Supervised** (`nodes/preprocessing/supervised/`): Full technique support with target encoding
  - **Unsupervised** (`nodes/preprocessing/unsupervised/`): Restricted techniques to preserve data integrity
- All preprocessing nodes support **technique-based execution**
- Each node has a **technique registry** with multiple implementations
- User selects techniques during HITL review via paradigm-aware questions
- Node executes selected technique from registry with Bedrock-optimized parameters

**Key Differences**:
- **Supervised**: Outliers are noise (remove them), complex imputation OK, target encoding available, scaling optional
- **Unsupervised**: Outliers are meaningful (preserve them), simple imputation only, NO target encoding, scaling MANDATORY

#### 4. Database Storage (`database/`)
- **PostgreSQL with pgvector**: Main database for pipeline runs and review sessions
- **MLflow PostgreSQL Backend**: Tracking metrics, params, artifacts

#### 5. Docker Deployment
- **Context**: Docker build context is set to parent `AI/` directory
- **Dockerfile**: Copies ONLY from `ml_pipeline/` subdirectory
- **No Parent Dependencies**: All parent folders (agents/, utils/, nodes/) were removed to avoid confusion

### Folder Ownership

**Self-Contained Rule**: The `ml_pipeline/` directory contains ALL code needed for the project. No files are shared with parent `AI/` directory except the base agent class.

---

## Core Implementation Principle

**IMPORTANT**: All implementations must be done **incrementally and systematically**, following the principle of **"bits and bits"** (step-by-step development).

### Implementation Workflow

```
User Request → Check Documentation → Plan Implementation → Execute in Steps → Update Documentation → Verify
```

1. **Check Documentation First**: Always refer to the design documents in the `docs/` folder before implementing
2. **Follow Existing Patterns**: If the feature is documented, strictly follow the design specifications
3. **Update Documentation**: If the feature is not documented or requires changes, update ALL related documentation BEFORE implementation
4. **Incremental Development**: Break down large tasks into small, manageable pieces
5. **Verify Against Design**: Ensure each implementation matches the documented architecture

---

## Documentation Reference

All design and architectural decisions are documented in the `/docs` folder. **Always consult these documents before implementing any feature**.

### Core Documentation Files

#### 1. `docs/PROJECT_STRUCTURE.md`
**Purpose**: Complete project structure reference with detailed file descriptions

**When to Use**:
- Adding new files or modules
- Understanding file organization
- Checking where to place new components
- Understanding file responsibilities

**Contains**:
- Complete directory tree structure
- Detailed description of every file (100+ files)
- File purposes, responsibilities, and interactions
- Module organization patterns

#### 2. `docs/DATA_FLOW_ARCHITECTURE.md`
**Purpose**: Stage-by-stage data flow through the ML pipeline

**When to Use**:
- Implementing preprocessing nodes
- Understanding data transformations
- Adding new pipeline stages
- Debugging data flow issues

**Contains**:
- 8 pipeline stages from data loading to artifact saving
- State transitions at each stage
- Data transformations and validations
- MLflow logging points
- AI agent decision integration points

#### 3. `docs/SYSTEM_ARCHITECTURE.md`
**Purpose**: High-level system architecture and component breakdown

**When to Use**:
- Understanding overall system design
- Adding new components
- Understanding component interactions
- Planning integrations

**Contains**:
- Layered architecture (UI, Core, Agents, Storage)
- Component breakdown (10+ major components)
- Technology stack details
- Deployment architecture
- Integration patterns

#### 4. `docs/HLD_MLOPS_AUTOMATION.md`
**Purpose**: Comprehensive High-Level Design document

**When to Use**:
- Understanding design goals and principles
- Planning new features
- Understanding non-functional requirements
- Architecture decisions and trade-offs

**Contains**:
- Executive summary
- System overview and objectives
- Design goals and principles (12 sections)
- Component design with detailed specifications
- Security and deployment considerations
- Performance requirements and NFRs

#### 5. `docs/SEQUENCE_DIAGRAMS.md`
**Purpose**: Temporal interactions between components

**When to Use**:
- Understanding execution flow
- Implementing inter-component communication
- Debugging timing issues
- Planning async operations

**Contains**:
- 6 detailed sequence diagrams:
  1. Complete pipeline execution (end-to-end)
  2. AI agent decision flow with retry logic
  3. Model training with GridSearchCV
  4. Monitoring and retraining flow
  5. MLflow integration flow
  6. User interaction flow

#### 6. `docs/UML_DIAGRAMS.md`
**Purpose**: Class-level design and relationships

**When to Use**:
- Implementing classes and interfaces
- Understanding class relationships
- Planning inheritance hierarchies
- Designing new components

**Contains**:
- Component diagrams (system-wide)
- Class diagrams by module (7 modules)
- Deployment diagrams (Kubernetes)
- State machine diagrams
- Relationship mappings

#### 7. `docs/FLOW_DIAGRAMS.md`
**Purpose**: Multi-level flow diagrams (1LD, 2LD, 3LD)

**When to Use**:
- Understanding workflow at different abstraction levels
- Presenting to stakeholders (1LD)
- Planning architecture (2LD)
- Implementing code (3LD)

**Contains**:
- **Level 1 (1LD)**: High-level overview (5-7 phases) for executives
- **Level 2 (2LD)**: Component interactions (20-30 components) for architects
- **Level 3 (3LD)**: Implementation details with code-level specifics for developers

#### 8. `docs/MODULE_INTERFACES.md` (To be created)
**Purpose**: API contracts between modules

**When to Use**:
- Implementing module interfaces
- Understanding parameter contracts
- Planning API changes

**Contains**:
- Function signatures
- Input/output specifications
- Error handling contracts
- Integration patterns

#### 9. `docs/COMPONENT_SPECIFICATIONS.md` (To be created)
**Purpose**: Detailed specifications for each component

**When to Use**:
- Implementing specific components
- Understanding component requirements
- Planning component enhancements

**Contains**:
- Component responsibilities
- Input/output specifications
- Performance requirements
- Error handling strategies

#### 10. `docs/API_REFERENCE.md` (To be created)
**Purpose**: Complete API documentation

**When to Use**:
- Using existing APIs
- Implementing new endpoints
- Integration with external systems

**Contains**:
- Function/method signatures
- Parameter descriptions
- Return values
- Usage examples
- Error codes

#### 11. `docs/DEPLOYMENT_GUIDE.md` (To be created)
**Purpose**: Step-by-step deployment instructions

**When to Use**:
- Deploying the pipeline
- Setting up infrastructure
- Configuring environments

**Contains**:
- Prerequisites
- Installation steps
- Configuration instructions
- Troubleshooting common issues

#### 12. `docs/TROUBLESHOOTING.md` (To be created)
**Purpose**: Common issues and solutions

**When to Use**:
- Debugging issues
- Understanding error messages
- Finding quick fixes

**Contains**:
- Common error messages
- Root cause analysis
- Step-by-step solutions
- Prevention strategies

---

## Implementation Guidelines

### Step 1: Understand the Request

When receiving an implementation request:

1. **Identify the Feature**: What exactly needs to be implemented?
2. **Determine Scope**: Is it a new feature, enhancement, or bug fix?
3. **Check Complexity**: Can it be broken into smaller tasks?

### Step 2: Consult Documentation

**MANDATORY**: Before writing any code:

1. **Check PROJECT_STRUCTURE.md**:
   - Does the file already exist?
   - Where should the new code be placed?
   - What's the file's intended purpose?

2. **Check DATA_FLOW_ARCHITECTURE.md**:
   - How does this fit into the data flow?
   - What stage does this belong to?
   - What are the inputs and outputs?

3. **Check SYSTEM_ARCHITECTURE.md**:
   - Which component does this belong to?
   - How does it interact with other components?

4. **Check HLD_MLOPS_AUTOMATION.md**:
   - What are the design principles?
   - Are there specific requirements?
   - What are the constraints?

5. **Check SEQUENCE_DIAGRAMS.md**:
   - What's the execution flow?
   - When should this be called?
   - What's the call order?

6. **Check UML_DIAGRAMS.md**:
   - What classes are involved?
   - What's the inheritance structure?
   - What are the relationships?

7. **Check FLOW_DIAGRAMS.md**:
   - What level of detail is needed?
   - How does it fit in the workflow?

### Step 3: Plan Implementation

Create a detailed implementation plan:

1. **List All Files to Modify/Create**:
   ```
   Example:
   - Create: nodes/classification/new_algorithm.py
   - Modify: nodes/classification/__init__.py
   - Modify: core/graph.py (add new node)
   - Modify: tuning/param_grids.py (add parameter grid)
   - Update: docs/PROJECT_STRUCTURE.md (document new file)
   ```

2. **Break Down into Steps**:
   ```
   Example for "Add New Algorithm":
   Step 1: Create algorithm node file with basic structure
   Step 2: Implement parameter grid
   Step 3: Implement training logic
   Step 4: Add MLflow logging
   Step 5: Add to LangGraph workflow
   Step 6: Update configuration
   Step 7: Add unit tests
   Step 8: Update documentation
   ```

3. **Identify Dependencies**:
   - What needs to be done first?
   - What can be done in parallel?
   - What depends on external resources?

### Step 4: Update Documentation (If Needed)

**If the feature is NOT fully documented or requires changes**:

1. **Update ALL Related Documentation**:
   - PROJECT_STRUCTURE.md (if adding/changing files)
   - DATA_FLOW_ARCHITECTURE.md (if changing data flow)
   - SYSTEM_ARCHITECTURE.md (if adding components)
   - HLD_MLOPS_AUTOMATION.md (if changing design)
   - SEQUENCE_DIAGRAMS.md (if changing interactions)
   - UML_DIAGRAMS.md (if adding classes)
   - FLOW_DIAGRAMS.md (if changing workflow)

2. **Get Confirmation**:
   - Present the documentation changes to the user
   - Confirm the approach before implementation
   - Adjust based on feedback

### Step 5: Implement Incrementally

**Follow the "Bits and Bits" Approach**:

#### ✅ DO:
- Implement one file at a time
- Complete one function/method before moving to the next
- Test each piece before moving forward
- Commit frequently with clear messages
- Update imports and dependencies immediately
- Log progress after each step

#### ❌ DON'T:
- Implement multiple unrelated features simultaneously
- Skip validation and testing
- Leave TODOs for "later"
- Ignore documentation updates
- Make assumptions without checking docs

#### Implementation Pattern:

```python
# Example: Adding a new classification algorithm

# STEP 1: Create the node file
# File: nodes/classification/new_algorithm.py
# - Implement basic structure
# - Add imports
# - Define node function signature

# STEP 2: Implement parameter grid
# File: tuning/param_grids.py
# - Add parameter grid for new algorithm
# - Document parameter ranges

# STEP 3: Implement training logic
# File: nodes/classification/new_algorithm.py
# - Implement training with GridSearchCV
# - Add error handling
# - Add state updates

# STEP 4: Add MLflow logging
# File: nodes/classification/new_algorithm.py
# - Log parameters
# - Log metrics
# - Log model artifact

# STEP 5: Update graph
# File: core/graph.py
# - Add node to workflow
# - Add edges
# - Update routing logic

# STEP 6: Update __init__.py
# File: nodes/classification/__init__.py
# - Export new node function

# STEP 7: Add tests
# File: tests/unit/test_algorithm_nodes.py
# - Add unit tests for new algorithm

# STEP 8: Update documentation
# File: docs/PROJECT_STRUCTURE.md
# - Document new file and its purpose
```

### Step 6: Verify Implementation

After each step:

1. **Check Against Documentation**:
   - Does the implementation match the design?
   - Are all requirements met?
   - Are patterns consistent?

2. **Validate Functionality**:
   - Does the code work as expected?
   - Are edge cases handled?
   - Is error handling robust?

3. **Check Integration**:
   - Does it integrate correctly with existing code?
   - Are all imports working?
   - Is the state managed correctly?

4. **Review Code Quality**:
   - Is the code readable?
   - Are there appropriate comments?
   - Does it follow project conventions?

---

## Common Implementation Scenarios

### Scenario 1: Adding a New Algorithm Node

**Documentation to Check**:
- PROJECT_STRUCTURE.md → nodes/classification/ or nodes/regression/
- DATA_FLOW_ARCHITECTURE.md → Stage 5: Model Training
- UML_DIAGRAMS.md → Class diagram for algorithm nodes
- FLOW_DIAGRAMS.md → 3LD implementation details

**Steps**:
1. Create node file in appropriate directory
2. Implement algorithm with GridSearchCV integration
3. Add parameter grid to tuning/param_grids.py
4. Update graph.py to include new node
5. Update __init__.py exports
6. Add unit tests
7. Update PROJECT_STRUCTURE.md

### Scenario 2: Implementing an AI Agent

**Documentation to Check**:
- PROJECT_STRUCTURE.md → agents/
- SYSTEM_ARCHITECTURE.md → Agent component specifications
- SEQUENCE_DIAGRAMS.md → AI agent decision flow
- HLD_MLOPS_AUTOMATION.md → Agent design principles

**Steps**:
1. Create agent class inheriting from BaseDecisionAgent
2. Implement build_prompt() method
3. Implement parse_response() method
4. Implement get_default_decision() method
5. Create prompt template in agents/prompts/
6. Add agent node wrapper function
7. Update graph.py to include agent node
8. Add tests
9. Update documentation

### Scenario 3: Adding a Monitoring Feature

**Documentation to Check**:
- PROJECT_STRUCTURE.md → monitoring/
- DATA_FLOW_ARCHITECTURE.md → Stage 7: Monitoring
- SYSTEM_ARCHITECTURE.md → Monitoring component
- SEQUENCE_DIAGRAMS.md → Monitoring and retraining flow

**Steps**:
1. Implement monitoring class in monitoring/
2. Add monitoring node if needed
3. Integrate with MLflow logging
4. Update alerting.py if alerts needed
5. Add configuration in config/
6. Update graph if adding node
7. Add tests
8. Update documentation

### Scenario 4: Modifying Data Flow

**Documentation to Check** (ALL of these):
- DATA_FLOW_ARCHITECTURE.md → Affected stages
- SEQUENCE_DIAGRAMS.md → Update sequence diagrams
- FLOW_DIAGRAMS.md → Update all 3 levels (1LD, 2LD, 3LD)
- SYSTEM_ARCHITECTURE.md → Component interactions
- HLD_MLOPS_AUTOMATION.md → Data design section

**Steps**:
1. **FIRST**: Update ALL documentation with new data flow
2. Get user confirmation on changes
3. Identify affected nodes
4. Update state schema in core/state.py if needed
5. Modify nodes one by one
6. Update validators if needed
7. Update tests
8. Verify end-to-end

---

## Error Handling Guidelines

When implementing features:

1. **Use Custom Exceptions**: Refer to core/exceptions.py for available exceptions
2. **Add State Errors**: Use add_error() from core/state.py
3. **Implement Retry Logic**: For external calls (Bedrock, MLflow)
4. **Validate Inputs**: Use validators from core/validators.py
5. **Log Failures**: Always log to MLflow and Python logs

---

## Testing Requirements

Every implementation must include:

1. **Unit Tests**: Test individual functions/methods
   - Location: tests/unit/
   - Use pytest fixtures from conftest.py
   - Mock external dependencies

2. **Integration Tests**: Test component interactions
   - Location: tests/integration/
   - Test with real MLflow (test instance)
   - Mock only Bedrock if needed

3. **End-to-End Tests**: Test complete workflows (for major features)
   - Location: tests/e2e/
   - Test full pipeline execution
   - Verify all outputs

---

## MLflow Logging Requirements

All implementations must log to MLflow:

1. **Parameters**: All hyperparameters and configuration
2. **Metrics**: All evaluation metrics
3. **Artifacts**: Models, plots, reports, decisions
4. **Tags**: Component name, version, execution metadata

Use MLflowLogger from mlflow_utils/logger.py for consistency.

---

## Configuration Management

When adding configuration:

1. **Add to config/config.py**: Create/update dataclass
2. **Add to default_config.yaml**: Provide default values
3. **Add to .env.example**: Document environment variable
4. **Update from_env() method**: Load from environment
5. **Document in HLD**: Update configuration section

---

## Documentation Update Checklist

When implementing a feature, update these documents if affected:

- [ ] PROJECT_STRUCTURE.md (if files added/changed)
- [ ] DATA_FLOW_ARCHITECTURE.md (if data flow changed)
- [ ] SYSTEM_ARCHITECTURE.md (if components added/changed)
- [ ] HLD_MLOPS_AUTOMATION.md (if design changed)
- [ ] SEQUENCE_DIAGRAMS.md (if interactions changed)
- [ ] UML_DIAGRAMS.md (if classes added/changed)
- [ ] FLOW_DIAGRAMS.md (if workflow changed)
- [ ] MODULE_INTERFACES.md (if APIs changed)
- [ ] API_REFERENCE.md (if public APIs changed)

---

## Version Control Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance tasks

**Example**:
```
feat(agents): Add algorithm selection agent

Implemented AlgorithmSelectionAgent inheriting from BaseDecisionAgent.
Agent analyzes data characteristics and selects 3-5 optimal algorithms.
Includes retry logic and fallback to default algorithms.

- Created agents/algorithm_selection.py
- Added prompt template
- Updated graph.py to include agent node
- Added unit tests
- Updated PROJECT_STRUCTURE.md

Refs: #123
```

---

## Communication Protocol

When implementing features:

1. **Before Implementation**:
   - Confirm understanding of requirements
   - Present implementation plan
   - Highlight any documentation gaps
   - Ask clarifying questions

2. **During Implementation**:
   - Report progress after each major step
   - Flag any blockers immediately
   - Suggest improvements if found
   - Ask for feedback on approach

3. **After Implementation**:
   - Summarize what was completed
   - List all files created/modified
   - Confirm documentation updates
   - Request testing/review

---

## Quick Reference Checklist

For every implementation task:

- [ ] 1. Read user requirement carefully
- [ ] 2. Check PROJECT_STRUCTURE.md for file locations
- [ ] 3. Check DATA_FLOW_ARCHITECTURE.md for data flow
- [ ] 4. Check SYSTEM_ARCHITECTURE.md for component design
- [ ] 5. Check HLD_MLOPS_AUTOMATION.md for design principles
- [ ] 6. Check SEQUENCE_DIAGRAMS.md for execution flow
- [ ] 7. Check UML_DIAGRAMS.md for class structure
- [ ] 8. Check FLOW_DIAGRAMS.md for workflow
- [ ] 9. Update documentation if needed (get confirmation)
- [ ] 10. Create implementation plan (list files and steps)
- [ ] 11. Implement step-by-step ("bits and bits")
- [ ] 12. Test each piece immediately
- [ ] 13. Update all affected documentation
- [ ] 14. Add/update tests
- [ ] 15. Verify against design documents
- [ ] 16. Commit with clear message
- [ ] 17. Report completion with summary

---

## Example: Complete Implementation Flow

**User Request**: "Add XGBoost classifier to the pipeline"

**Step-by-Step Process**:

```
1. CHECK DOCUMENTATION
   ✓ PROJECT_STRUCTURE.md → nodes/classification/xgboost_classifier.py mentioned as optional
   ✓ DATA_FLOW_ARCHITECTURE.md → Stage 5 covers algorithm training
   ✓ UML_DIAGRAMS.md → Should follow BaseClassifierNode pattern
   ✓ requirements.txt → xgboost already listed as optional

2. CONFIRM WITH USER
   "I found XGBoost is mentioned in PROJECT_STRUCTURE.md as optional.
   I'll implement it following the existing classification node pattern.

   Implementation Plan:
   1. Create nodes/classification/xgboost_classifier.py
   2. Add XGBoost parameter grid to tuning/param_grids.py
   3. Update nodes/classification/__init__.py
   4. Update core/graph.py to add node
   5. Update config/config.py to enable XGBoost
   6. Add tests
   7. Update documentation

   Proceed?"

3. IMPLEMENT STEP BY STEP
   Step 1: Create xgboost_classifier.py
   [Create file with complete implementation]
   ✓ Done

   Step 2: Add parameter grid
   [Modify tuning/param_grids.py]
   ✓ Done

   Step 3: Update __init__.py
   [Add export]
   ✓ Done

   Step 4: Update graph
   [Add node and edges]
   ✓ Done

   Step 5: Update config
   [Add enable_xgboost option]
   ✓ Done

   Step 6: Add tests
   [Create test file]
   ✓ Done

   Step 7: Update docs
   [Update PROJECT_STRUCTURE.md description]
   ✓ Done

4. REPORT COMPLETION
   "✅ XGBoost classifier implementation complete!

   Files Created:
   - nodes/classification/xgboost_classifier.py (147 lines)

   Files Modified:
   - nodes/classification/__init__.py (added export)
   - tuning/param_grids.py (added XGBoost parameter grid)
   - core/graph.py (added xgboost_classifier node)
   - config/config.py (added enable_xgboost flag)
   - tests/unit/test_algorithm_nodes.py (added tests)
   - docs/PROJECT_STRUCTURE.md (updated description)

   The implementation follows the existing pattern and includes:
   - GridSearchCV integration
   - MLflow logging
   - Error handling
   - Unit tests

   Ready to test!"
```

---

## Remember

> "Implementation without documentation is guesswork.
> Documentation without implementation is fiction.
> Both must evolve together, incrementally."

**Always**:
- ✅ Check documentation first
- ✅ Update documentation when needed
- ✅ Implement incrementally
- ✅ Test continuously
- ✅ Verify against design
- ✅ Communicate clearly

**Never**:
- ❌ Implement without checking docs
- ❌ Skip documentation updates
- ❌ Implement large features at once
- ❌ Leave broken tests
- ❌ Deviate from documented design without discussion

---

## Support

For questions about:
- **Architecture**: Check HLD_MLOPS_AUTOMATION.md and SYSTEM_ARCHITECTURE.md
- **Data Flow**: Check DATA_FLOW_ARCHITECTURE.md
- **File Structure**: Check PROJECT_STRUCTURE.md
- **Interactions**: Check SEQUENCE_DIAGRAMS.md
- **Classes**: Check UML_DIAGRAMS.md
- **Workflow**: Check FLOW_DIAGRAMS.md

If documentation is unclear or missing:
1. Flag the gap
2. Propose documentation update
3. Get confirmation
4. Update documentation
5. Then implement

---

## Preprocessing Strategies and Algorithm-Aware HITL System

### Overview

The ML pipeline uses an **intelligent Human-in-the-Loop (HITL) system** that generates algorithm-aware preprocessing questions. Instead of applying fixed preprocessing strategies, the system:

1. **Predicts the likely algorithm category** based on data characteristics
2. **Generates context-specific questions** (1-5 per preprocessing step) tailored to that algorithm
3. **Offers multiple technique options** ranked by suitability for the algorithm type
4. **Executes user-approved techniques** during preprocessing

This ensures optimal preprocessing for the ML algorithm while maintaining human oversight.

---

### Algorithm Categories and Their Preprocessing Requirements

#### 1. Linear Models (Linear Regression, Logistic Regression, SVM)

**Characteristics**:
- Assume linear relationships between features and target
- Strongly affected by outliers
- Require feature scaling
- Sensitive to multicollinearity

**Preprocessing Requirements**:
- **Outlier Handling**: **CRITICAL** - Use Winsorization or Z-score filtering (avoid IQR removal)
- **Missing Values**: Mean/median imputation (simple methods preferred)
- **Scaling**: **REQUIRED** - StandardScaler or MinMaxScaler
- **Encoding**: One-hot encoding for categorical variables
- **Feature Engineering**: Consider polynomial features, interaction terms

**Why**:
- Outliers drastically skew linear models → use capping instead of removal
- Scaling ensures all features contribute equally to the model
- One-hot encoding maintains linear interpretability

---

#### 2. Tree-Based Models (Random Forest, Gradient Boosting, XGBoost)

**Characteristics**:
- Use recursive partitioning (if-then rules)
- Robust to outliers and non-linear relationships
- Handle missing values natively (some implementations)
- Scale-invariant

**Preprocessing Requirements**:
- **Outlier Handling**: **OPTIONAL** - Can skip or use IQR for extreme outliers only
- **Missing Values**: Can use native handling or simple imputation
- **Scaling**: **NOT REQUIRED** - Tree models are scale-invariant
- **Encoding**: Label encoding or target encoding (preferred for high cardinality)
- **Feature Engineering**: Minimal needed

**Why**:
- Trees split on thresholds → absolute values don't matter (scale-invariant)
- Outliers become separate branches → no negative impact
- Target encoding captures category-target relationships better than one-hot

---

#### 3. Neural Networks (Deep Learning, MLPClassifier)

**Characteristics**:
- Learn complex non-linear patterns
- Require large datasets
- Sensitive to feature scales
- Benefit from data augmentation

**Preprocessing Requirements**:
- **Outlier Handling**: **REQUIRED** - Use Z-score or percentile capping
- **Missing Values**: KNN or MICE imputation (preserve relationships)
- **Scaling**: **CRITICAL** - StandardScaler or MinMaxScaler (0-1 range)
- **Encoding**: One-hot encoding or embeddings for categorical variables
- **Feature Engineering**: Normalization, handling class imbalance

**Why**:
- Gradient descent optimization requires consistent feature scales
- Extreme outliers cause vanishing/exploding gradients
- Complex imputation preserves feature correlations

---

#### 4. Ensemble Methods (Stacking, Voting, Blending)

**Characteristics**:
- Combine multiple models
- Requirements depend on base learners
- More robust than individual models

**Preprocessing Requirements**:
- **Outlier Handling**: **MODERATE** - Use Robust techniques (RobustScaler approach)
- **Missing Values**: Multiple imputation or KNN
- **Scaling**: **CONDITIONAL** - Required if ensemble includes linear/neural models
- **Encoding**: Mixed encoding strategies based on base models
- **Feature Engineering**: Diverse feature representations

**Why**:
- Must satisfy requirements of most restrictive base learner
- Robust methods prevent any single model from being negatively impacted

---

#### 5. Time Series Models (ARIMA, Prophet, LSTM)

**Characteristics**:
- Temporal dependencies critical
- Require sequential data integrity
- Sensitive to trends and seasonality

**Preprocessing Requirements**:
- **Outlier Handling**: **CAREFUL** - Use rolling Z-score, not global IQR
- **Missing Values**: Forward-fill, interpolation, or seasonal decomposition (NOT row drop!)
- **Scaling**: Depends on model (LSTM requires scaling, ARIMA doesn't)
- **Encoding**: Cyclical encoding for temporal features (day of week, month)
- **Feature Engineering**: Lag features, rolling statistics, seasonal decomposition

**Why**:
- Dropping rows breaks temporal continuity
- Global outlier detection ignores seasonal patterns
- Forward-fill preserves time-ordered dependencies

---

### Comprehensive Preprocessing Technique Catalog

#### A. Outlier Handling Techniques

| Technique | Algorithm Suitability | Pros | Cons | Use When |
|-----------|----------------------|------|------|----------|
| **IQR Method** | Tree models, Ensemble | Simple, robust to distribution | May remove valid extreme values | Default for tree models |
| **Z-Score Filtering** | Linear, Neural networks | Assumes Gaussian distribution | Requires normal distribution | Data is approximately normal |
| **Percentile Capping (Winsorization)** | Linear models | Preserves data size, reduces impact | May introduce bias at tails | Linear models with outliers |
| **Isolation Forest** | All models | ML-based, handles multivariate | Computationally expensive | Complex multivariate outliers |
| **DBSCAN** | Clustering, Ensemble | Identifies clustered outliers | Requires parameter tuning | Spatial/clustered data |
| **Robust Scalers** | Linear, Neural networks | Keeps data, reduces influence | Doesn't remove outliers | Need to preserve all samples |
| **Domain Clipping** | All models | Preserves domain validity | Requires domain knowledge | Known valid ranges (e.g., age 0-120) |

---

#### B. Missing Value Handling Techniques

| Technique | Algorithm Suitability | Pros | Cons | Use When |
|-----------|----------------------|------|------|----------|
| **Drop Rows** | All models | Simple, no bias introduced | Loses data | <5% missing, large dataset |
| **Mean Imputation** | Linear, Tree models | Fast, simple | Reduces variance, ignores correlations | Low missing %, numerical features |
| **Median Imputation** | Tree models | Robust to outliers | Reduces variance | Skewed distributions |
| **Mode Imputation** | Tree models, Ensemble | Works for categorical | Ignores relationships | Categorical features |
| **KNN Imputation** | Neural networks, Ensemble | Preserves relationships | Slow for large datasets | <30% missing, numerical features |
| **MICE (Iterative)** | Neural networks, Ensemble | Handles complex patterns | Very slow, overfitting risk | Complex relationships, mixed types |
| **Domain-Specific** | All models | Most accurate | Requires domain knowledge | Known imputation rules exist |
| **Constant/Unknown** | Tree models | Simple for categorical | Creates new category | Categorical "missing" is informative |
| **Forward Fill / Interpolation** | Time series | Preserves temporal order | Only for time series | Time series data |

---

#### C. Categorical Encoding Techniques

| Technique | Algorithm Suitability | Pros | Cons | Use When |
|-----------|----------------------|------|------|----------|
| **One-Hot Encoding** | Linear, Neural networks | No ordinal assumption | High dimensionality | Low cardinality (<10 categories) |
| **Label Encoding** | Tree models | Compact, fast | Implies false ordering | Tree models, ordinal variables |
| **Target Encoding** | Tree models, Ensemble | Captures target relationship | Risk of overfitting, leakage | High cardinality (>10 categories) |
| **Frequency Encoding** | All models | Simple, captures popularity | Loses individual category info | Very high cardinality |
| **Binary Encoding** | All models | More compact than one-hot | Less interpretable | Medium cardinality (10-50) |
| **Hash Encoding** | Neural networks, Ensemble | Handles unseen categories | Collision risk | Extreme cardinality (>1000) |
| **Embeddings** | Neural networks | Learns optimal representation | Requires deep learning | Deep learning models |

---

#### D. Feature Scaling Techniques

| Technique | Algorithm Suitability | Pros | Cons | Use When |
|-----------|----------------------|------|------|----------|
| **StandardScaler** | Linear, Neural networks, SVM | Mean=0, Std=1, preserves distribution | Affected by outliers | Data is approximately normal |
| **MinMaxScaler** | Neural networks | Scales to [0,1] range | Very sensitive to outliers | Bounded activation functions (sigmoid) |
| **RobustScaler** | Linear, Neural networks | Uses IQR, robust to outliers | Doesn't guarantee specific range | Data has outliers |
| **MaxAbsScaler** | Sparse data, Neural networks | Preserves sparsity, scales to [-1,1] | Sensitive to outliers | Sparse matrices, positive features |
| **Normalizer** | Text, Neural networks | Scales rows (samples) to unit norm | Unusual use case | Text features, L2 normalization |
| **QuantileTransformer** | Neural networks | Forces uniform/normal distribution | Changes data distribution | Highly skewed data |
| **None (No Scaling)** | Tree models | Fast, preserves interpretation | Required for linear/neural nets | Tree-based models only |

---

### Two-Agent Architecture: Algorithm-Aware Preprocessing System

#### Overview

The system uses **two sequential AI agents** (Agent 1A and Agent 1B) to provide intelligent preprocessing guidance:

- **Agent 1A (Algorithm Category Predictor)**: Analyzes data characteristics and predicts the optimal algorithm category
- **Agent 1B (Preprocessing Question Generator)**: Uses Agent 1A's prediction to generate algorithm-aware preprocessing questions (4-20 total, 1-5 per step)

#### Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│               Enhanced HITL Preprocessing Review System               │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 1: load_data_node                                          │ │
│  │          - Load dataset                                           │ │
│  │          - Extract data profile (shape, dtypes, statistics)      │ │
│  │          Output: raw_data, data_profile                          │ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 2: Agent 1A - Algorithm Category Predictor (NEW)          │ │
│  │          Input:                                                   │ │
│  │          - n_samples, n_features                                  │ │
│  │          - target_type (classification/regression)                │ │
│  │          - feature_types (numeric/categorical distribution)       │ │
│  │          - class_distribution (for classification)                │ │
│  │                                                                   │ │
│  │          Bedrock Prompt:                                          │ │
│  │          "Based on dataset characteristics, predict the most      │ │
│  │           likely algorithm category that will perform best."      │ │
│  │                                                                   │ │
│  │          Output:                                                  │ │
│  │          - algorithm_category: "linear_models" | "tree_models" |  │ │
│  │            "neural_networks" | "ensemble" | "time_series"         │ │
│  │          - confidence: 0.0-1.0                                    │ │
│  │          - reasoning: str                                         │ │
│  │          - recommended_algorithms: List[str]                      │ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 3: Agent 1B - Preprocessing Question Generator (Enhanced) │ │
│  │          Input:                                                   │ │
│  │          - data_profile (statistics, missing%, duplicates)        │ │
│  │          - algorithm_category (from Step 2)                       │ │
│  │          - preprocessing_steps: ["clean_data", "handle_missing", │ │
│  │            "encode_features", "scale_features"]                   │ │
│  │                                                                   │ │
│  │          Processing:                                              │ │
│  │          For each preprocessing step:                             │ │
│  │            1. Analyze data requirements for that step             │ │
│  │            2. Check algorithm category requirements               │ │
│  │            3. Generate 1-5 questions with multiple technique      │ │
│  │               options ranked by suitability                       │ │
│  │            4. Assign priority (HIGH/MEDIUM/LOW) based on:         │ │
│  │               - Algorithm requirements                            │ │
│  │               - Data characteristics                              │ │
│  │                                                                   │ │
│  │          Output:                                                  │ │
│  │          - questions: List[Dict] (4-20 questions total)           │ │
│  │            Grouped by preprocessing step:                         │ │
│  │            • clean_data_questions (1-5 questions)                 │ │
│  │            • handle_missing_questions (1-5 questions)             │ │
│  │            • encode_features_questions (1-5 questions)            │ │
│  │            • scale_features_questions (1-5 questions)             │ │
│  │          - preprocessing_recommendations: Dict[step, technique]   │ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 4: review_config_node                                      │ │
│  │          - Store questions in PostgreSQL (review_questions table)│ │
│  │          - Set state["pipeline_status"] = "awaiting_review"      │ │
│  │          - LangGraph: workflow.interrupt_after(["review_config"])│ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 5: Frontend ReviewForm.jsx                                 │ │
│  │          Display:                                                 │ │
│  │          - Algorithm category prediction banner                   │ │
│  │          - Questions grouped by preprocessing step (tabs)         │ │
│  │          - Each question shows:                                   │ │
│  │            • Question text                                        │ │
│  │            • Multiple technique options (radio buttons)           │ │
│  │            • Recommended option (highlighted in green)            │ │
│  │            • Context tooltip (why this matters)                   │ │
│  │            • Priority badge (HIGH/MEDIUM/LOW)                     │ │
│  │          - Summary panel showing all selections                   │ │
│  │          - Approve / Request Re-Analysis buttons                  │ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 6: User Approves Techniques                                │ │
│  │          POST /api/pipeline/submit-review-answers                │ │
│  │          Body: {                                                  │ │
│  │            "answers": {                                           │ │
│  │              "clean_data_technique": "z_score_filtering",         │ │
│  │              "outlier_threshold": 3.0,                            │ │
│  │              "handle_missing_technique": "knn_imputation",        │ │
│  │              "knn_neighbors": 5,                                  │ │
│  │              "encode_technique": "target_encoding",               │ │
│  │              "scale_technique": "standard_scaler"                 │ │
│  │            },                                                     │ │
│  │            "approved": true                                       │ │
│  │          }                                                        │ │
│  │          - Store in PostgreSQL review_questions.answers (JSONB)  │ │
│  │          - Update state with approved techniques                  │ │
│  │          POST /api/pipeline/continue/{pipeline_run_id}           │ │
│  └──────────────────────────┬────────────────────────────────────────┘ │
│                             │                                          │
│                             ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Step 7: Preprocessing Nodes Execute with Approved Techniques   │ │
│  │          clean_data_node(state):                                  │ │
│  │            technique = state["review_answers"]["clean_data_..."] │ │
│  │            if technique == "z_score_filtering":                   │ │
│  │              apply_z_score_outlier_removal(...)                   │ │
│  │            elif technique == "iqr_method":                        │ │
│  │              apply_iqr_outlier_removal(...)                       │ │
│  │            elif technique == "winsorization":                     │ │
│  │              apply_winsorization(...)                             │ │
│  │            ...                                                    │ │
│  │                                                                   │ │
│  │          handle_missing_node(state):                              │ │
│  │            technique = state["review_answers"]["handle_miss..."] │ │
│  │            if technique == "knn_imputation":                      │ │
│  │              apply_knn_imputation(k=answers["knn_neighbors"])    │ │
│  │            elif technique == "mean_imputation":                   │ │
│  │              apply_mean_imputation(...)                           │ │
│  │            ...                                                    │ │
│  │                                                                   │ │
│  │          encode_features_node(state): ...                         │ │
│  │          scale_features_node(state): ...                          │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
```

#### Question Generation Logic

**Example for Linear Models**:

```python
# Agent 1B receives algorithm_category = "linear_models"

# Question 1 (clean_data): Outlier handling - CRITICAL for linear models
{
  "question_id": "clean_q1",
  "preprocessing_step": "clean_data",
  "question_text": "How should we handle outliers in numerical features?",
  "question_type": "multiple_choice",
  "priority": "high",
  "context": "Linear models are highly sensitive to outliers. Winsorization (capping) is recommended over removal to preserve sample size.",
  "options": [
    {
      "value": "winsorization",
      "label": "Percentile Capping (Winsorization) - 1st/99th percentile",
      "recommended": true,  # ← Highlighted in UI
      "reasoning": "Preserves data size while reducing outlier impact - ideal for linear models"
    },
    {
      "value": "z_score_filtering",
      "label": "Z-Score Filtering (remove |z| > 3)",
      "recommended": false,
      "reasoning": "Removes outliers but loses samples"
    },
    {
      "value": "iqr_method",
      "label": "IQR Method (1.5×IQR bounds)",
      "recommended": false,
      "reasoning": "Too aggressive for linear models, may remove valid data"
    },
    {
      "value": "none",
      "label": "No outlier removal",
      "recommended": false,
      "reasoning": "Not recommended - outliers will skew linear model coefficients"
    }
  ]
}

# Question 2 (scale_features): Scaling - REQUIRED for linear models
{
  "question_id": "scale_q1",
  "preprocessing_step": "scale_features",
  "question_text": "Which scaling method should we use? (Required for linear models)",
  "question_type": "multiple_choice",
  "priority": "high",
  "context": "Linear models require feature scaling so all features contribute equally. StandardScaler is recommended for normally distributed data.",
  "options": [
    {
      "value": "standard_scaler",
      "label": "StandardScaler (mean=0, std=1)",
      "recommended": true,
      "reasoning": "Best for normally distributed features"
    },
    {
      "value": "minmax_scaler",
      "label": "MinMaxScaler (scale to [0,1])",
      "recommended": false,
      "reasoning": "Good alternative, but sensitive to outliers"
    },
    {
      "value": "robust_scaler",
      "label": "RobustScaler (uses IQR)",
      "recommended": false,
      "reasoning": "Use if data has many outliers after cleaning"
    }
  ]
}
```

**Example for Tree Models**:

```python
# Agent 1B receives algorithm_category = "tree_models"

# Question 1 (clean_data): Outlier handling - OPTIONAL for tree models
{
  "question_id": "clean_q1",
  "preprocessing_step": "clean_data",
  "question_text": "Should we remove outliers? (Tree models are naturally robust to outliers)",
  "question_type": "multiple_choice",
  "priority": "low",  # ← Low priority for tree models
  "context": "Tree-based models split data recursively and are robust to outliers. Removal is optional unless outliers are data quality issues.",
  "options": [
    {
      "value": "iqr_method",
      "label": "IQR Method (only extreme outliers)",
      "recommended": true,
      "reasoning": "Remove only obvious data quality issues"
    },
    {
      "value": "none",
      "label": "No outlier removal",
      "recommended": true,  # ← Can have multiple recommended options
      "reasoning": "Tree models handle outliers naturally - often best to keep all data"
    }
  ]
}

# Question 2 (scale_features): Scaling - NOT REQUIRED for tree models
{
  "question_id": "scale_q1",
  "preprocessing_step": "scale_features",
  "question_text": "Should we scale numerical features?",
  "question_type": "yes_no",
  "priority": "low",
  "context": "Tree models are scale-invariant (splits don't depend on feature scales). Scaling is unnecessary but harmless.",
  "options": null,
  "recommended_answer": "no",
  "reasoning": "Skip scaling to save computation time - tree models don't benefit from it"
}
```

#### Dynamic Question Count Logic

```python
def determine_question_count(preprocessing_step, data_characteristics, algorithm_category):
    """
    Determine how many questions to generate for a preprocessing step.

    Returns: int (1-5)
    """
    question_count = 1  # Always at least 1 question per step

    # clean_data step
    if preprocessing_step == "clean_data":
        if data_characteristics["has_outliers"]:
            question_count += 1  # Outlier method question
        if data_characteristics["duplicate_rows"] > 0:
            question_count += 1  # Duplicate handling question
        if algorithm_category == "linear_models":
            question_count += 1  # Additional robustness question

    # handle_missing step
    elif preprocessing_step == "handle_missing":
        missing_pct = data_characteristics["missing_percentage"]
        if missing_pct > 0:
            question_count += 1  # Imputation method
        if missing_pct > 20:
            question_count += 1  # Additional question for high missing rate
        if algorithm_category == "neural_networks":
            question_count += 1  # Advanced imputation option

    # encode_features step
    elif preprocessing_step == "encode_features":
        categorical_count = len(data_characteristics["categorical_columns"])
        if categorical_count > 0:
            question_count += 1
        if data_characteristics["high_cardinality_columns"]:
            question_count += 1  # Target encoding vs frequency encoding

    # scale_features step
    elif preprocessing_step == "scale_features":
        if algorithm_category in ["linear_models", "neural_networks"]:
            question_count += 2  # Scaling required - ask method + parameters
        else:
            question_count += 0  # Tree models - optional, minimal questions

    return min(question_count, 5)  # Cap at 5 questions per step
```

---

### Implementation Guidelines for Enhanced HITL System

#### 1. Agent 1A: Algorithm Category Predictor

**File**: `agents/algorithm_category_predictor.py`

**Input Schema**:
```python
{
    "n_samples": int,
    "n_features": int,
    "target_type": "classification" | "regression",
    "feature_types": {
        "numeric_count": int,
        "categorical_count": int
    },
    "class_distribution": Dict[str, int],  # For classification
    "dataset_size_mb": float
}
```

**Output Schema**:
```python
{
    "algorithm_category": "linear_models" | "tree_models" | "neural_networks" | "ensemble" | "time_series",
    "confidence": float,  # 0.0-1.0
    "reasoning": str,
    "recommended_algorithms": List[str],
    "preprocessing_priorities": Dict[str, str]  # {step: "critical"|"required"|"optional"}
}
```

#### 2. Agent 1B: Enhanced Preprocessing Question Generator

**File**: `agents/preprocessing_question_generator.py` (rename from review_question_generator.py)

**Key Methods**:
- `generate_clean_data_questions()` → Returns 1-5 questions
- `generate_handle_missing_questions()` → Returns 1-5 questions
- `generate_encode_features_questions()` → Returns 1-5 questions
- `generate_scale_features_questions()` → Returns 1-5 questions

**Question Schema** (enhanced):
```python
{
    "question_id": str,
    "preprocessing_step": "clean_data" | "handle_missing" | "encode_features" | "scale_features",
    "question_text": str,
    "question_type": "multiple_choice" | "yes_no" | "numeric_input",
    "priority": "high" | "medium" | "low",
    "context": str,  # Why this matters
    "options": [
        {
            "value": str,  # Internal value (e.g., "knn_imputation")
            "label": str,  # Display text (e.g., "KNN Imputation (k=5)")
            "recommended": bool,  # Highlight in UI
            "reasoning": str  # Why recommended/not recommended
        }
    ],
    "parameters": [  # Optional: technique-specific parameters
        {
            "param_name": "knn_neighbors",
            "param_type": "int",
            "default": 5,
            "range": [3, 10]
        }
    ]
}
```

#### 3. Technique-Based Preprocessing Nodes

Each preprocessing node must:
1. Read approved technique from `state["review_answers"]`
2. Load technique from registry: `from techniques.<step> import TECHNIQUES`
3. Execute technique with user-specified parameters
4. Log technique selection with algorithm context to MLflow
5. Handle missing technique gracefully (use defaults)

**Technique Registry Pattern**:

The preprocessing techniques are organized in a registry structure:
```
nodes/preprocessing/techniques/
├── clean_data.py        # 8 outlier handling techniques
├── handle_missing.py    # 7 missing value imputation techniques
├── encode_features.py   # 7 categorical encoding techniques
└── scale_features.py    # 7 feature scaling techniques
```

Each technique module exports a `TECHNIQUES` dictionary mapping technique names to functions.

**Example**: `ml_pipeline/nodes/preprocessing/clean_data.py`

```python
from techniques.clean_data import TECHNIQUES

def clean_data_node(state: PipelineState) -> PipelineState:
    """Technique-based clean_data node with algorithm-aware execution."""

    # Get algorithm context from Agent 1A
    algorithm_category = state.get("algorithm_category", "tree_models")

    # Get approved technique from review answers
    approved_technique = state.get("review_answers", {}).get("clean_data_technique", "iqr_method")
    technique_params = state.get("review_answers", {}).get("clean_data_params", {})

    # Load technique from registry
    if approved_technique in TECHNIQUES:
        technique_func = TECHNIQUES[approved_technique]
        df = technique_func(state["cleaned_data"], **technique_params)
    elif approved_technique == "none":
        logger.info(f"Skipping outlier removal (algorithm_category={algorithm_category})")
        df = state["cleaned_data"]
    else:
        logger.warning(f"Unknown technique '{approved_technique}', using default")
        df = TECHNIQUES["iqr_method"](state["cleaned_data"], multiplier=1.5)

    # Log technique selection with algorithm context to MLflow
    mlflow.log_param("clean_data_technique", approved_technique)
    mlflow.log_param("algorithm_category", algorithm_category)
    mlflow.log_params(technique_params)

    # Update state with technique metadata
    return {
        **state,
        "cleaned_data": df,
        "technique_applied": approved_technique,
        "technique_metadata": {
            "clean_data": {
                "technique": approved_technique,
                "parameters": technique_params,
                "algorithm_context": algorithm_category
            }
        }
    }
```

**Example Technique Registry**: `ml_pipeline/nodes/preprocessing/techniques/clean_data.py`

```python
"""Outlier handling technique registry (8 techniques)."""
import pandas as pd
from typing import Dict, Callable

def iqr_method(df: pd.DataFrame, multiplier: float = 1.5) -> pd.DataFrame:
    """Remove outliers using IQR method."""
    # Implementation...
    return df

def z_score_filtering(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Remove outliers using Z-score threshold."""
    # Implementation...
    return df

def winsorization(df: pd.DataFrame, lower_pct: int = 1, upper_pct: int = 99) -> pd.DataFrame:
    """Cap outliers at percentiles."""
    # Implementation...
    return df

def isolation_forest(df: pd.DataFrame, contamination: float = 0.1) -> pd.DataFrame:
    """Detect outliers using Isolation Forest."""
    # Implementation...
    return df

def dbscan_outliers(df: pd.DataFrame, eps: float = 0.5, min_samples: int = 5) -> pd.DataFrame:
    """Identify outliers using DBSCAN clustering."""
    # Implementation...
    return df

def robust_scalers(df: pd.DataFrame) -> pd.DataFrame:
    """Apply RobustScaler to reduce outlier impact."""
    # Implementation...
    return df

def domain_clipping(df: pd.DataFrame, bounds: Dict[str, tuple]) -> pd.DataFrame:
    """Clip values to domain-specific ranges."""
    # Implementation...
    return df

def none_technique(df: pd.DataFrame) -> pd.DataFrame:
    """Skip outlier removal (no-op)."""
    return df

# Registry dictionary
TECHNIQUES: Dict[str, Callable] = {
    "iqr_method": iqr_method,
    "z_score_filtering": z_score_filtering,
    "winsorization": winsorization,
    "isolation_forest": isolation_forest,
    "dbscan": dbscan_outliers,
    "robust_scalers": robust_scalers,
    "domain_clipping": domain_clipping,
    "none": none_technique
}
```

#### 4. Frontend ReviewForm.jsx Enhancement

**New Features**:
- **Tabbed Interface**: One tab per preprocessing step
- **Algorithm Category Banner**: Display predicted category at top
- **Technique Comparison Table**: Show pros/cons of each option
- **Recommended Badges**: Green checkmark for recommended techniques
- **Parameter Inputs**: Slider/input for technique parameters (e.g., k for KNN)
- **Live Preview**: Show sample of what technique will do (if possible)

**UI Mockup**:
```
┌─────────────────────────────────────────────────────────────────────┐
│  📊 Preprocessing Configuration Review                              │
│                                                                     │
│  🎯 Predicted Algorithm Category: Tree-Based Models (confidence 87%)│
│     Recommended algorithms: Random Forest, XGBoost, Gradient Boost  │
├─────────────────────────────────────────────────────────────────────┤
│  Tab: [Clean Data] [Handle Missing] [Encode Features] [Scale]      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Question 1 of 3  [HIGH PRIORITY]                                   │
│  ─────────────────────────────────────────────────────────────────  │
│  How should we handle outliers in numerical features?               │
│  💡 Tree-based models are robust to outliers. Removal is optional.  │
│                                                                     │
│  ○ IQR Method (only extreme outliers) ✓ RECOMMENDED                │
│     Removes only obvious data quality issues                        │
│                                                                     │
│  ○ No outlier removal ✓ RECOMMENDED                                │
│     Tree models handle outliers naturally                           │
│                                                                     │
│  ○ Z-Score Filtering (|z| > 3)                                     │
│     More aggressive - may lose valid samples                        │
│                                                                     │
│  [Previous]  [Next (2/3)]                                          │
├─────────────────────────────────────────────────────────────────────┤
│  Summary: 8 questions answered, 2 pending                          │
│  [✓ Approve & Continue Pipeline]  [🔄 Request Re-Analysis]        │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Documentation Update Requirements

When implementing enhanced HITL system, update:

1. **HLD_MLOPS_AUTOMATION.md**:
   - Section 5.3: Replace with enhanced HITL architecture
   - Section 5.3.3: Update Agent 1 to Agent 1A and 1B
   - Add preprocessing technique tables

2. **DATA_FLOW_ARCHITECTURE.md**:
   - Update Stage 2 (Data Loading) to include algorithm prediction
   - Update Stage 3 (Preprocessing) to show technique selection
   - Update state schema with new fields

3. **SEQUENCE_DIAGRAMS.md**:
   - Add "Algorithm Category Prediction" sequence
   - Update "HITL Review Workflow" with new question types
   - Add "Technique-Based Preprocessing" sequence

4. **FLOW_DIAGRAMS.md**:
   - Update 2LD with Agent 1A/1B split
   - Update 3LD with dynamic question generation logic

5. **PROJECT_STRUCTURE.md**:
   - Add `agents/algorithm_category_predictor.py`
   - Rename `agents/review_question_generator.py` → `agents/preprocessing_question_generator.py`
   - Document enhanced preprocessing nodes

---

**Last Updated**: 2025-12-06
**Version**: 2.0.0
