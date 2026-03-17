# Bookstore Management System - Spring Boot Edition

## 🚀 Overview
This is a modernized version of the Group7 Bookstore Management System, rebuilt using **Spring Boot**. It retains the original console-based user interface but replaces the underlying architecture with industry-standard technologies like **Spring Data JPA**, **Hibernate**, and **Dependency Injection**.

## ✨ Features
- **Console UI**: Familiar menu-driven interface.
- **Spring Boot**: Auto-configuration and dependency management.
- **Spring Data JPA**: Repository pattern for database access (no more manual DAOs).
- **Hibernate**: ORM handling.
- **MySQL Database**: Persistent storage.
- **Transaction Management**: Key operations are transactional.

## 🛠️ Technology Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| Java | 17 | Programming Language |
| Spring Boot | 3.1.5 | Framework |
| Spring Data JPA | 3.x | Data Access Layer |
| Hibernate | 6.x | ORM Provider |
| MySQL Driver | 8.x | Database Connectivity |
| Lombok | 1.18 | Boilerplate Reduction |

## 📋 Prerequisites
- JDK 17 or higher
- Maven 3.x
- MySQL Database running locally

## ⚙️ Configuration
The database configuration is located in `src/main/resources/application.properties`.

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/bookstore_db
spring.datasource.username=root
spring.datasource.password=root
spring.jpa.hibernate.ddl-auto=update
```
**Make sure to update the username/password to match your local MySQL setup.**

## 🏃 parameters to Run

### VS Code
1. Open the folder `Group7_BookStore_Advance_Java_SpringBoot` in VS Code.
2. Wait for the Java extensions to load.
3. Open `src/main/java/com/group7/bookstore/BookstoreApplication.java`.
4. Click "Run" or "Debug" above the `main` method.

### IntelliJ IDEA
1. Open the folder `Group7_BookStore_Advance_Java_SpringBoot` as a Project.
2. Maven should auto-reload. If not, right-click `pom.xml` -> Maven -> Reload Project.
3. Run `BookstoreApplication.java`.

### Command Line
```bash
mvn spring-boot:run
```

## 🗄️ Database Setup
The application is configured to automatically create/update the schema (`spring.jpa.hibernate.ddl-auto=update`).
You just need to ensure the database exists:
```sql
CREATE DATABASE bookstore_db;
```

## 🤝 Comparison: Spring Boot vs Original
| Feature | Original (Advanced Java) | Spring Boot Edition |
|---------|-------------------------|---------------------|
| **Boilerplate** | High (Manual DAOs, EntityManager) | Low (Interfaces & Annotations) |
| **Config** | persistence.xml (Manual) | application.properties (Auto) |
| **Wiring** | Manual `new Service()` | `@Autowired` Dependency Injection |
| **Server** | N/A (Console App) | Embedded Tomcat (Disabled for console usage) |
