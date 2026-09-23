\# Contributing



This document defines the development workflow, Git conventions, pull request process, and code review expectations for the Helpdesk Ticketing System (HTS) API.



The project uses a team-based Git workflow where features are developed independently, reviewed through pull requests, validated by automated checks, and merged into the integration branch before production release.



\---



\## Development Workflow



The standard development workflow is:



```text

Task / Issue

&#x20;    ↓

Create Feature Branch from develop

&#x20;    ↓

Implement Feature

&#x20;    ↓

Write / Update Tests

&#x20;    ↓

Run Code Quality Checks

&#x20;    ↓

Commit Changes

&#x20;    ↓

Push Branch

&#x20;    ↓

Open Pull Request

&#x20;    ↓

GitHub Actions / CI

&#x20;    ↓

Code Review

&#x20;    ↓

Merge into develop

```



Production changes follow:



```text

develop

&#x20;  ↓

Production Validation

&#x20;  ↓

Pull Request

&#x20;  ↓

main

&#x20;  ↓

AWS Deployment

```



\---



\## Branch Strategy



The project uses the following branches:



| Branch      | Purpose                              |

| ----------- | ------------------------------------ |

| `main`      | Production-ready code                |

| `develop`   | Integration and staging branch       |

| `feature/\*` | New features and planned development |

| `hotfix/\*`  | Urgent production fixes              |



\### Main



`main` represents the production state of the application.



Direct commits to `main` are not allowed.



Changes reach `main` through a reviewed pull request from `develop` or through an approved hotfix.



\### Develop



`develop` is the integration branch for completed features.



Feature branches are merged into `develop` after code review and successful CI checks.



\### Feature Branches



Feature branches are created from `develop`.



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

```



\### Hotfix Branches



Hotfix branches are created from `main` when an urgent production issue must be corrected.



Example:



```text

hotfix/fix-ticket-closure

```



After the hotfix is merged into `main`, the change must also be merged back into `develop` so the branches remain synchronized.



\---



\## Commit Conventions



Commit messages should be short, clear, and written in the imperative style.



The project uses a simple Conventional Commits format:



```text

type: description

```



Common types:



| Type       | Purpose                                      |

| ---------- | -------------------------------------------- |

| `feat`     | New functionality                            |

| `fix`      | Bug fix                                      |

| `test`     | Tests                                        |

| `docs`     | Documentation                                |

| `refactor` | Code restructuring without changing behavior |

| `chore`    | Tooling or maintenance                       |

| `ci`       | CI/CD changes                                |



Examples:



```text

feat: add ticket assignment service

fix: prevent duplicate ticket closure

test: add ticket lifecycle tests

docs: update API architecture

refactor: separate ticket repository logic

chore: configure pre-commit hooks

ci: add GitHub Actions test workflow

```



Commits should represent logical changes rather than unrelated collections of changes.



\---



\## Pull Requests



All feature changes must be submitted through a pull request.



A pull request should contain:



\* Clear description of the change

\* Related issue or task

\* Tests added or updated

\* Database migrations, when applicable

\* Documentation updates, when applicable

\* Any important implementation or design notes



Before requesting review, the developer should verify that:



```text

Tests pass

Code quality checks pass

No secrets are committed

Database migrations are included when required

Documentation is updated when required

Changes are limited to the intended task

```



\---



\## Code Review



Code review is required before merging changes into `develop` or `main`.



Reviewers should consider:



\* Correctness

\* Business rules

\* Authentication and authorization

\* Customer data isolation

\* Error handling

\* Test coverage

\* Database changes

\* Security

\* Maintainability

\* Performance

\* API consistency

\* Background task behavior

\* Potential side effects



Review comments should focus on improving the implementation and explaining the reason for requested changes.



The author is responsible for addressing review feedback before the pull request is merged.



\---



\## Continuous Integration



Pull requests must pass the project's automated CI checks before merging.



CI will progressively validate:



```text

Install dependencies

&#x20;       ↓

Code quality checks

&#x20;       ↓

Automated tests

&#x20;       ↓

Application/build validation

```



The CI pipeline will be expanded as the project introduces additional tooling and infrastructure.



\---



\## Testing



New functionality should include appropriate automated tests.



Tests may include:



\* Unit tests

\* Service tests

\* Repository tests

\* API tests

\* Permission tests

\* Workflow tests

\* Background task tests

\* Integration tests



Run the test suite locally with:



```powershell

pytest

```



Code quality checks will include:



```powershell

ruff check .

```



Additional commands will be added as the project's development tooling is introduced.



\---



\## Database Changes



Changes to Django models must include the corresponding migration files.



Developers should:



1\. Modify the model.

2\. Generate migrations.

3\. Review the generated migration.

4\. Run the migration locally.

5\. Update relevant tests.

6\. Include the migration in the pull request.



Production database changes must not be performed manually when a Django migration can safely represent the change.



\---



\## Security



Never commit sensitive information to the repository.



This includes:



\* Passwords

\* API keys

\* Tokens

\* Secret keys

\* Database credentials

\* AWS credentials

\* Private certificates

\* Production environment variables



Local configuration should use environment variables and `.env` files.



Sensitive configuration must never be committed to Git.



\---



\## Documentation



Changes that affect architecture, API behavior, configuration, workflows, or developer setup should update the relevant documentation.



Important documentation includes:



\* `README.md`

\* API documentation

\* Architecture documentation

\* Development instructions

\* Deployment documentation



Documentation should describe the system as it actually exists rather than documenting planned functionality as completed functionality.



\---



\## Definition of Done



A development task is considered complete when:



\* The required functionality is implemented.

\* Business rules are enforced.

\* Appropriate tests are added or updated.

\* Authentication and authorization requirements are satisfied.

\* Database migrations are included when required.

\* Code quality checks pass.

\* Documentation is updated when necessary.

\* CI passes.

\* Code review feedback is addressed.

\* The pull request is approved and merged.



\---



\## Merge Rules



The project follows these rules:



```text

feature/\*  →  develop

hotfix/\*   →  main

develop    →  main

```



Protected branches should not receive direct pushes.



Changes should reach protected branches through pull requests and the required CI/review process.



\---



\## Local Development



Development environment setup and application-specific commands are documented in:



```text

README.md

```



As the project grows, additional development documentation will be added where necessary.



