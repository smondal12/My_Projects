package com.group7.bookstore.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "authors")
@Data
@NoArgsConstructor
@ToString(exclude = "books") // Prevent infinite recursion in toString
public class Author {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "author_id")
    private Long id; // Changed from int to Long for JPA best practices

    @Column(nullable = false, length = 100)
    private String name;

    @Column(length = 50)
    private String country;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Book> books = new ArrayList<>();

    public Author(String name, String country) {
        this.name = name;
        this.country = country;
    }
}
