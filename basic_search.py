from typing import List, Dict
import json


class BasicSearchEngine:
    """
    A class to perform keyword sequence (K-seq) searches within sentences.
    - This optimized version precomputes a hash map for fast lookups.
    """
    def __init__(self, k_seq: List[List[str]], sentences: List[List[str]], task_number: str):
        self.k_seq: List[List[str]] = k_seq
        self.sentences: List[List[str]] = sentences
        self.task_number: str = task_number
        self.k_seq_index: Dict[str, set] = {}  # Set to prevent duplicate storage

    def build_index(self) -> None:
        """
        Precomputes a hash map to store all K-seqs and their corresponding sentences.
        This allows for O(1) lookup for any given K-seq.
        """
        try:
            for sentence in self.sentences:
                for k in range(1, len(sentence) + 1):  # Iterate through all possible K-seq lengths
                    for i in range(len(sentence) - k + 1):
                        k_seq = " ".join(sentence[i:i + k])
                        if k_seq not in self.k_seq_index:
                            self.k_seq_index[k_seq] = set()  # Set to prevent duplicates
                        self.k_seq_index[k_seq].add(tuple(sentence))
        except Exception as e:
            print("Error during index building:", str(e))

    def search(self) -> None:
        """
        Search for each K-seq in the precomputed dictionary (O(1) lookup).
        """
        try:
            self.build_index()  # Precompute index for fast lookup
            # Retrieve matches in O(1) time per K-seq
            k_seq_matches = {
                " ".join(k_seq): list(self.k_seq_index.get(" ".join(k_seq), [])) for k_seq in self.k_seq
            }
            # Filter out empty matches
            filtered_output = {k_seq: matches for k_seq, matches in k_seq_matches.items() if matches}
            output_data = {
                "Question " + self.task_number: {
                    "K-Seq Matches": sorted(
                        [[k_seq, sorted(matches)] for k_seq, matches in filtered_output.items()],
                        key=lambda x: str(x[0])  # Sort by K-seq string
                    )
                }
            }
            print(json.dumps(output_data, indent=4))  # Print JSON results
        except Exception as e:
            print("Error during search: " + str(e))
