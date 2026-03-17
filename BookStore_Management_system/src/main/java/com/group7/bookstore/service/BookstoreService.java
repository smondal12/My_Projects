package com.group7.bookstore.service;

import com.group7.bookstore.entity.Author;
import com.group7.bookstore.entity.Book;
import com.group7.bookstore.repository.AuthorRepository;
import com.group7.bookstore.repository.BookRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class BookstoreService {

    private final BookRepository bookRepository;
    private final AuthorRepository authorRepository;

    // ==================== Book Operations ====================

    public List<Book> listAllBooks() {
        return bookRepository.findAllWithAuthors();
    }

    @Transactional
    public boolean addNewBook(String title, BigDecimal price, int quantity, String authorName, String authorCountry) {
        try {
            if (price.compareTo(BigDecimal.ZERO) < 0) {
                log.error("VALIDATION: Price cannot be negative");
                return false;
            }
            if (quantity < 0) {
                log.error("VALIDATION: Quantity cannot be negative");
                return false;
            }

            // Find or create author
            Author author = authorRepository.findByName(authorName)
                    .orElseGet(() -> {
                        log.info("Author '{}' not found. Creating new author.", authorName);
                        return authorRepository.save(new Author(authorName, authorCountry));
                    });

            Book book = new Book(title, price, quantity, author);
            bookRepository.save(book);

            log.info("Book added successfully: {}", title);
            return true;
        } catch (Exception e) {
            log.error("Error adding book", e);
            return false;
        }
    }

    @Transactional
    public boolean updateBookPrice(Long bookId, BigDecimal newPrice) {
        try {
            int updatedCount = bookRepository.updatePrice(bookId, newPrice);
            return updatedCount > 0;
        } catch (Exception e) {
            log.error("Error updating book price", e);
            return false;
        }
    }

    public boolean removeBook(Long bookId) {
        try {
            if (bookRepository.existsById(bookId)) {
                bookRepository.deleteById(bookId);
                return true;
            }
            return false;
        } catch (Exception e) {
            log.error("Error deleting book", e);
            return false;
        }
    }

    public List<Book> searchBooksByTitle(String title) {
        return bookRepository.findByTitleContainingIgnoreCase(title);
    }

    public List<Book> findBooksByAuthor(Long authorId) {
        return bookRepository.findByAuthorId(authorId);
    }

    // ==================== Author Operations ====================

    public List<Author> listAllAuthors() {
        return authorRepository.findAll();
    }

    @Transactional
    public boolean addNewAuthor(String name, String country) {
        try {
            authorRepository.save(new Author(name, country));
            return true;
        } catch (Exception e) {
            log.error("Error adding author", e);
            return false;
        }
    }

    @Transactional
    public boolean updateAuthor(Long authorId, String newName, String newCountry) {
        try {
            Optional<Author> authorOpt = authorRepository.findById(authorId);
            if (authorOpt.isPresent()) {
                Author author = authorOpt.get();
                author.setName(newName);
                author.setCountry(newCountry);
                authorRepository.save(author);
                return true;
            }
            return false;
        } catch (Exception e) {
            log.error("Error updating author", e);
            return false;
        }
    }

    @Transactional
    public boolean deleteAuthor(Long authorId) {
        try {
            // In JPA with CascadeType.ALL on Author.books, deleting the author
            // will automatically delete all their books. This matches the behavior
            // requested in the original project (though the original manually disassociated
            // them).
            // To faithfully replicate "books remain without an author" (if that was the
            // intent),
            // we would need to set book.author = null.
            //
            // Reviewing original code: `bookDao.disassociateBooksFromAuthor(authorId)`
            // So we should replicate that.

            Optional<Author> authorOpt = authorRepository.findById(authorId);
            if (authorOpt.isPresent()) {
                Author author = authorOpt.get();

                // Disassociate books
                for (Book book : author.getBooks()) {
                    book.setAuthor(null);
                    bookRepository.save(book);
                }

                // Now verify the list is cleared to prevent cascade delete issues
                author.getBooks().clear();
                authorRepository.save(author); // flush changes

                authorRepository.deleteById(authorId);
                return true;
            }
            return false;
        } catch (Exception e) {
            log.error("Error deleting author", e);
            return false;
        }
    }
}
