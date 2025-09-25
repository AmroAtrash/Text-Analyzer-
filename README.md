Text Analyzer Project By Amro Atrash

Overview

The Text Analyzer is a Python project designed to process and analyze text data efficiently.
It uses object-oriented programming (OOP) principles with a strong focus on inheritance and modularity, making the codebase scalable, testable, and easy to maintain.

The project is divided into multiple tasks, each handling a specific aspect of text analysis, such as:

Preprocessing and cleaning text.

Counting sequences of words (k-sequences).

Building co-occurrence graphs of people.

Finding direct and indirect connections between people in a text corpus.

Search engine functionality for querying specific patterns.

This project simulates real-world text analytics, similar to applications in NLP, knowledge graph building, and relationship analysis.

Features / Extensions
1. Preprocessing Extension

Cleans text by:

Lowercasing and tokenizing sentences.

Removing stopwords and punctuation.

Standardizing names and alternate nicknames.

Prepares text for downstream tasks such as counting and graph construction.

2. Graph-Based Connection Analysis

Uses a sliding window algorithm to build graphs representing co-occurrences of people in nearby sentences.

Models relationships between individuals based on how often they appear together in the text.

Useful for building social network graphs from raw text.

3. Path-Finding Extension

Implements two fundamental graph algorithms:

BFS (Breadth-First Search): Detects indirect paths between people.

DFS (Depth-First Search): Finds fixed-length paths between entities.

Analyzes hidden or indirect relationships in the network.

4. Query-Based Search

Implements a basic search engine to query specific patterns or k-sequences.

Enables O(1) search performance for frequent queries.

Class Structure & OOP Design

The project is built using class-based design, emphasizing inheritance to maximize code reuse and modularity.

Core Classes
1. BaseGraph (Parent Class)

Responsible for core graph-building logic:

Stores edges and constructs adjacency lists.

Applies thresholds to filter low-frequency connections.

2. IndirectConnectionFinder (Inherits from BaseGraph)

Uses BFS to check whether two people are connected.

Supports both direct and indirect relationship detection.

3. FindConnection (Inherits from BaseGraph)

Implements DFS to search for paths of exact length K.

Evaluates runtime efficiency for different path lengths.

4. Preprocessor

Cleans and tokenizes sentences.

Removes unnecessary words and standardizes entity names.

5. SequenceCounter

Extracts and counts k-sequences (consecutive word groups).

Optimized for handling very large datasets.

6. BasicSearchEngine

Searches for specific terms or sequences in the processed text.

Supports user-defined query conditions.

Algorithms Used
Algorithm	Purpose
Sliding Window	Detect co-occurrences of people in nearby sentences.
Breadth-First Search (BFS)	Find indirect connections between individuals.
Depth-First Search (DFS)	Find fixed-length paths between nodes.
Tokenization & Stopword Removal	Text preprocessing for clean inputs.
Sorting & Hashing	Optimize lookups for people, names, and sequences.
Why This Approach

I chose graph-based analysis and OOP with inheritance to:

Promote code reusability and scalability.

Allow efficient handling of large text datasets.

Apply classic algorithms like BFS and DFS, which are well-suited for relationship exploration in text.

Ensure that each module remains modular, testable, and easy to extend for future improvements.

Quick Start

1. Run Preprocessing (Task 1)
python main.py -t 1 -s Q1_examples/example_1/sentences.csv \
-n Q1_examples/example_1/people.csv -r REMOVEWORDS.csv

2. Count K-Sequences (Task 2)
python main.py -t 2 --maxk 3 -s Q2_examples/example_1/sentences.csv -r REMOVEWORDS.csv

3. Build Graph Connections (Task 6)
python main.py -t 6 -s Q6_examples/example_1/sentences.csv \
-n Q6_examples/example_1/people.csv -r REMOVEWORDS.csv \
--windowsize 4 --threshold 2

Input Files
File	Description
sentences.csv	Contains raw sentences for analysis.
people.csv	List of names and nicknames to track.
remove_words.csv	Stopwords to exclude during preprocessing.
Output Format

All outputs are in JSON format, printed to the console.

Example Output (Task 3: Counting Mentions)
{
  "Question 3": {
    "Name Mentions": [
      ["harry potter", 5],
      ["hermione granger", 3]
    ]
  }
}
