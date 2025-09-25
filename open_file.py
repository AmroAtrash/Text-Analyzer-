import csv
from typing import List, Set, Tuple


class OpenFile:
    """
    A utility class for handling file operations related to sentences, names, and words to remove.
    """
    def __init__(self, sentences_path: str, names_path: str, remove_words_path: str):
        """
        Initializes the file paths for the respective files.
        Args:
            sentences_path (str): Path to the sentences file.
            names_path (str): Path to the names file.
            remove_words_path (str): Path to the remove words file.
        """
        self.sentences_path: str = sentences_path
        self.names_path: str = names_path
        self.remove_words_path: str = remove_words_path

    @staticmethod
    def read_sentences_file(sentences_path: str) -> List[str]:
        """
        Reads a CSV file containing sentences and extracts them.
        Args:
            sentences_path (str): Path to the CSV file with sentences.
        Returns:
            List[str]: A list of sentences converted to lowercase.
        """
        try:
            read_sentences = []
            with open(sentences_path, 'r') as f:
                read_csv = csv.DictReader(f)
                for file_row in read_csv:
                    # Ensure the "sentence" column exists
                    if "sentence" in file_row:
                        sentence = file_row.get("sentence", "").strip().lower()
                        if sentence:
                            read_sentences.append(sentence)
                    else:
                        print("CSV file" + sentences_path + "does not contain a 'sentence' column.")
                        return []
            return read_sentences
        except FileNotFoundError:
            print("Error: File" + sentences_path + "not found.")  # Handle missing file
            return []
        except Exception as e:
            print("Error during read_sentences_file: " + str(e))  # Handle unexpected errors
            return []

    @staticmethod
    def read_names_file(names_path: str) -> List[Tuple[str, List[str]]]:
        """
        Reads a CSV file containing names and extracts main names along with their other names (aliases).
        Args:
            names_path (str): Path to the CSV file containing names.
        Returns:
            List[Tuple[str, List[str]]]: A list of tuples, each containing a main name and a list of other names.
        """
        try:
            read_names = []
            with open(names_path, 'r') as f:
                read_csv = csv.DictReader(f)
                # Ensure the required columns exist
                if not read_csv.fieldnames or not {"Name", "Other Names"}.issubset(set(read_csv.fieldnames)):
                    print("Warning: The file must contain 'Name' and 'Other Names' columns. Skipping file.")
                    return []
                for file_row in read_csv:
                    main_name = file_row.get("Name", "").strip().lower()
                    other_names = file_row.get("Other Names", "")
                    if main_name:
                        # Process aliases by splitting them into a list
                        other_names_list = [alias.strip().lower() for alias in other_names.split(',') if alias.strip()]
                        read_names.append((main_name, other_names_list))
            return read_names
        except FileNotFoundError:
            print("Error: File" + names_path + "not found.")  # Handle missing file
            return []
        except Exception as e:
            print("Error during read_names_file: " + str(e))  # Handle unexpected errors
            return []

    @staticmethod
    def read_remove_words_file(remove_words_path: str) -> Set[str]:
        """
        Reads a file containing words that should be removed during processing.
        Args:
            remove_words_path (str): Path to the file containing words to remove.
        Returns:
            Set[str]: A set of words that need to be removed.
        """
        try:
            remove_words = set()
            with open(remove_words_path, 'r') as f:
                read_csv = csv.reader(f)
                for row in read_csv:
                    if len(row) > 0:
                        remove_words.add(row[0].strip().lower())  # Store words in lowercase
            return remove_words
        except FileNotFoundError:
            print("Error: File" + remove_words_path + "not found.")  # Handle missing file
            return set()
        except Exception as e:
            print("Error during read_remove_words_file: " + str(e))  # Handle unexpected errors
            return set()