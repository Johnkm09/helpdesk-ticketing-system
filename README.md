# Helpdesk Ticketing System (HTS) API

A Helpdesk Ticketing System REST API built with Django REST Framework for managing customer support workflows, including ticket creation, automated assignment, agent communication, follow-ups, notifications, resolution, and closure.

The system follows a layered backend architecture with clear separation between API handling, authentication and authorization, validation, business logic, persistence, background processing, testing, documentation, CI/CD, and infrastructure.

---

<details>
<summary><strong>Contents</strong></summary>

* [System Overview](#system-overview)
* [Architecture & Design Patterns](#architecture--design-patterns)
* [API & Business Workflows](#api--business-workflows)
* [Ticket Lifecycle](#ticket-lifecycle)
* [Background Processing](#background-processing)
* [Database & Data Integrity](#database--data-integrity)
* [Authentication & Authorization](#authentication--authorization)
* [Audit History](#audit-history)
* [Testing](#testing)
* [API Documentation](#api-documentation)
* [CI/CD & Git Workflow](#cicd--git-workflow)
* [Infrastructure & Containerization](#infrastructure--containerization)
* [Cloud & Deployment](#cloud--deployment)
* [Security](#security)
* [Technology Stack](#technology-stack)
* [Local Development](#local-development)
* [Project Status](#project-status)

</details>

---

## System Overview

The HTS API provides backend services for managing the complete customer support lifecycle.

### Core capabilities

* Authentication and authorization
* Customer ticket creation
* Ticket categorization
* Automated ticket assignment
* Agent ticket management
* Customer and agent communication
* Internal notes
* Ticket status management
* Customer follow-ups
* Notifications
* Automated reminders
* Inactivity detection
* Automatic ticket closure
* Ticket reassignment
* Audit history
* File attachments
* Operational reporting

### Engineering overview

**Django REST Framework · Layered Architecture · PostgreSQL · Redis · Celery · Automated Testing · OpenAPI · Docker · GitHub Actions · AWS**

---

## Architecture & Design Patterns

The application follows a layered architecture with clearly defined responsibilities.

```text
Client
  ↓
URL / Router
  ↓
Authentication
  ↓
Permission / Authorization
  ↓
API View
  ↓
Serializer
  ↓
Service / Application Layer
  ↓
Repository / Data Access
  ↓
Django ORM
  ↓
PostgreSQL
```

### Architecture responsibilities

| Layer          | Responsibility                                       |
| -------------- | ---------------------------------------------------- |
| URLs / Routers | Define API endpoints and routing                     |
| Authentication | Identify authenticated API users                     |
| Permissions    | Enforce role and resource access rules               |
| API Views      | Coordinate HTTP requests and responses               |
| Serializers    | Validate and transform API data                      |
| Services       | Execute application and business workflows           |
| Repositories   | Encapsulate persistence operations where appropriate |
| Django ORM     | Provide database interaction and relationships       |
| PostgreSQL     | Provide persistent relational storage                |
| Celery         | Execute asynchronous and scheduled workloads         |
| Redis          | Provide task broker and supporting infrastructure    |

### Service Layer

Business workflows are handled by dedicated services rather than placing complex business logic inside API views.

Services coordinate operations such as:

* Ticket creation
* Ticket assignment
* Ticket status transitions
* Ticket resolution
* Ticket reopening
* Customer confirmation
* Notifications
* Follow-up workflows
* Audit history

This keeps HTTP concerns separate from application behavior.

### Repository / Data Access Layer

Persistence operations can be isolated behind repository interfaces where useful.

```text
TicketService
     ↓
TicketRepository
     ↓
Django ORM
     ↓
PostgreSQL
```

This provides separation between business workflows and persistence concerns and makes data access behavior easier to test and evolve.

### Dependency Injection

Application services depend on defined interfaces or collaborators rather than tightly coupling business workflows to implementation details where abstraction provides value.

Dependencies are configured through Django's application configuration and dependency management patterns.

### Serializers

Django REST Framework serializers provide the API validation and representation boundary.

They are responsible for:

* Request validation
* Input normalization
* Response serialization
* Field-level validation
* Object-level validation

Business workflows remain in the application/service layer rather than being hidden inside serializers.

### Permissions & Authorization

Authorization is handled independently from business logic.

Permissions determine whether a user may:

* View a resource
* Create a resource
* Update a resource
* Change a ticket state
* Reassign a ticket
* Add internal notes
* Perform manager operations

Object-level authorization is applied where resource ownership or assignment matters.

---

## API & Business Workflows

The API follows REST conventions and is versioned under:

```text
/api/v1/
```

Resources use appropriate HTTP methods, status codes, validation responses, pagination, filtering, sorting, and consistent response structures.

### Ticket creation workflow

```text
Customer
  ↓
Create Ticket
  ↓
Validate Request
  ↓
Create Ticket
  ↓
Record History
  ↓
Determine Assignment
  ↓
Assign Agent
  ↓
Notify Relevant Users
```

### Ticket assignment

New tickets can be automatically assigned to eligible agents using an application-level assignment strategy.

The initial strategy considers active ticket workload when determining an appropriate agent.

The assignment mechanism is isolated so that the strategy can later evolve without changing the rest of the ticket workflow.

Possible future strategies include:

* Least active tickets
* Round-robin assignment
* Skill/category matching
* Availability-aware assignment
* Priority-aware assignment

### Ticket communication

Customer-visible communication is separated from internal notes.

```text
Customer
  ↕
Ticket Comments
  ↕
Agent
```

Internal notes are available to authorized support personnel and are not exposed to customers.

### Ticket resolution

```text
Agent
  ↓
Resolve Ticket
  ↓
Customer Notified
  ↓
Customer Confirms
  ↓
Ticket Closed
```

A resolved ticket does not automatically become closed merely because an agent marks it resolved. The system supports customer confirmation and authorized management actions.

### Customer inactivity workflow

```text
Ticket Waiting for Customer
          ↓
     Inactivity Period
          ↓
        Reminder
          ↓
Customer Still Inactive
          ↓
    Automatic Closure
```

The reminder and automatic closure operations are handled asynchronously through Celery.

### Ticket reopening

Authorized users can reopen a closed ticket when additional work is required.

```text
CLOSED
  ↓
Authorized Reopen
  ↓
IN_PROGRESS
```

The reopening operation is recorded in the ticket history.

---

## Ticket Lifecycle

Tickets use an explicit state model.

```text
OPEN
  ↓
ASSIGNED
  ↓
IN_PROGRESS
  ├──────────────→ WAITING_FOR_CUSTOMER
  │                         ↓
  │                  IN_PROGRESS
  │
  └──────────────→ RESOLVED
                         ↓
                       CLOSED
```

Authorized users may reopen a closed ticket:

```text
CLOSED
  ↓
IN_PROGRESS
```

### Ticket states

| Status                 | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `OPEN`                 | Ticket has been created but has not yet been assigned       |
| `ASSIGNED`             | Ticket has been assigned to an agent                        |
| `IN_PROGRESS`          | Agent is actively working on the ticket                     |
| `WAITING_FOR_CUSTOMER` | Further information or action is required from the customer |
| `RESOLVED`             | Agent has completed the requested support work              |
| `CLOSED`               | Ticket lifecycle has been completed                         |

### State transition rules

Valid transitions are enforced by application business rules.

```text
OPEN → ASSIGNED

ASSIGNED → IN_PROGRESS

IN_PROGRESS → WAITING_FOR_CUSTOMER

IN_PROGRESS → RESOLVED

WAITING_FOR_CUSTOMER → IN_PROGRESS

WAITING_FOR_CUSTOMER → CLOSED

RESOLVED → CLOSED

CLOSED → IN_PROGRESS
```

Invalid transitions are rejected rather than allowing clients to arbitrarily modify ticket state.

---

## Background Processing

Redis and Celery provide the infrastructure for asynchronous and scheduled operations.

Background processing is used where work does not need to block the original API request.

### Asynchronous workflow

```text
Django API
   ↓
Create Celery Task
   ↓
Redis
   ↓
Celery Worker
   ↓
Background Operation
```

Examples include:

* Sending notifications
* Processing reminders
* Ticket follow-ups
* Non-blocking application tasks
* Automated workflow operations

### Scheduled processing

Celery Beat is used for scheduled operations.

```text
Celery Beat
   ↓
Scheduled Task
   ↓
Redis
   ↓
Celery Worker
   ↓
Business Operation
```

Scheduled workflows include:

* Detecting inactive tickets
* Sending customer reminders
* Identifying tickets eligible for automatic closure
* Executing recurring operational tasks

### Automatic ticket closure

The system can periodically identify tickets that have remained inactive beyond the configured period.

```text
Scheduled Check
      ↓
Find Eligible Tickets
      ↓
Validate Current State
      ↓
Close Ticket
      ↓
Record Audit Event
      ↓
Notify Relevant Users
```

Background tasks are designed to be safe to retry and should avoid performing duplicate business operations.

---

## Database & Data Integrity

PostgreSQL provides the primary relational database for the application.

Django ORM is used for database interaction while critical integrity rules are reinforced through database constraints and transactional operations.

### Database responsibilities

* Foreign-key relationships
* Unique constraints
* Indexes
* Referential integrity
* Transactional operations
* Controlled deletion behavior
* Consistent relationships
* Atomic state changes

### Core domain relationships

```text
User
 ├── Customer
 │      ↓
 │    Tickets
 │      ↓
 │    Comments
 │
 └── Agent
        ↓
      Tickets

Category
   ↓
Tickets

Ticket
 ├── Comments
 ├── Attachments
 └── Ticket History
```

### Transactional integrity

Critical multi-step operations are executed within database transactions where multiple records must remain consistent.

For example:

```text
Ticket Assignment
      +
Assignment History
      ↓
    COMMIT
```

Or:

```text
Ticket Status Change
      +
Audit History
      ↓
    COMMIT
```

If a critical operation fails, the transaction can be rolled back rather than leaving partially updated data.

### Database constraints

The database provides an additional layer of protection against invalid application states.

Examples include:

* Unique constraints
* Foreign-key constraints
* Required fields
* Valid relationships
* Appropriate indexes

Application validation provides user-friendly errors while database constraints provide final data integrity protection.

### Indexing

Indexes will be applied to fields frequently used for:

* Ticket filtering
* Ticket status queries
* Agent assignment
* Customer ticket retrieval
* Category filtering
* Date-based reporting
* Audit history queries

---

## Authentication & Authorization

The system uses authenticated API access with role-based authorization.

### User roles

```text
CUSTOMER
AGENT
MANAGER
```

### Customer access

Customers can access only resources they are authorized to view.

For example:

```text
Customer A
   ↓
Customer A's Tickets
```

Customer A must not be able to retrieve:

```text
Customer B's Tickets
```

through manipulated IDs or API parameters.

### Agent access

Agents can access tickets according to their assigned permissions and ticket relationships.

Agent capabilities include:

* Viewing assigned tickets
* Updating permitted ticket states
* Adding comments
* Adding internal notes
* Resolving tickets

### Manager access

Managers have broader operational permissions.

Manager capabilities include:

* Viewing support tickets
* Assigning tickets
* Reassigning tickets
* Managing agents
* Managing categories
* Reviewing ticket history
* Reopening tickets
* Closing tickets
* Accessing operational reports

Authorization is enforced server-side rather than relying on frontend restrictions.

---

## Audit History

Important ticket operations are recorded in a historical record.

Examples include:

* Ticket creation
* Assignment
* Reassignment
* Status changes
* Comments
* Internal notes
* Resolution
* Customer confirmation
* Reminder
* Automatic closure
* Reopening
* Manager actions

A ticket history provides a chronological record of how the ticket changed over time.

Example:

```text
Ticket Created
      ↓
Assigned to Agent A
      ↓
Status: IN_PROGRESS
      ↓
Agent Added Comment
      ↓
Status: WAITING_FOR_CUSTOMER
      ↓
Reminder Sent
      ↓
Customer Replied
      ↓
Status: IN_PROGRESS
      ↓
Resolved
      ↓
Customer Confirmed
      ↓
Closed
```

Automated operations performed by Celery are recorded in the same history where appropriate.

---

## Testing

The application uses Pytest and pytest-django for automated testing.

Testing is divided across unit, integration, API, and workflow behavior.

### Unit Tests

Unit tests isolate application components and verify:

* Business rules
* Assignment logic
* State transition rules
* Calculations
* Service behavior
* Validation behavior

### API Tests

API tests verify complete HTTP behavior including:

* Authentication
* Authorization
* Request validation
* HTTP status codes
* Response structures
* Pagination
* Filtering
* Sorting
* Customer isolation
* Agent permissions
* Manager permissions

### Workflow Tests

Workflow tests verify complete business processes.

Example:

```text
Create Ticket
     ↓
Assign Ticket
     ↓
Work Ticket
     ↓
Resolve Ticket
     ↓
Customer Confirmation
     ↓
Close Ticket
```

### Background Task Tests

Celery-related tests verify:

* Reminder behavior
* Inactivity detection
* Automatic closure
* Notification tasks
* Retry-safe behavior
* Task/business-rule integration

### Concurrency-sensitive tests

Important workflows are tested for conditions where concurrent requests could otherwise produce inconsistent state.

Examples include:

* Concurrent assignment
* Simultaneous status changes
* Duplicate operations

### Test execution

```bash
pytest
```

The automated test suite is also executed through GitHub Actions.

---

## API Documentation

The API is documented using OpenAPI.

Interactive documentation will provide:

* Endpoints
* HTTP methods
* Authentication
* Request parameters
* Request bodies
* Validation requirements
* Response structures
* Example responses

The project will expose interactive documentation through Swagger UI and ReDoc.

Example API root:

```text
/api/v1/
```

---

## CI/CD & Git Workflow

The project uses GitHub Actions for continuous integration.

### Development workflow

```text
Feature Branch
     ↓
Implementation
     ↓
Automated Tests
     ↓
Commit
     ↓
Push
     ↓
Pull Request
     ↓
GitHub Actions
     ↓
Code Review
     ↓
Merge
```

### Branch structure

```text
main
 ↑
develop
 ↑
feature/*
```

### `main`

Contains production-ready code.

### `develop`

Integration branch where completed features are combined and validated before production release.

### `feature/*`

Used for individual development tasks.

Examples:

```text
feature/authentication
feature/ticket-model
feature/ticket-api
feature/ticket-assignment
feature/ticket-comments
feature/celery-reminders
feature/notifications
feature/reporting
feature/aws-deployment
```

### `hotfix/*`

Used for urgent production corrections.

### CI pipeline

Pull requests will automatically execute relevant checks such as:

```text
Install Dependencies
        ↓
Code Quality Checks
        ↓
Run Tests
        ↓
Build Validation
```

The goal is to catch problems before changes are merged into the integration or production branches.

---

## Infrastructure & Containerization

Docker is used to provide a consistent development environment.

### Development services

The local environment is expected to include:

```text
┌──────────────────────────────┐
│        Django / DRF          │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       ↓                ↓
  PostgreSQL          Redis
                        ↓
                 Celery Worker
                        ↑
                   Celery Beat
```

Docker Compose orchestrates the local infrastructure.

### PostgreSQL

PostgreSQL provides persistent relational storage for application data.

### Redis

Redis provides infrastructure for asynchronous task processing and other supporting workloads.

### Celery Worker

Celery workers execute background tasks outside the request/response cycle.

### Celery Beat

Celery Beat schedules recurring tasks such as inactivity detection and automated follow-ups.

---

## Cloud & Deployment

The application is intended for deployment on Amazon Web Services (AWS).

The AWS deployment will be implemented as a dedicated production phase after the application and infrastructure have been completed and tested locally.

### Target architecture

```text
                         Internet
                            │
                            ↓
                   ┌─────────────────┐
                   │  Load Balancer  │
                   └────────┬────────┘
                            ↓
                ┌───────────────────────┐
                │    Django / DRF API   │
                └───────────┬───────────┘
                            │
                 ┌──────────┴──────────┐
                 ↓                     ↓
          ┌─────────────┐       ┌─────────────┐
          │ PostgreSQL  │       │    Redis    │
          └─────────────┘       └──────┬──────┘
                                       ↓
                                ┌─────────────┐
                                │   Celery    │
                                │   Workers   │
                                └─────────────┘

                         Celery Beat
                              ↓
                       Scheduled Tasks
```

### Production infrastructure

The final AWS architecture is expected to address:

* Django application hosting
* Application load balancing
* Managed PostgreSQL
* Redis
* Celery workers
* Scheduled Celery tasks
* Object storage for attachments
* HTTPS/TLS
* Environment configuration
* Secrets management
* Logging
* Monitoring
* Health checks
* Database backups
* CI/CD deployment

The exact AWS services will be documented once the production deployment is implemented.

### Deployment workflow

The intended production workflow is:

```text
Feature Branch
     ↓
Pull Request
     ↓
CI
     ↓
Code Review
     ↓
develop
     ↓
Production Validation
     ↓
main
     ↓
AWS Deployment
```

---

## Security

Security controls are applied across the application, database, API, and infrastructure layers.

### Application security

* Authentication
* Role-based authorization
* Object-level authorization
* Customer data isolation
* Input validation
* Secure password handling
* Permission checks
* Controlled API access

### API security

* Authenticated endpoints
* Permission enforcement
* Request validation
* Controlled resource access
* Appropriate error handling
* Pagination and filtering controls

### File upload security

Attachments are treated as untrusted input.

File upload handling will address:

* File type validation
* File size limits
* Safe storage
* Controlled access
* Filename handling
* Prevention of executable uploads

### Production security

Production configuration will address:

* Secret management
* Secure environment variables
* HTTPS
* Database access restrictions
* Redis access restrictions
* Secure application configuration
* Logging and monitoring

---

## Technology Stack

| Category              | Technology                                   |
| --------------------- | -------------------------------------------- |
| Backend               | Python / Django                              |
| API                   | Django REST Framework                        |
| Database              | PostgreSQL                                   |
| ORM                   | Django ORM                                   |
| Authentication        | Django REST Framework Authentication         |
| Authorization         | DRF Permissions / Object-Level Authorization |
| Background Processing | Celery                                       |
| Task Broker           | Redis                                        |
| Scheduled Tasks       | Celery Beat                                  |
| Testing               | Pytest / pytest-django                       |
| API Documentation     | OpenAPI / Swagger UI / ReDoc                 |
| Code Quality          | Ruff                                         |
| Git Hooks             | pre-commit                                   |
| Dependency Management | uv                                           |
| Containers            | Docker / Docker Compose                      |
| CI/CD                 | GitHub Actions                               |
| Cloud                 | AWS                                          |

---

## Local Development

The project uses Docker-based infrastructure to provide a consistent development environment.

### Prerequisites

The development environment will require:

* Git
* Python
* uv
* Docker
* Docker Compose

### Clone the repository

```bash
git clone https://github.com/Johnkm09/helpdesk-ticketing-system.git
cd helpdesk-ticketing-system
```

### Create the environment

Environment configuration will be based on:

```text
.env.example
```

Copy the example environment file into the local environment configuration and provide the required development values.

### Start infrastructure

The intended development workflow will use:

```bash
docker compose up
```

This will run the required application and supporting services.

### Database migrations

Django migrations will be applied using:

```bash
python manage.py migrate
```

### Run tests

```bash
pytest
```

### Run code quality checks

```bash
ruff check .
```

The exact setup and commands will be maintained as the project implementation progresses.

---

## Project Status

The project is currently in the **Project Foundation** phase.

Planned development phases include:

1. Project foundation and Git workflow
2. Python and Django environment
3. Authentication and users
4. Ticket management
5. Ticket lifecycle and assignment
6. Comments and attachments
7. Audit history
8. Redis and Celery background processing
9. Notifications and automated workflows
10. Reporting
11. Testing and code quality
12. CI/CD
13. Production readiness
14. AWS deployment

The README will be updated as features and infrastructure are implemented.

---

## License

This project is currently developed as a portfolio and engineering demonstration project.
