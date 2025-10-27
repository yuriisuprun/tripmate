# 🌍 TripMate

TripMate is a **microservice-based travel booking platform** built using modern Java and DevOps technologies.  
It demonstrates how to design, containerize and orchestrate multiple microservices with **Spring Boot 3**, **Java 21**, and **Docker**, following clean architectural and testing practices.

---

## 🚀 Tech Stack

**Backend:**
- Java 21
- Spring Boot 3 (Web, Security, Data JPA, Validation)
- PostgreSQL
- Spring Cloud (Config Server, Eureka, Gateway)

**DevOps & Infrastructure:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- AWS-ready (ECS / RDS compatible)

**Testing:**
- JUnit 5
- Testcontainers (for integration tests)
- Mockito

---

## 🧩 Repository Structure & Design Choice

TripMate is organized as a **monorepo** — meaning all microservices live within a single GitHub repository.

### 🧠 Why One Repository?

While real-world enterprise systems often use separate repositories for each microservice, this project intentionally uses a **monorepo** for practical and demonstrative reasons:

| ✅ Benefit | 💬 Explanation |
|-------------|----------------|
| **Easier to clone and run** | A single `git clone` gives you the entire system. You can spin up all services locally with one `docker compose up`. |
| **Simplified CI/CD** | One GitHub Actions workflow builds and tests all microservices together. |
| **Unified versioning** | Each release tag (e.g., `v1.0.0`) represents a consistent set of microservices. |
| **Shared modules** | Common models and utilities can be reused across services without publishing to a remote package registry. |
| **Better for demonstration** | Reviewers can explore and understand the full microservices architecture in one place. |
| **Fast iteration** | Easier to make coordinated changes (e.g., shared DTOs or API contracts) without syncing multiple repos. |

### 🚀 When to Split Into Multiple Repositories

In large production systems, teams often separate microservices into their own repos to:
- Manage independent release cycles
- Assign different access controls per service
- Reduce build times for unchanged modules
- Support autonomous development teams

For TripMate, however, a **single repo structure** provides the best balance between **clarity, maintainability, and demonstration value**.

---

## 🗂️ Repository Layout

tripmate/
├── auth-service/ # Authentication & JWT service
├── booking-service/ # Trip booking management
├── payment-service/ # Payment handling (mock)
├── notification-service/ # Email / push notifications
├── gateway-service/ # API gateway (Spring Cloud Gateway)
├── config-server/ # Centralized configuration
├── eureka-server/ # Service discovery
├── common-models/ # Shared DTOs and constants
├── docker-compose.yml # Local environment setup
└── pom.xml # Parent Maven configuration