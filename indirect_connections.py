import json
from typing import List
from finding_connection_between_people import BaseGraph


class IndirectConnectionFinder(BaseGraph):
    """Class for finding indirect connections between people."""
    def __init__(self, sentences: List[List[str]], names: List[List[str]], window_size: int,
                 people_connections: List[List[str]], threshold: int, maximal_distance: int, task_number: str):
        """
        Initializes the IndirectConnectionFinder class.
        Args:
            sentences (List[List[str]]): Tokenized sentences.
            names (List[List[str]]): List of people’s names and aliases.
            window_size (int): Number of sentences to consider together as a window.
            people_connections (List[List[str]]): Pairs of people whose indirect connection needs checking.
            threshold (int): Minimum connection strength required to form an edge.
            maximal_distance (int): Maximum number of connections allowed between two people.
            task_number (str): Task identifier.
        """
        super().__init__(sentences, names, window_size, threshold, task_number)  # Inherit BaseGraph methods
        self.people_connections: List[List[str]] = people_connections  # Pairs of people to check
        self.max_dist: int = maximal_distance  # Maximum allowed path length

    def bfs_check_connection(self, start: str, target: str) -> bool:
        try:
            if start == target:
                return True  # If the start and target are the same, they are trivially connected.
            queue = [(start, 0)]  # BFS queue, storing (current person, current depth)
            visited = {start}  # Set to keep track of visited nodes to avoid cycles
            while queue:
                current, depth = queue.pop(0)  # Remove the first item (FIFO behavior)
                # If the current depth exceeds max_dist, stop further exploration
                if depth > self.max_dist:
                    continue
                # Explore all neighbors in the graph
                for neighbor in self.graph.get(current, []):
                    if neighbor == target:
                        return True  # Found a valid connection
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))  # Add to queue with incremented depth
                        visited.add(neighbor)  # Mark as visited
            return False  # No valid path found within max_dist
        except Exception as e:
            print("Error during bfs_check_connection:", str(e))
            return False

    def check_indirect_connections(self) -> None:
        """
        Checks if person pairs are connected in the graph (either directly or indirectly).
        Uses `bfs_check_connection` to determine connectivity.
        """
        try:
            # Ensure the graph is built before performing searches
            self.build_graph()
            # Validate that the graph structure is correctly initialized
            if not hasattr(self, "graph") or not isinstance(self.graph, dict):
                raise ValueError("Graph was not built correctly.")
            results = []
            # Iterate through each pair of people and check their connection
            for person1, person2 in self.people_connections:
                sorted_pair = sorted([person1, person2])  # Sort pair to maintain consistency
                connected = self.bfs_check_connection(sorted_pair[0], sorted_pair[1])  # Perform BFS search
                results.append([sorted_pair[0], sorted_pair[1], connected])
            # Sort results alphabetically for consistent output
            results.sort(key=lambda x: (x[0], x[1]))
            # Format the output in JSON structure
            output = {
                "Question " + self.task_number: {
                    "Pair Matches": results
                }
            }
            # Print results in JSON format
            print(json.dumps(output, indent=4))
        except Exception as e:
            print("Error during check_indirect_connections:", str(e))
