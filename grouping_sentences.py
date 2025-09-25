import json
from typing import List, Dict, Set
import time


class SentenceGrouping:
    def __init__(self, sentences: List[List[str]], threshold: int, task_number: str):
        """
        Initializes the SentenceGrouping class.
        Args:
            sentences (List[List[str]]): Tokenized sentences from the dataset.
            threshold (int): The minimum number of shared words to form a connection.
            task_number (str): Task number identifier.
        Attributes:
            graph (Dict[int, List[int]]): Adjacency list representation of sentence connections.
        """
        self.sentences: List[List[str]] = sentences
        self.threshold: int = threshold
        self.graph: Dict[int, List[int]] = {}
        self.task_number: str = task_number

    def build_graph(self) -> None:
        try:
            num_sentences = len(self.sentences)
            self.graph = {i: [] for i in range(num_sentences)}  # Initialize graph with empty adjacency lists.
            for i in range(num_sentences):
                for j in range(i + 1, num_sentences):
                    shared_words = set(self.sentences[i]).intersection(set(self.sentences[j]))  # Compute word overlap.
                    if len(shared_words) >= self.threshold:
                        self.graph[i].append(j)  # Connect sentence i to j.
                        self.graph[j].append(i)  # Connect sentence j to i (undirected).
        except Exception as e:
            print("Error in build_graph:", e)

    def _dfs(self, node: int, visited: Set[int]) -> Set[int]:
        """
        Performs Depth-First Search (DFS) to collect all connected nodes in a group.
        Args:
            node (int): The starting node for DFS.
            visited (Set[int]): A set to track visited nodes.
        Returns:
            Set[int]: The connected group of nodes.
        Explanation:
        - Uses an **explicit stack** instead of recursion (avoids stack overflow for large graphs).
        - Ensures each node is visited only once.
        Efficiency:
        - Time Complexity: **O(V + E)**, where `V` is the number of sentences and `E` is the number of connections.
        - Space Complexity: **O(V)** (worst case where all sentences form one large cluster).
        """
        group = set()
        stack = [node]
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                group.add(current)
                stack.extend(self.graph[current])  # Push unvisited neighbors to stack.
        return group

    def find_groups(self) -> List[Set[int]]:
        """
        Identifies groups of connected sentences using DFS traversal.
        Explanation:
        - Iterates over all sentence indices, starting a DFS when an unvisited sentence is found.
        - Each DFS traversal captures a complete connected component.
        Efficiency:
        - **O(V + E)**, since it performs DFS on each connected component.
        """
        try:
            visited: Set[int] = set()
            groups = []
            for node in range(len(self.sentences)):
                if node not in visited:
                    group = self._dfs(node, visited)  # Perform DFS for unvisited sentence.
                    groups.append(group)
            return groups
        except Exception as e:
            print("Error in find_groups:", e)
            return []

    def get_sentence_groups(self) -> Dict:
        """
        Groups sentences based on similarity and formats the output.
        Explanation:
        - Calls `build_graph()` to create the adjacency list.
        - Calls `find_groups()` to retrieve clusters.
        - Sorts groups for consistency.
        Efficiency:
        - Sorting sentences **O(N log N)** (ensures predictable output order).
        - Constructing the final result **O(N)**.
        Edge Cases:
        - If no sentences share enough words, each sentence is its own group.
        """
        try:
            self.build_graph()
            groups = self.find_groups()
            # Sorting groups:
            # 1. Sort by group size.
            # 2. If sizes are equal, sort sentences lexicographically.
            sorted_groups = sorted(groups, key=lambda g: (len(g), sorted(self.sentences[i] for i in g)))
            result: Dict[str, Dict[str, List[List]]] = {"Question " + self.task_number: {"group Matches": []}}
            for index, group in enumerate(sorted_groups, 1):
                sorted_sentences = sorted([self.sentences[i] for i in group])
                result["Question " + self.task_number]["group Matches"].append(
                    ["Group " + str(index), sorted_sentences]
                )
            return result
        except Exception as e:
            print("Error in get_sentence_groups:", e)
            return {"Question " + self.task_number: {"group Matches": []}}

    def export_results(self) -> None:
        """
        Prints the final sentence groups in JSON format.
        - Calls `get_sentence_groups()` to retrieve the grouping structure.
        - Uses `json.dumps()` to format output.
        Efficiency:
        - The function is mainly **O(N log N)** due to sorting.
        """
        try:
            result = self.get_sentence_groups()
            print(json.dumps(result, indent=4))
        except Exception as e:
            print("Error in export_results:", e)

    def analyze_runtime(self) -> Dict:
        """
        Measures and analyzes the runtime of `get_sentence_groups()` for different values of `T`.
        Returns:
            Dict[int, float]: Mapping of `T` values to their respective runtime durations.
        Explanation:
        - Measures execution time for different values of the threshold.
        - Helps analyze how `T` impacts clustering complexity.
        Efficiency:
        - Runs **O(N^2 * M)** operations multiple times.
        - Increases time complexity but provides insights on performance scaling.
        """
        runtimes = {}
        for T in range(6):  # Measure for different threshold values.
            self.threshold = T
            start_time = time.time()
            _ = self.get_sentence_groups()
            end_time = time.time()
            runtimes[T] = end_time - start_time  # Store execution time.
        return runtimes
