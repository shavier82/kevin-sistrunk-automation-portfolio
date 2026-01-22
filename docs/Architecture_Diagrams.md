# System Architecture Diagrams

Visual representations of the automation system architecture for portfolio and documentation use.

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User/Client Interface                         │
│              (API, CLI, Web Interface, etc.)                     │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Integration Layer (Python)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         ServiceOrchestrator                                │  │
│  │  - Unified API for all services                             │  │
│  │  - Caching & error handling                                │  │
│  │  - Batch operations                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Service 1  │    │   Service 2  │    │   Service N  │
│  (Data API)  │    │  (Rules API) │    │  (Custom API)│
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              State Management Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         StateManager                                     │  │
│  │  - Atomic updates                                        │  │
│  │  - Automatic backups                                     │  │
│  │  - Conflict resolution                                   │  │
│  │  - Validation                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Parallel Processing Engine                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ REFEREE  │  │NARRATOR  │  │  STATE   │  │    QA     │       │
│  │  Agent   │  │  Agent   │  │ PATCHER  │  │COMPLIANCE │       │
│  │          │  │          │  │  Agent   │  │  Agent    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│     │              │              │              │              │
│     └──────────────┴──────────────┴──────────────┘              │
│                            │                                     │
│                            ▼                                     │
│                  ┌─────────────────┐                            │
│                  │  Result Merger   │                            │
│                  └─────────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final Output   │
                    │  (Validated)     │
                    └─────────────────┘
```

---

## 2. Service Integration Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Application                            │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Calls unified API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              ServiceOrchestrator                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Methods:                                                │  │
│  │  - get_entity_data()                                     │  │
│  │  - update_entity_status()                                │  │
│  │  - lookup_rule()                                         │  │
│  │  - execute_action()                                      │  │
│  │  - log_event()                                          │  │
│  │  - batch_lookup_entities()  [Parallel]                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Internal Cache                                           │  │
│  │  - Reduces API calls                                      │  │
│  │  - Improves performance                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Data Service│    │ Rules Service│    │ Audit Service│
│   (REST API) │    │   (REST API) │    │   (REST API) │
└──────────────┘    └──────────────┘    └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Normalized     │
                    │  Response       │
                    └─────────────────┘
```

**Key Benefits:**
- Single interface for all services
- Automatic caching
- Error handling and retries
- Parallel batch operations

---

## 3. State Management Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    State Update Request                          │
│              (Delta: entity_001.resource -= 1)                  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              StateManager                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Parse Delta                                          │  │
│  │     - Validate format                                    │  │
│  │     - Extract (entity, resource, amount)                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  2. Load Current State                                   │  │
│  │     - Read from file                                     │  │
│  │     - Validate schema                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  3. Create Backup                                        │  │
│  │     - Copy current state                                 │  │
│  │     - Timestamp backup                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  4. Validate & Apply Delta                               │  │
│  │     - Check resource availability                        │  │
│  │     - Prevent underflow                                  │  │
│  │     - Apply changes atomically                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5. Validate Updated State                               │  │
│  │     - Schema validation                                  │  │
│  │     - Business rule checks                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  6. Save Atomically                                      │  │
│  │     - Write to temp file                                 │  │
│  │     - Atomic rename                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Updated State  │
                    │  (Validated)    │
                    └─────────────────┘
```

**Key Features:**
- Atomic updates (all-or-nothing)
- Automatic backups
- Resource underflow prevention
- Schema validation

---

## 4. Parallel Processing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow Input                                │
│              {action: {type: "validate", ...}}                  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Parallel Agent System                               │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  asyncio.gather() - Parallel Execution                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│     ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│     │   REFEREE    │  │   NARRATOR   │  │    STATE     │      │
│     │    Agent     │  │    Agent     │  │   PATCHER    │      │
│     │              │  │              │  │    Agent     │      │
│     │ • Validate   │  │ • Generate   │  │ • Generate   │      │
│     │   rules      │  │   narration │  │   patches    │      │
│     │ • Calculate  │  │ • Suggest   │  │ • Track      │      │
│     │   outcome    │  │   actions    │  │   resources  │      │
│     └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│            │                 │                 │                │
│            └─────────────────┼─────────────────┘                │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  QA_COMPLIANCE   │                         │
│                    │      Agent        │                         │
│                    │                   │                         │
│                    │ • Validate        │                         │
│                    │   schemas         │                         │
│                    │ • Check          │                         │
│                    │   compliance     │                         │
│                    └────────┬─────────┘                         │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Result Merger                                           │  │
│  │  - Check for blocks                                      │  │
│  │  - Validate QA status                                    │  │
│  │  - Compose final output                                  │  │
│  │  - Handle conflicts                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Final Output   │
                    │  (Validated)    │
                    │  < 5 seconds    │
                    └─────────────────┘
```

**Performance:**
- Sequential: ~15-20 seconds
- Parallel: ~4-5 seconds
- **Speedup: 3-4x**

---

## 5. Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Request                                  │
│         "Process incident: threat_001"                         │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Service Integration Layer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Lookup incident data (Data Service)                 │  │
│  │  2. Validate rules (Rules Service)                      │  │
│  │  3. Check environment (Data Service)                    │  │
│  │  4. Log event (Audit Service)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Parallel Agent Execution                                │  │
│  │  - REFEREE: Validate & calculate                        │  │
│  │  - NARRATOR: Generate output                             │  │
│  │  - STATE_PATCHER: Update state                           │  │
│  │  - QA_COMPLIANCE: Validate                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  State Management                                         │  │
│  │  - Create backup                                          │  │
│  │  - Apply state patches                                    │  │
│  │  - Validate updated state                                 │  │
│  │  - Save atomically                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Result Merging                                           │  │
│  │  - Combine agent outputs                                  │  │
│  │  - Validate compliance                                   │  │
│  │  - Generate final response                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  User Response  │
                    │  + State Update │
                    └─────────────────┘
```

**Total Time: < 5 seconds**

---

## 6. Security Operations Application (XSOAR/XSIAM)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Incident                             │
│              "Malware detected on endpoint_001"                 │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              XSOAR/XSIAM Playbook Execution                      │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Service Integration Layer                               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │   SIEM   │  │    EDR    │  │ Ticketing│            │  │
│  │  │   API    │  │    API    │  │   API    │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │  │
│  │  │ Threat   │  │   Case   │  │  Threat  │            │  │
│  │  │  Intel   │  │Management│  │ Hunting  │            │  │
│  │  └──────────┘  └──────────┘  └──────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Parallel Processing                                     │  │
│  │  - Validate threat (REFEREE)                             │  │
│  │  - Generate report (NARRATOR)                            │  │
│  │  - Update incident state (STATE_PATCHER)                 │  │
│  │  - Ensure compliance (QA_COMPLIANCE)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  State Management                                         │  │
│  │  - Track incident lifecycle                              │  │
│  │  - Sync across systems                                    │  │
│  │  - Maintain audit trail                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Incident       │
                    │  Resolved       │
                    │  < 5 seconds    │
                    └─────────────────┘
```

**Real-World Application:**
- Incident response automation
- Threat hunting workflows
- Compliance reporting
- Multi-tool orchestration

---

## 7. Performance Comparison

```
Sequential Execution:
┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐
│Agent│───▶│Agent│───▶│Agent│───▶│Agent│
│  1  │    │  2  │    │  3  │    │  4  │
└─────┘    └─────┘    └─────┘    └─────┘
  │          │          │          │
  4s         4s         4s         4s
  │          │          │          │
  └──────────┴──────────┴──────────┘
              Total: ~16 seconds

Parallel Execution:
┌─────┐
│Agent│
│  1  │──┐
└─────┘  │
         │
┌─────┐  │  ┌──────────┐
│Agent│──┼─▶│  Merge   │
│  2  │  │  │ Results  │
└─────┘  │  └──────────┘
         │
┌─────┐  │
│Agent│──┘
│  3  │
└─────┘
         │
┌─────┐  │
│Agent│──┘
│  4  │
└─────┘
  │      │
  4s     │
  │      │
  └──────┘
    Total: ~4-5 seconds

Speedup: 3-4x faster
```

---

## Usage in Documentation

These diagrams can be used in:
- Portfolio README
- Blog posts
- Technical documentation
- Proposals and presentations
- Architecture documentation

**Format:** ASCII/text-based for easy inclusion in Markdown files.

**Customization:** Easy to modify for specific use cases or add color/style in presentation tools.
