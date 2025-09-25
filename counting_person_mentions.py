import json
from typing import List


class CountingPersonMentions:
    """
    A class for counting mentions of people's names (including alternate names) in tokenized sentences.
    - Extracts main names and their associated nicknames from input.
    - Counts occurrences of each name or alias in the given text data.
    - Outputs results in JSON format.
    """
    def __init__(self, sentences: List[List[str]], names: list[list[str]], task_number: str):
        """
        Initialize the CountingPersonMentions class.
        Args:
            sentences (List[List[str]]): List of tokenized sentences (preprocessed).
            names (List[List[str]]): List of name groups (each containing a main name and aliases).
            task_number (str): Task number for output formatting.
        Attributes:
            self.sentences (List[List[str]]): Stores the tokenized sentences.
            self.names (List[List[str]]): Stores the list of name groups.
            self.task_number (str): Stores the task number.
        """
        self.sentences: List[List[str]] = sentences
        self.names: list[list[str]] = names
        self.task_number: str = task_number

    def count_mentions(self) -> None:
        """
        Count the mentions of each person's name, including alternate names (nicknames),
        and print the output as a JSON-formatted result.
        Steps:
        - Builds a dictionary mapping main names to their aliases.
        - Generates different possible name variations (substrings of main names).
        - Counts occurrences of each name and its variations in the tokenized sentences.
        - Outputs the results sorted alphabetically.
        Efficiency:
        - **O(N * M * K)** where:
          - `N` is the number of names.
          - `M` is the number of sentences.
          - `K` is the average sentence length.
        """
        try:
            # Step 1: Convert names into a dictionary for easier lookup.
            name_to_nicknames = {
                ' '.join(name_lst[0]): [' '.join(other_name) for other_name in name_lst[1]]
                for name_lst in self.names if len(name_lst) > 0
            }
            name_counts = {}  # Dictionary to store counts of each name.
            # Step 2: Iterate over names to generate all possible variations.
            for main_name, nicknames in name_to_nicknames.items():
                all_names = nicknames  # Initialize with nicknames.
                # Generate possible sub-names from the main name.
                for j in range(1, len(main_name)):
                    for i in range(len(main_name)):
                        if i + j > len(main_name):
                            break
                        all_names.append(' '.join(main_name[i:i + j]))
                all_names.append(main_name)  # Include full name.
                all_names.reverse()  # Reverse to prioritize longer names first.
                total_count = 0  # Counter for total occurrences.
                # Step 3: Count occurrences of each name in the sentences.
                for sentence in self.sentences:
                    for name in all_names:
                        name_words = name.split()
                        for word in name_words:
                            total_count += sentence.count(word)  # Count occurrences of each word.
                # Step 4: Store results only if mentions exist.
                if total_count > 0:
                    name_counts[main_name] = total_count
            # Step 5: Format output as a JSON object.
            output_data = {
                "Question " + self.task_number: {
                    "Name Mentions": [
                        [name, count] for name, count in sorted(name_counts.items(), key=lambda x: x[0])
                        # Sort names alphabetically.
                    ]
                }
            }
            print(json.dumps(output_data, indent=4))  # Print the JSON result.
        except Exception as e:
            print("Error during counting mentions: " + str(e))  # Handle any unexpected errors.
