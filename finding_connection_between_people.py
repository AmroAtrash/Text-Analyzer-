import json
from typing import List, Tuple, Dict
from collections import defaultdict


class BaseGraph:
    def __init__(self, sentences: List[List[str]], names: List[List[str]], window_size: int,
                 threshold: int, task_number: str):
        """
        Initializes the BaseGraph object.
        Args:
            sentences (List[List[str]]): Preprocessed tokenized sentences.
            names (List[List[str]]): Names and aliases of people.
            window_size (int): Size of the sliding window for detecting relationships.
            threshold (int): Minimum occurrence threshold for connections to be valid.
            task_number (str): Task identifier.
        Attributes:
            edges (Dict[Tuple[str, str], int]): Stores relationship counts between people.
            graph (Dict[str, List[str]]): Adjacency list representation of valid connections.
        """
        self.sentences: List[List[str]] = sentences
        self.names: Dict[str, List[str]] = self.names_to_dict(names)
        self.window_size: int = window_size
        self.threshold: int = threshold
        self.edges: Dict[Tuple[str, str], int] = defaultdict(int)  # Dictionary for weighted edges
        self.task_number: str = task_number
        self.graph: Dict[str, List[str]] = defaultdict(list)  # Adjacency list representation

    @staticmethod
    def names_to_dict(names: List[List[str]]) -> Dict[str, List[str]]:
        """
        Converts a list of names and aliases into a dictionary format.
        Args:
            names (List[List[str]]): List of names and their aliases.
        Returns:
            Dict[str, List[str]]: A mapping of primary names to their aliases.
        Explanation:
        - The first element of each inner list is considered the primary name.
        - Subsequent elements are considered aliases.
        """
        try:
            return {
                ' '.join(name_group[0]): [' '.join(other_name) for other_name in name_group[1:][0]]
                for name_group in names
            }
        except Exception as e:
            print("Error during names_to_dict: " + str(e))
            return {}

    def check_person_in_window(self, window: List[List[str]], person: str, aliases: List[str]) -> bool:
        """
        Checks if a person or any of their aliases appear in the given window of sentences.
        Args:
            window (List[List[str]]): A window of tokenized sentences.
            person (str): The primary name.
            aliases (List[str]): List of alternative names.
        Returns:
            bool: True if the person or any alias is found in the window, else False.
        Explanation:
        - Flattens the window into a set of unique words for fast lookup.
        - Uses set intersection to check if any variant of the name is present.
        - Improves efficiency by avoiding unnecessary iteration over tokens.
        """
        try:
            all_variants = set(person.split()).union(set(aliases))  # Combine name and aliases
            flattened_window = {word.lower() for sentence in window for word in sentence}  # Flatten window
            return bool(all_variants & flattened_window)  # Check for intersection
        except Exception as e:
            print("Error during check_person_in_window: " + str(e))
            return False

    def count_connections(self) -> None:
        """
        Counts connections between people based on overlapping sentence windows.
        Explanation:
        - Uses a sliding window to track relationships appearing together in a sentence group.
        - Stores relationships in `edges` with frequency counts.
        Efficiency:
        - Uses a dictionary to store and count relationships, making lookups and updates O(1).
        - Processes the dataset in O(N * W) time, where:
          - N is the number of sentences.
          - W is the window size.
        """
        try:
            num_sentences = len(self.sentences)
            for start_idx in range(num_sentences - self.window_size + 1):
                window = self.sentences[start_idx:start_idx + self.window_size]
                people_in_window = set()
                # Identify all unique people appearing in the current window
                for person, aliases in self.names.items():
                    if self.check_person_in_window(window, person, aliases):
                        people_in_window.add(person)
                # Count co-occurrences of people in the same window
                for person1 in people_in_window:
                    for person2 in people_in_window:
                        if person1 < person2:  # Avoid duplicate pairs
                            self.edges[(person1, person2)] += 1
        except Exception as e:
            print("Error during count_connections: " + str(e))

    def filter_edges(self) -> List[Tuple[str, str]]:
        """
        Filters edges based on the threshold value.
        Returns:
            List[Tuple[str, str]]: A list of valid edges meeting the threshold.
        Explanation:
        - Only includes edges where the relationship frequency is at least `threshold`.
        - Ensures that weak relationships are excluded from the final graph.
        """
        try:
            return [pair for pair, count in self.edges.items() if count >= self.threshold]
        except Exception as e:
            print("Error during filter_edges: " + str(e))
            return []

    def build_graph(self) -> None:
        try:
            self.count_connections()  # Identify all connections
            valid_edges = self.filter_edges()  # Apply threshold filter
            for p1, p2 in valid_edges:
                self.graph[p1].append(p2)
                self.graph[p2].append(p1)  # Ensure bidirectional edges
        except Exception as e:
            print("Error during build_graph: " + str(e))

    def export_results(self) -> None:
        """
        Exports the graph connections in JSON format.
        Output Format:
        {
            "Question <task_number>": {
                "Pair Matches": [
                    ["person1", "person2"],
                    ["person3", "person4"]
                ]
            }
        }
        Explanation:
        - Outputs the final graph connections in a structured format.
        - Uses `json.dumps()` for readable formatting.
        """
        try:
            output = {
                "Question " + self.task_number: {
                    "Pair Matches": [
                        [p1.split(), p2.split()]
                        for p1, p2 in sorted(self.filter_edges())
                    ]
                }
            }
            print(json.dumps(output, indent=4))
        except Exception as e:
            print("Error during export_results: " + str(e))
