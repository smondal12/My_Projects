package com.group7.bookstore;

import com.group7.bookstore.entity.Author;
import com.group7.bookstore.entity.Book;
import com.group7.bookstore.service.BookstoreService;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;
import java.util.Scanner;

@Component
@RequiredArgsConstructor
public class ConsoleRunner implements CommandLineRunner {

    private final BookstoreService service;
    private final Scanner scanner = new Scanner(System.in);

    @Override
    public void run(String... args) {
        System.out.println("╔════════════════════════════════════════════════════════╗");
        System.out.println("║  Bookstore Management System - Spring Boot Edition     ║");
        System.out.println("║  Using: Spring Data JPA | Hibernate | Maven            ║");
        System.out.println("╚════════════════════════════════════════════════════════╝");

        runMenu();
    }

    private void runMenu() {
        while (true) {
            printMainMenu();
            int choice = getIntegerInput("Enter your choice: ");

            switch (choice) {
                case 1:
                    handleBookMenu();
                    break;
                case 2:
                    handleAuthorMenu();
                    break;
                case 3:
                    System.out.println("Goodbye!");
                    return; // Exit the loop and the application
                default:
                    System.out.println("Invalid choice. Please enter a number between 1 and 3.");
            }
        }
    }

    private void printMainMenu() {
        System.out.println("\n╔═══════════════════════════╗");
        System.out.println("║      MAIN MENU           ║");
        System.out.println("╠═══════════════════════════╣");
        System.out.println("║ 1. Manage Books          ║");
        System.out.println("║ 2. Manage Authors        ║");
        System.out.println("║ 3. Exit                  ║");
        System.out.println("╚═══════════════════════════╝");
    }

    // --- Book Management ---
    private void handleBookMenu() {
        while (true) {
            System.out.println("\n┌─────────────────────────────────┐");
            System.out.println("│    📚 Book Management Menu      │");
            System.out.println("├─────────────────────────────────┤");
            System.out.println("│ 1. List all books              │");
            System.out.println("│ 2. Add a new book              │");
            System.out.println("│ 3. Update a book's price       │");
            System.out.println("│ 4. Delete a book               │");
            System.out.println("│ 5. Search books by title       │");
            System.out.println("│ 6. Find books by author        │");
            System.out.println("│ 7. Back to Main Menu           │");
            System.out.println("└─────────────────────────────────┘");
            int choice = getIntegerInput("Enter your choice: ");

            switch (choice) {
                case 1:
                    handleListAllBooks();
                    break;
                case 2:
                    handleAddNewBook();
                    break;
                case 3:
                    handleUpdateBookPrice();
                    break;
                case 4:
                    handleDeleteBook();
                    break;
                case 5:
                    handleSearchBookByTitle();
                    break;
                case 6:
                    handleFindBooksByAuthor();
                    break;
                case 7:
                    return;
                default:
                    System.out.println("Invalid choice.");
            }
        }
    }

    // --- Author Management ---
    private void handleAuthorMenu() {
        while (true) {
            System.out.println("\n┌─────────────────────────────────┐");
            System.out.println("│    ✍️ Author Management Menu    │");
            System.out.println("├─────────────────────────────────┤");
            System.out.println("│ 1. List all authors            │");
            System.out.println("│ 2. Add a new author            │");
            System.out.println("│ 3. Update an author            │");
            System.out.println("│ 4. Delete an author            │");
            System.out.println("│ 5. Back to Main Menu           │");
            System.out.println("└─────────────────────────────────┘");
            int choice = getIntegerInput("Enter your choice: ");

            switch (choice) {
                case 1:
                    handleListAllAuthors();
                    break;
                case 2:
                    handleAddNewAuthor();
                    break;
                case 3:
                    handleUpdateAuthor();
                    break;
                case 4:
                    handleDeleteAuthor();
                    break;
                case 5:
                    return;
                default:
                    System.out.println("Invalid choice.");
            }
        }
    }

    // --- Book Handler Methods ---
    private void handleListAllBooks() {
        System.out.println("\n[READ]: Listing all books from the database...");
        List<Book> books = service.listAllBooks();
        if (books.isEmpty()) {
            System.out.println("No books found in the database.");
        } else {
            System.out.println("\nFound " + books.size() + " book(s):");
            books.forEach(System.out::println);
        }
    }

    private void handleAddNewBook() {
        System.out.println("\n[CREATE]: Add a new book");
        String title = getStringInput("Enter book title: ");
        String authorName = getStringInput("Enter author's name: ");
        String authorCountry = getStringInput("Enter author's country: ");
        BigDecimal price = getBigDecimalInput("Enter price: ");
        int quantity = getIntegerInput("Enter quantity: ");

        if (service.addNewBook(title, price, quantity, authorName, authorCountry)) {
            System.out.println("\n✓ SUCCESS: Book added successfully!");
        } else {
            System.out.println("\n✗ FAILURE: Failed to add book. Check error logs for details.");
        }
    }

    private void handleUpdateBookPrice() {
        System.out.println("\n[UPDATE]: Change a book's price");
        long bookId = getLongInput("Enter book ID to update: ");
        BigDecimal newPrice = getBigDecimalInput("Enter the new price: ");

        if (service.updateBookPrice(bookId, newPrice)) {
            System.out.println("✓ Price updated successfully!");
        } else {
            System.out.println("✗ Could not update price for book ID " + bookId + ". It may not exist.");
        }
    }

    private void handleDeleteBook() {
        System.out.println("\n[DELETE]: Delete a book");
        long bookId = getLongInput("Enter book ID to delete: ");

        if (service.removeBook(bookId)) {
            System.out.println("✓ Book deleted successfully!");
        } else {
            System.out.println("✗ Could not delete book with ID " + bookId + ". It may not exist.");
        }
    }

    private void handleSearchBookByTitle() {
        System.out.println("\n[SEARCH]: Search for a book");
        String title = getStringInput("Enter the book title to search for: ");
        List<Book> foundBooks = service.searchBooksByTitle(title);

        if (foundBooks.isEmpty()) {
            System.out.println("No books found with a title containing '" + title + "'.");
        } else {
            System.out.println("\nFound " + foundBooks.size() + " book(s):");
            foundBooks.forEach(System.out::println);
        }
    }

    private void handleFindBooksByAuthor() {
        System.out.println("\n[SEARCH]: Find books by author");
        handleListAllAuthors();
        long authorId = getLongInput("Enter the author ID to see their books: ");
        List<Book> books = service.findBooksByAuthor(authorId);

        if (books.isEmpty()) {
            System.out.println("No books found for this author.");
        } else {
            System.out.println("\nFound " + books.size() + " book(s) for author ID " + authorId + ":");
            books.forEach(System.out::println);
        }
    }

    // --- Author Handler Methods ---
    private void handleListAllAuthors() {
        System.out.println("\n[LIST]: Listing all authors...");
        List<Author> authors = service.listAllAuthors();
        if (authors.isEmpty()) {
            System.out.println("No authors found in the database.");
        } else {
            authors.forEach(System.out::println);
        }
    }

    private void handleAddNewAuthor() {
        System.out.println("\n[CREATE]: Add a new author");
        String name = getStringInput("Enter author's name: ");
        String country = getStringInput("Enter author's country: ");

        if (service.addNewAuthor(name, country)) {
            System.out.println("✓ SUCCESS: Author added!");
        } else {
            System.out.println("✗ FAILURE: Could not add author.");
        }
    }

    private void handleUpdateAuthor() {
        System.out.println("\n[UPDATE]: Update an author");
        handleListAllAuthors();
        long authorId = getLongInput("Enter the ID of the author to update: ");
        String newName = getStringInput("Enter the new name for the author: ");
        String newCountry = getStringInput("Enter the new country for the author: ");

        if (service.updateAuthor(authorId, newName, newCountry)) {
            System.out.println("✓ SUCCESS: Author updated!");
        } else {
            System.out.println("✗ FAILURE: Could not update author. ID may not exist.");
        }
    }

    private void handleDeleteAuthor() {
        System.out.println("\n[DELETE]: Delete an author");
        System.out.println("⚠️  WARNING: Deleting an author will disassociate their books.");
        handleListAllAuthors();
        long authorId = getLongInput("Enter the ID of the author to delete: ");

        if (service.deleteAuthor(authorId)) {
            System.out.println("✓ SUCCESS: Author deleted!");
        } else {
            System.out.println("✗ FAILURE: Could not delete author. ID may not exist.");
        }
    }

    // --- Input Helper Methods ---
    private String getStringInput(String prompt) {
        String input;
        while (true) {
            System.out.print(prompt);
            input = scanner.nextLine().trim();
            if (input != null && !input.isEmpty()) {
                return input;
            }
            System.out.println("Input cannot be empty. Please try again.");
        }
    }

    private int getIntegerInput(String prompt) {
        while (true) {
            try {
                System.out.print(prompt);
                String line = scanner.nextLine();
                return Integer.parseInt(line);
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a whole number.");
            }
        }
    }

    // Added for Long IDs
    private long getLongInput(String prompt) {
        while (true) {
            try {
                System.out.print(prompt);
                String line = scanner.nextLine();
                return Long.parseLong(line);
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a whole number.");
            }
        }
    }

    private BigDecimal getBigDecimalInput(String prompt) {
        while (true) {
            try {
                System.out.print(prompt);
                return new BigDecimal(scanner.nextLine());
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a valid number (e.g., 29.99).");
            }
        }
    }
}
