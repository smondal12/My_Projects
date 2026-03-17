package com.group7.bookstore.repository;

import com.group7.bookstore.entity.Book;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {

    // Custom query to fetch books with their authors eagerly
    @Query("SELECT b FROM Book b JOIN FETCH b.author")
    List<Book> findAllWithAuthors();

    // Case-insensitive search by title (partial match)
    List<Book> findByTitleContainingIgnoreCase(String title);

    // Find books by author ID
    List<Book> findByAuthorId(Long authorId);

    // Custom query to update price
    @Modifying
    @Query("UPDATE Book b SET b.price = :price WHERE b.id = :id")
    int updatePrice(Long id, BigDecimal price);
}
