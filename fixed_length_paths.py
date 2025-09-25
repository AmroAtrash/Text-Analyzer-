import json
from typing import List, Dict
from finding_connection_between_people import BaseGraph
import time


class FindConnection(BaseGraph):
    def __init__(self, sentences: List[List[str]], names: List[List[str]], window_size: int, threshold: int,
                 people_connections: List[List[str]], K: int, task_number: str):
        """
        Initializes the FindConnection object.
        Args:
            sentences (List[List[str]]): Tokenized sentences.
            names (List[List[str]]): Names and aliases.
            window_size (int): Window size for context-based connections.
            threshold (int): Minimum frequency threshold for edges.
            people_connections (List[List[str]]): Pairs of people to check connections for.
            K (int): Fixed length of path to find.
            task_number (str): Task number.
        """
        super().__init__(sentences, names, window_size, threshold, task_number)  # Inherits BaseGraph functionalities
        self.people_connections: List[List[str]] = people_connections
        self.K: int = K  # Fixed path length

    def _build_graph(self) -> None:
        """
        Builds an adjacency list graph from valid edges and ensures all people are included.
        - Uses BaseGraph's `count_connections()` and `filter_edges()` to create edges.
        - Ensures that every person in `people_connections` exists in the graph, even if isolated.
        """
        try:
            self.count_connections()  # Step 1: Build connections based on text data
            valid_edges = self.filter_edges()  # Step 2: Apply threshold filter
            # Step 3: Ensure all individuals from `people_connections` are included
            for person1, person2 in self.people_connections:
                if person1 not in self.graph:
                    self.graph[person1] = []
                if person2 not in self.graph:
                    self.graph[person2] = []
            # Step 4: Add valid edges to adjacency list representation
            for p1, p2 in valid_edges:
                if p2 not in self.graph[p1]:
                    self.graph[p1].append(p2)
                if p1 not in self.graph[p2]:
                    self.graph[p2].append(p1)
        except Exception as e:
            print("Error during _build_graph: " + str(e))

    def dfs_fixed_length_path(self, current: str, target: str, visited: set, depth: int) -> bool:
        """
        Perform Depth-First Search (DFS) to check if a path of exactly length `K` exists.
        Args:
            current (str): Current node being visited.
            target (str): Target node.
            visited (set): Tracks visited nodes to avoid cycles.
            depth (int): Current depth of traversal.
        Returns:
            bool: True if a path of exactly `K` length exists, else False.
        Efficiency:
        - Uses DFS because it efficiently explores paths of fixed length.
        - Stops early if depth exceeds K, preventing unnecessary computation.
        """
        if depth > self.K:  # If path length exceeds K, stop early
            return False
        if current == target and depth == self.K:  # Exact path length match
            return True
        visited.add(current)
        for neighbor in self.graph.get(current, []):  # Explore each neighbor
            if neighbor not in visited:
                if self.dfs_fixed_length_path(neighbor, target, visited, depth + 1):
                    return True
        visited.remove(current)  # Backtrack
        return False

    def check_fixed_length_path(self) -> List[List]:
        """
        Checks if there exists a path of exactly length K between pairs of people.
        Returns:
            List[List]: Each sublist contains [Person1, Person2, True/False]
        Process:
        1. Builds graph if not already built.
        2. Iterates through `people_connections` and checks if a K-length path exists.
        3. Uses DFS to search for the paths.
        """
        try:
            self._build_graph()  # Ensure graph is built
            results = []
            for person1, person2 in self.people_connections:
                person1, person2 = sorted([person1, person2])  # Ensure consistent ordering
                # If either person is missing from the graph, path cannot exist
                if person1 not in self.graph or person2 not in self.graph:
                    results.append([person1, person2, False])
                    continue
                # Perform DFS to check for a fixed-length path
                path_exists = self.dfs_fixed_length_path(person1, person2, set(), 0)
                results.append([person1, person2, path_exists])
            return results
        except Exception as e:
            print("Error in check_fixed_length_path:", e)
            return []

    def export_results(self) -> None:
        """
        Exports results of fixed-length path search in JSON format.
        Output:
        {
            "Question <task_number>": {
                "Pair Matches": [
                    ["person1", "person2", True/False]
                ]
            }
        }
        """
        try:
            output = {
                "Question " + self.task_number: {
                    "Pair Matches": [
                        [p1, p2, result]
                        for p1, p2, result in sorted(self.check_fixed_length_path())
                    ]
                }
            }
            print(json.dumps(output, indent=4))
        except Exception as e:
            print("Error during export_results: " + str(e))

    def analyze_runtime(self) -> Dict:
        """
        Measures and analyzes the runtime of check_fixed_length_path() for different values of K.
        Returns:
            Dict: {K: runtime_in_seconds}
        Explanation:
        - Runs `check_fixed_length_path()` for K in range [0, 5].
        - Measures runtime for each K and stores it in a dictionary.
        - Allows analysis of how increasing path length affects computational cost.
        Expected Outcome:
        - For small K, runtime is fast since few paths are explored.
        - For larger K, runtime increases as DFS explores exponentially more paths.
        """
        runtimes = {}
        for K in range(6):  # Testing for K from 0 to 5
            self.K = K
            start_time = time.time()
            _ = self.check_fixed_length_path()  # Run the path check
            end_time = time.time()
            runtimes[K] = end_time - start_time  # Store execution time
        return runtimes
