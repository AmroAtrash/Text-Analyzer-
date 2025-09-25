import json
from typing import List, Dict, Tuple


class SequenceCounter:
    def __init__(self, sentences: List[List[str]], remove_words: set[str], max_k: int, task_number: str):
        """
        Initializes the SequenceCounter class.
        Args:
            sentences (List[List[str]]): A list of tokenized sentences (preprocessed).
            remove_words (set[str]): A set of words to remove (not used directly here).
            max_k (int): Maximum sequence length to count.
            task_number (str): Task number identifier.
        """
        self.sentences: List[List[str]] = sentences  # Store tokenized sentences
        self.remove_words: set[str] = remove_words  # Set of words to remove (currently unused)
        self.max_k: int = max_k  # Max sequence length to analyze
        self.task_number = task_number  # Identifier for output formatting

    def count_all_sequences(self) -> None:
        """
        Counts all k-sequences from 1 to max_k and outputs the result in JSON format.
        This function:
        - Iterates over k values from 1 to max_k.
        - Calls count_k_sequences(k) for each k.
        - Collects and structures the output into a JSON format.
        """
        try:
            all_counts = {}
            # Iterate through all k values from 1 to max_k
            for k in range(1, self.max_k + 1):
                all_counts[k] = self.count_k_sequences(k)  # Get k-sequence counts
            formatted_counts = []
            # Structure the output as required
            for k, counts in all_counts.items():
                # Convert dictionary of sequences to list format for JSON output
                k_seq_list = [[f"{' '.join(seq)}", count] for seq, count in sorted(counts.items())]
                formatted_counts.append([f"{k}_seq", k_seq_list])
            # Construct final JSON output format
            output_data = {
                "Question " + self.task_number: {
                    str(self.max_k) + "-Seq Counts": formatted_counts
                }
            }
            # Print the output in JSON format
            print(json.dumps(output_data, indent=4))
        except Exception as e:
            print("Error during count_all_sequences: " + str(e))

    def count_k_sequences(self, k: int) -> dict:
        """
        Counts the occurrences of k-sequences (n-grams) in the tokenized sentences.
        Args:
            k (int): The length of the sequence (n-gram size).
        Returns:
            dict: A dictionary where keys are k-sequences (as tuples of words)
                  and values are their frequency counts.
        """
        try:
            k_seq_counts: Dict[Tuple[str, ...], int] = {}
            # Iterate over each sentence in the dataset
            for sentence in self.sentences:
                # Generate k-sequences using a sliding window approach
                for i in range(len(sentence) - k + 1):
                    k_seq = tuple(sentence[i:i + k])  # Extract k-sequence
                    k_seq_counts[k_seq] = k_seq_counts.get(k_seq, 0) + 1  # Count occurrences
            return k_seq_counts  # Return the frequency dictionary
        except Exception as e:
            print("Error during count_k_sequences: " + str(e))
            return {}

