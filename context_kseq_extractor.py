import json
from typing import List, Tuple, Dict
from collections import defaultdict


class ContextKSeqExtractor:
    """
    A class for extracting k-sequences from tokenized sentences and associating them with specific names.
    - The class is responsible for identifying context sequences of variable lengths (k-sequences).
    - It can interleave sequences for structured output.
    """

    def __init__(self, sentences: List[List[str]], names: List[List[str]], max_k: int, task_number: str):
        """
        Initializes the ContextKSeqExtractor.
        Args:
            sentences (List[List[str]]): List of tokenized sentences.
            names (List[List[str]]): List of name groups (primary name + aliases).
            max_k (int): Maximum value of K for k-sequences.
            task_number (str): Task number for output formatting.
        Attributes:
            self.sentences (List[List[str]]): Stores the tokenized sentences.
            self.names (Dict[str, List[str]]): Maps primary names to aliases.
            self.max_k (int): Maximum k-sequence length.
            self.task_number (str): Stores the task number.
        """
        self.sentences: List[List[str]] = sentences
        self.names: Dict[str, List[str]] = self.names_to_dict(names)
        self.max_k: int = max_k
        self.task_number: str = task_number

    @staticmethod
    def names_to_dict(names: List[List[str]]) -> Dict[str, List[str]]:
        """
        Converts a list of names and aliases into a dictionary format.
        Args:
            names (List[List[str]]): List of lists with names and aliases.
        Returns:
            Dict[str, List[str]]: Dictionary mapping primary names to their aliases.
        Efficiency:
        - **O(N)**, where `N` is the number of name groups.
        - Uses a dictionary for fast lookups.
        Edge Cases:
        - Handles cases where no aliases exist.
        """
        try:
            return {
                ' '.join(name_group[0]): [' '.join(other_name) for other_name in name_group[1:][0]]
                for name_group in names
            }
        except Exception as e:
            print("Error during names_to_dict: " + str(e))
            return {}

    @staticmethod
    def generate_ngrams(tokens: List[str], n: int) -> List[str]:
        """
        Generate n-grams from a list of tokens.
        Args:
            tokens (List[str]): List of tokens.
            n (int): Size of the n-grams.
        Returns:
            List[str]: List of generated n-grams.
        Efficiency:
        - **O(M)**, where `M` is the length of the tokenized sentence.
        - Uses a sliding window approach.
        Edge Cases:
        - If `n` is larger than the token list, returns an empty list.
        """
        try:
            return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]
        except Exception as e:
            print("Error during generate_ngrams: " + str(e))
            return []

    def extract_k_sequences(self, sentence: List[str]) -> Dict[int, List[List[str]]]:
        """
        Extracts k-sequences (1 to max_k) from a given sentence.
        Args:
            sentence (List[str]): Tokenized sentence.
        Returns:
            Dict[int, List[List[str]]]: Dictionary of k-sequences grouped by k.
        Efficiency:
        - **O(M*K)**, where `M` is sentence length and `K` is the max sequence length.
        """
        try:
            k_seqs = defaultdict(list)
            for k in range(1, self.max_k + 1):
                for i in range(len(sentence) - k + 1):
                    k_seqs[k].append(sentence[i:i + k])
            return k_seqs
        except Exception as e:
            print("Error during extract_k_sequences: " + str(e))
            return {}

    @staticmethod
    def interleave_sequences_with_priority(grouped_k_seqs: Dict[int, List[Tuple[str]]]) -> List[Tuple[str]]:
        """
        Interleaves sequences with priority, maintaining the order of 1-seq, 2-seq, ..., max_k-seq.
        Args:
            grouped_k_seqs (Dict[int, List[Tuple[str]]]): Grouped k-sequences.
        Returns:
            List[Tuple[str]]: Interleaved k-sequences.
        Efficiency:
        - **O(N)**, where `N` is the total number of k-seqs.
        - Uses an index tracking method to ensure fairness across k-sequences.
        """
        try:
            max_k = max(grouped_k_seqs.keys())
            interleaved_seqs = []
            indices = {k: 0 for k in grouped_k_seqs}
            while any(indices[k] < len(grouped_k_seqs[k]) for k in grouped_k_seqs):
                for k in range(1, max_k + 1):
                    if k in grouped_k_seqs and indices[k] < len(grouped_k_seqs[k]):
                        current_seq = grouped_k_seqs[k][indices[k]]
                        interleaved_seqs.append(current_seq)
                        indices[k] += 1
            return interleaved_seqs
        except Exception as e:
            print("Error during interleave_sequences_with_priority: " + str(e))
            return []

    def find_person_contexts(self) -> None:
        """
        Extracts k-sequences from tokenized sentences and associates them with matched names.
        Returns:
            str: JSON-formatted output with interleaved k-sequences for each person.
        Efficiency:
        - **O(P * S * K)**, where `P` is the number of people, `S` is the number of sentences, and `K` is max_k.
        - Uses name matching and k-sequence extraction for every relevant sentence.
        Edge Cases:
        - If `max_k` is 0, it prints the names instead of sequences.
        """
        try:
            if self.max_k == 0:
                output = {
                    "Question " + self.task_number: {
                        "Person Names": sorted(self.names.keys())
                    }
                }
                print(json.dumps(output, indent=4))
                return
            person_contexts: Dict[str, Dict[int, set[Tuple[str, ...]]]] = defaultdict(lambda: defaultdict(set))
            for sentence in self.sentences:
                if any(isinstance(word, list) for word in sentence):
                    sentence = [word for sublist in sentence for word in sublist]
                k_seqs = self.extract_k_sequences(sentence)
                for primary_name, aliases in self.names.items():
                    all_names = [primary_name] + aliases
                    name_parts = set(primary_name.split())
                    # Check if any name appears in the sentence
                    if any(name in " ".join(sentence) for name in all_names) or name_parts.intersection(set(sentence)):
                        for k, seqs in k_seqs.items():
                            person_contexts[primary_name][k].update(tuple(seq) for seq in seqs)
            print(self.format_output_interleaved(dict(person_contexts)))
        except Exception as e:
            print("Error during find_person_contexts: " + str(e))

    def format_output_interleaved(self, person_contexts: Dict[str, Dict[int, set]]) -> str:
        """
        Formats the output by interleaving k-sequences for each person.
        Args:
            person_contexts (Dict[str, Dict[int, set]]): Dictionary of person contexts and k-sequences.
        Returns:
            str: JSON-formatted output.
        Efficiency:
        - **O(N log N)**, due to sorting operations.
        Edge Cases:
        - If no sequences exist, returns an empty JSON.
        """
        try:
            output: Dict = {"Question " + self.task_number: {"Person Contexts and K-Seqs": []}}
            for person in sorted(person_contexts.keys()):
                k_seqs = person_contexts[person]
                grouped_k_seqs = defaultdict(list)
                for k, sequences in k_seqs.items():
                    grouped_k_seqs[k].extend(sorted(sequences))
                interleaved_seqs = self.interleave_sequences_with_priority(grouped_k_seqs)
                output["Question " + self.task_number]["Person Contexts and K-Seqs"].append([
                    person,
                    sorted([list(seq) for seq in interleaved_seqs])
                ])
            return json.dumps(output, indent=4)
        except Exception as e:
            print("Error during format_output_interleaved: " + str(e))
            return "{}"
