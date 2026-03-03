#!/usr/bin/env python3
"""
BM25 Search Algorithm for Aesthetic Eye
Lightweight ranking algorithm for CSV-based knowledge search.
"""

import math
import re
from collections import Counter


class BM25:
    """BM25 ranking algorithm for text search."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 with tuning parameters.

        Args:
            k1: Term frequency saturation parameter (1.2-2.0 typical)
            b: Length normalization parameter (0.75 typical)
        """
        self.k1 = k1
        self.b = b
        self.documents = []
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.idf = {}
        self.doc_term_freqs = []

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into lowercase words.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens (words with 2+ characters)
        """
        if not text:
            return []
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if len(t) >= 2]

    def fit(self, documents: list[str]) -> None:
        """
        Build index from documents.

        Args:
            documents: List of document strings to index
        """
        self.documents = documents
        n_docs = len(documents)

        if n_docs == 0:
            return

        # Tokenize all documents
        tokenized_docs = [self.tokenize(doc) for doc in documents]

        # Calculate document lengths
        self.doc_lengths = [len(doc) for doc in tokenized_docs]
        self.avg_doc_length = sum(self.doc_lengths) / n_docs if n_docs > 0 else 0

        # Calculate term frequencies per document
        self.doc_term_freqs = [Counter(doc) for doc in tokenized_docs]

        # Calculate IDF for each term
        doc_freq = Counter()
        for doc in tokenized_docs:
            doc_freq.update(set(doc))

        for term, df in doc_freq.items():
            # IDF with smoothing
            self.idf[term] = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)

    def score(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """
        Score documents against a query.

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of (doc_index, score) tuples, sorted by score descending
        """
        query_tokens = self.tokenize(query)

        if not query_tokens or not self.documents:
            return []

        scores = []

        for idx, doc_tf in enumerate(self.doc_term_freqs):
            score = 0.0
            doc_len = self.doc_lengths[idx]

            for term in query_tokens:
                if term not in self.idf:
                    continue

                tf = doc_tf.get(term, 0)
                idf = self.idf[term]

                # BM25 formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_length))
                score += idf * (numerator / denominator) if denominator > 0 else 0

            if score > 0:
                scores.append((idx, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]


def search_csv_data(rows: list[dict], query: str, search_columns: list[str], top_k: int = 5) -> list[dict]:
    """
    Search CSV data using BM25.

    Args:
        rows: List of dictionaries (CSV rows)
        query: Search query
        search_columns: Column names to search in
        top_k: Number of results to return

    Returns:
        List of matching rows with scores
    """
    # Build searchable text from specified columns
    documents = []
    for row in rows:
        text_parts = [str(row.get(col, '')) for col in search_columns if col in row]
        documents.append(' '.join(text_parts))

    # Run BM25 search
    bm25 = BM25()
    bm25.fit(documents)
    results = bm25.score(query, top_k)

    # Return matching rows with scores
    return [{'row': rows[idx], 'score': score} for idx, score in results]


if __name__ == '__main__':
    # Quick test
    test_docs = [
        "glassmorphism dark mode design style",
        "brutalism bold typography minimal",
        "neumorphism soft shadows light colors",
        "flat design simple clean modern",
    ]

    bm25 = BM25()
    bm25.fit(test_docs)

    results = bm25.score("dark mode glass", top_k=3)
    print("Query: 'dark mode glass'")
    for idx, score in results:
        print(f"  [{score:.2f}] {test_docs[idx]}")
