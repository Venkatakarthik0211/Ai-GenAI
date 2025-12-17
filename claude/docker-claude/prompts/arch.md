# Architecture Diagram Prompt for OpenAI Image Generation

Generate a professional, detailed technical architecture diagram showing the Claude Code Automated Code Generation System with Guardrails. Use a clean, modern style with clear visual hierarchy.

## Visual Elements Required:

### 1. Host System (Left Side - Light Blue Background)
- **AWS Credentials Storage**
  - Show a folder icon labeled "~/.aws/" containing:
    - "credentials" file
    - "config" file
  - Add a lock icon indicating security
  - Label: "IAM-Based Authentication (Guardrail #1)"

### 2. Docker Container (Center - Gray Border Box)
- Large rectangular container with dashed border
- Label at top: "Docker Container - Isolated Environment (Guardrail #2)"

**Inside the container, show these layers from top to bottom:**

#### Layer A: Root Context (Red tinted section at top)
- Small section showing:
  - AWS CLI installation icon
  - bedrock.py script icon
  - Arrow pointing down with label "Bearer Token Generation"
  - Lock icon with "SigV4 Signing"

#### Layer B: User Context Switch (Orange section)
- Horizontal dividing line with downward arrow
- Label: "Switch to claude-user (Non-root Guardrail #3)"
- Show user icon changing from "root" to "claude-user"

#### Layer C: Claude Code Execution (Green section - largest)
- Claude Code CLI icon/logo
- settings.json file icon with label "Permission Config (Guardrail #4)"
- Command line showing: `--dangerously-skip-permissions`
- Label: "Headless/Automated Mode"

**Inside Claude Code execution area:**
- Small box showing "code-generator subagent"
  - List capabilities: Read, Write, Glob, Grep, Bash
  - Label: "Bounded Tools (Guardrail #5)"

#### Layer D: File System Operations (Blue section at bottom)
Show three distinct areas:

**Left box (Read-Only - Red border):**
- Label: ".claude/agents/ (Read-Only Guardrail #6)"
- Show file: "code-generator.md"
- Lock icon

**Center box (Read-Write - Green border):**
- Label: ".agents/ (Specification Guardrail #7)"
- Show multiple PROMPT.md files:
  - "api/PROMPT.md"
  - "frontend/PROMPT.md"
  - "database/PROMPT.md"
- Magnifying glass icon labeled "Discovery"

**Right box (Read-Write - Green border):**
- Label: "output/ (Audit Trail Guardrail #8)"
- Show file: "execution.log"
- Clock icon indicating timestamps

### 3. Output Flow (Right Side - Green Background)
- Arrow from container pointing to right side
- Show directory tree of generated code:
```
.agents/
├── test-app/
│   ├── api/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── ...
│   ├── frontend/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── ...
│   └── database/
│       ├── schema.sql
│       └── ...
```
- Label: "Production-Ready Code Output"

### 4. Data Flow Arrows
Show numbered arrows indicating flow:
1. **Red arrow**: AWS credentials (read-only) → Docker container
2. **Orange arrow**: PROMPT.md specs → Claude Code CLI
3. **Blue arrow**: code-generator subagent → File operations
4. **Green arrow**: Generated files → Output directory
5. **Purple arrow**: Execution logs → Audit trail

### 5. Guardrail Indicators
Add shield icons with numbers 1-8 at each guardrail enforcement point:
1. Shield at AWS credentials (Authentication)
2. Shield at Docker boundary (Isolation)
3. Shield at user context switch (Non-root execution)
4. Shield at settings.json (Permission control)
5. Shield at subagent box (Tool boundaries)
6. Shield at .claude mount (Read-only config)
7. Shield at PROMPT.md discovery (Specification-driven)
8. Shield at execution.log (Audit trails)

### 6. Legend Box (Bottom Right)
Show a small legend box containing:
- **Red Border** = Read-Only Access
- **Green Border** = Read-Write Access
- **Shield Icon** = Guardrail Enforcement Point
- **Lock Icon** = Security Control
- **Arrow Colors**:
  - Red = Credentials
  - Orange = Specifications
  - Blue = Processing
  - Green = Output
  - Purple = Logging

## Color Scheme:
- **Host System**: Light blue background (#E3F2FD)
- **Docker Container**: Gray border (#757575) with white background
- **Root Context**: Light red tint (#FFEBEE)
- **Non-root Context**: Light orange tint (#FFF3E0)
- **Execution Context**: Light green tint (#E8F5E9)
- **File System**: Light blue tint (#E1F5FE)
- **Output Area**: Light green background (#F1F8E9)
- **Read-Only Borders**: Red (#D32F2F)
- **Read-Write Borders**: Green (#388E3C)
- **Arrows**: Use specified colors (red, orange, blue, green, purple)

## Style Guidelines:
- Use clean, modern flat design
- Icons should be simple and recognizable
- Text should be legible (minimum 10pt font equivalent)
- Use consistent spacing between elements
- Add subtle drop shadows for depth
- Ensure all labels are clearly visible
- Use rounded corners for boxes (5px radius)
- Make arrows bold and directional
- Number all guardrail shields (1-8)

## Layout Orientation:
- Horizontal layout (landscape)
- Left to right flow (Host → Container → Output)
- Top to bottom privilege elevation (Root → Non-root)
- Clear visual separation between sections

## Additional Details:
- Show Docker logo/icon on container border
- Include AWS logo near credentials section
- Add Claude/Anthropic branding near CLI section
- Show version numbers: "Docker 3.8", "Claude Code CLI", "Python 3.10+"
- Include timestamp/date indicator on execution log
- Add small "✓" checkmarks at successful guardrail points

## Annotations:
Add small text annotations explaining key concepts:
- "IAM-based authentication eliminates API key risks"
- "Container isolation prevents host system contamination"
- "Non-root execution limits privilege escalation"
- "Bounded tool access prevents arbitrary code execution"
- "Read-only configs prevent tampering"
- "Specification-driven approach ensures controlled generation"
- "Audit trails enable compliance and debugging"

This diagram should clearly show how multiple layers of guardrails work together to create a secure, controlled, automated code generation system suitable for enterprise use.
