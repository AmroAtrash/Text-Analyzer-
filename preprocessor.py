import json
from typing import List, Set, Tuple


class Preprocessor:
    def __init__(self, sentences: List[str], names: List[Tuple[str, List[str]]], remove_words: set[str],
                 task_number: str):
        """
        Initializes the Preprocessor class with sentences, names, and words to remove.
        Args:
            sentences (List[str]): A list of raw sentences from the input file.
            names (List[Tuple[str, List[str]]]): A list of names and their aliases.
            remove_words (set[str]): A set of words to be removed during preprocessing.
            task_number (str): Task identifier for output formatting.
        """
        self.sentences: List[str] = sentences
        self.names: List[Tuple[str, List[str]]] = names
        self.remove_words: set[str] = remove_words
        self.task_number: str = task_number

    def preprocess_data(self) -> None:
        """
        Preprocesses the sentences and names by:
        - Cleaning the sentences
        - Removing unnecessary words
        - Tokenizing sentences into word lists
        - Cleaning names and aliases
        The output is printed in JSON format.
        """
        try:
            # Clean sentences by removing unnecessary words
            cleaned_sentences = self.clean_sentences(self.sentences, self.remove_words)
            # Clean names and associated aliases
            cleaned_names = self.clean_names_and_other_names(self.names, self.remove_words)
            # Tokenize the cleaned sentences into word lists
            split_sentences = self.sentences_to_words(cleaned_sentences)
            # Format the output
            output_data = {
                "Question " + self.task_number: {
                    "Processed Sentences": split_sentences,
                    "Processed Names": cleaned_names,
                }
            }
            print(json.dumps(output_data, indent=4))
        except Exception as e:
            print("Error during preprocessing:" + str(e))

    @staticmethod
    def clean_sentences(sentences: List[str], remove_words: Set[str]) -> List[str]:
        """
        Cleans sentences by:
        - Removing non-alphanumeric characters
        - Normalizing whitespace
        - Removing stop words (words from `remove_words` set)
        Args:
            sentences (List[str]): Raw sentences.
            remove_words (Set[str]): Set of words to remove.
        Returns:
            List[str]: Cleaned sentences.
        """
        try:
            cleaned_sentences = []
            for sentence in sentences:
                # Replace non-alphanumeric characters with spaces
                sentence = ''.join(char if char.isalnum() or char.isspace() else ' ' for char in sentence)
                # Normalize whitespace
                sentence = " ".join(sentence.split())
                # Remove stop words and convert to lowercase
                words = sentence.split()
                filtered_words = [word.lower() for word in words if word.lower() not in remove_words]
                # Reconstruct cleaned sentence
                cleaned_sentence = " ".join(filtered_words)
                # Only add non-empty sentences
                if cleaned_sentence.strip():
                    cleaned_sentences.append(cleaned_sentence)
            return cleaned_sentences
        except Exception as e:
            print("Error during clean_sentences:" + str(e))
            return []

    @staticmethod
    def sentences_to_words(cleaned_sentences: List[str]) -> List[List[str]]:
        """
        Tokenizes cleaned sentences into lists of words.
        Args:
            cleaned_sentences (List[str]): List of cleaned sentences.
        Returns:
            List[List[str]]: Tokenized sentences.
        """
        try:
            split_sentence_to_words = []
            for sentence in cleaned_sentences:
                words_sentence = sentence.split()
                split_sentence_to_words.append(words_sentence)
            return split_sentence_to_words
        except Exception as e:
            print("Error during sentences_to_words:" + str(e))
            return []

    def clean_names_and_other_names(self, names: List[Tuple[str, List[str]]],
                                    remove_words: Set[str]) -> List[List]:
        """
        Cleans main names and their associated aliases by:
        - Removing unwanted words
        - Normalizing formatting
        - Eliminating duplicates
        Args:
            names (List[Tuple[str, List[str]]]): Names and aliases.
            remove_words (Set[str]): Words to remove.
        Returns:
            List[List]: Cleaned names and aliases.
        """
        try:
            cleaned_data = []
            appeared_names = set()
            # Clean each name and its aliases
            names = [(self.clean_name(main_name.lower(), remove_words), other_names) for main_name, other_names in names]
            for main_name, other_names in names:
                if main_name == '':
                    continue
                if main_name in appeared_names:
                    continue
                appeared_names.add(main_name.lower())
                # Structure: [Main name, [List of aliases]]
                to_append = [main_name.split(),
                             [self.clean_name(other_name.lower(), remove_words).split() for other_name in other_names]]
                cleaned_data.append(to_append)
            return cleaned_data
        except Exception as e:
            print("Error during clean_names_and_other_names: " + str(e))
            return []

    def clean_name(self, name: str, remove_words: Set[str]) -> str:
        """
        Cleans a single name by:
        - Removing unwanted words
        - Normalizing whitespace and case
        - Removing special characters
        Args:
            name (str): Raw name.
            remove_words (Set[str]): Set of words to remove.
        Returns:
            str: Cleaned name.
        """
        try:
            # Replace non-alphanumeric characters with spaces
            name = ''.join(char if char.isalnum() or char.isspace() else ' ' for char in name)
            # Normalize whitespace
            name = " ".join(name.split())
            # Remove stop words
            words = name.split()
            filtered_words = [word for word in words if word.lower() not in remove_words]
            # Return final cleaned name
            return " ".join(filtered_words)
        except Exception as e:
            print("Error during clean_name: " + str(e))
            return ""
