# 📘 Technical Implementation Guide (Spring Boot)

This document explains the technical details of the Spring Boot implementation of the Bookstore Management System.

## 🏗️ Architecture
The application follows a standard layered architecture managed by the Spring Container (IoC).

1.  **Presentation Layer**: `ConsoleRunner.java`
    *   Implements `CommandLineRunner`.
    *   This interface tells Spring Boot: "Run this code after the application context is loaded."
    *   It handles all `System.out` and `Scanner` logic.

2.  **Service Layer**: `BookstoreService.java`
    *   Annotated with `@Service`.
    *   Contains the core business logic (e.g., "Check if author exists before adding book").
    *   Annotated with `@Transactional` where needed to ensure data integrity (ACID properties).

3.  **Repository Layer**: `BookRepository` / `AuthorRepository`
    *   These interfaces extend `JpaRepository<T, ID>`.
    *   **Magic**: We do NOT write the implementation code. Spring Data JPA generates the SQL and JDBC code automatically at runtime based on the method names (e.g., `findByTitleContainingIgnoreCase`).

4.  **Domain Layer**: `Book` / `Author`
    *   JPA Entities annotated with `@Entity`.
    *   Uses Lombok (`@Data`) to automatically generate Getters, Setters, and `toString()` methods, keeping the code clean.

## 🔑 Key Technical Decisions

### 1. Dependency Injection
Instead of creating objects manually (`BookDao dao = new BookDao()`), we let Spring inject them.
```java
@Component
@RequiredArgsConstructor
public class ConsoleRunner {
    private final BookstoreService service; // Injected by Spring
}
```
The `@RequiredArgsConstructor` annotation (from Lombok) creates a constructor that Spring uses to inject the dependencies.

### 2. Transaction Management
In the previous version, transactions were manual (`em.getTransaction().begin()`, `commit()`, `rollback()`).
In Spring Boot, we simply add `@Transactional` to a method. If an exception occurs, Spring automatically rolls back the transaction.

### 3. Cascading
The relationship between Author and Book handles deletions automatically.
*   Deleting an **Author** will disassociate their books (handled manually in logic to mirror the original requirement).
*   Deleting a **Book** just removes the record.

## 🌍 Global Settings for IDEs

### IntelliJ IDEA
*   **Lombok Plugin**: Ensure the Lombok plugin is installed and "Annotation Processing" is enabled in Settings.
*   **JDK**: Project structure should be set to JDK 17.

### VS Code
*   **Extension Pack for Java**: Install the Microsoft Java extension pack.
*   **Lombok**: The Red Hat Java extension supports Lombok by default, but you may need to enable annotation processing if prompted.

## ❓ FAQ for the Developer

**Q: Where is `persistence.xml`?**
A: It's gone. Spring Boot configures the `EntityManagerFactory` automatically based on the settings in `application.properties`.

**Q: Where are the DAO classes?**
A: Replaced by *Repository Interfaces*. We only declare methods; Spring implements them.

**Q: How do I change the database?**
A: Just change the URL and Driver in `application.properties`. No code changes required.
