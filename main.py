#!/usr/bin/env python3
import argparse
import json
import os
from typing import Dict, Optional, Any
from matplotlib import pyplot as plt
from preprocessor import Preprocessor
from open_file import OpenFile
from sequence_counter import SequenceCounter
from counting_person_mentions import CountingPersonMentions
from basic_search import BasicSearchEngine
from context_kseq_extractor import ContextKSeqExtractor
from finding_connection_between_people import BaseGraph
from indirect_connections import IndirectConnectionFinder
from fixed_length_paths import FindConnection
from grouping_sentences import SentenceGrouping


def readargs(args=None):
    parser = argparse.ArgumentParser(
        prog='Text Analyzer project',
    )
    # General arguments
    parser.add_argument('-t', '--task',
                        help="task number",
                        required=True
                        )
    parser.add_argument('-s', '--sentences',
                        help="Sentence file path",
                        )
    parser.add_argument('-n', '--names',
                        help="Names file path",
                        )
    parser.add_argument('-r', '--removewords',
                        help="Words to remove file path",
                        )
    parser.add_argument('-p', '--preprocessed',
                        action='append',
                        help="json with preprocessed data",
                        )
    # Task specific arguments
    parser.add_argument('--maxk',
                        type=int,
                        help="Max k",
                        )
    parser.add_argument('--fixed_length',
                        type=int,
                        help="fixed length to find",
                        )
    parser.add_argument('--windowsize',
                        type=int,
                        help="Window size",
                        )
    parser.add_argument('--pairs',
                        help="json file with list of pairs",
                        )
    parser.add_argument('--threshold',
                        type=int,
                        help="graph connection threshold",
                        )
    parser.add_argument('--maximal_distance',
                        type=int,
                        help="maximal distance between nodes in graph",
                        )

    parser.add_argument('--qsek_query_path',
                        help="json file with query path",
                        )
    return parser.parse_args(args)


def check_is_valid_number(value) -> bool:
    if value is None:
        return False
    try:
        return int(value) >= 0
    except ValueError:
        return False


def validate_files(args) -> Optional[Dict[str, Any]]:
    """
    Validates the presence of required files and loads their data.
    Returns:
        A dictionary containing the loaded data if valid, otherwise None.
    """
    try:
        required_files: Dict[str, Optional[str]] = {
            'sentences': args.sentences,
            'names': args.names,
            'removewords': args.removewords,
            'preprocessed': args.preprocessed[0] if args.preprocessed else None,
            'pairs': args.pairs,
            'qsek_query_path': args.qsek_query_path,
        }
        # Check if files exist
        for key, file_path in required_files.items():
            if file_path and not os.path.isfile(file_path):
                print("Error: The" + str(key) + "file does not exist.")
                return None
        # Check integer arguments (they must be non-negative)
        if args.windowsize is not None and not check_is_valid_number(int(args.windowsize)):
            print("Error: --windowsize must be non-negative.")
            exit()
        if args.threshold is not None and not check_is_valid_number(int(args.threshold)):
            print("Error: --threshold must be non-negative.")
            exit()
        if args.fixed_length is not None and not check_is_valid_number(int(args.fixed_length)):
            print("Error: --fixed_length must be non-negative.")
            exit()
        if args.maximal_distance is not None and not check_is_valid_number(int(args.maximal_distance)):
            print("Error: --maximal_distance must be non-negative.")
            exit()
        if args.maxk is not None and not check_is_valid_number(int(args.maxk)):
            print("Error: --maxk must be non-negative.")
            exit()
        # Initialize data storage
        data: Dict[str, Any] = {'sentences': [], 'names': [], 'removewords': set(), 'pairs': [], 'qsek_query': []}
        # Load file data
        if args.sentences:
            data['sentences'] = OpenFile.read_sentences_file(args.sentences)
        if args.names:
            data['names'] = OpenFile.read_names_file(args.names)
        if args.removewords:
            data['removewords'] = OpenFile.read_remove_words_file(args.removewords)
        data['pairs'] = []
        if args.pairs:
            try:
                with open(args.pairs, 'r') as file:
                    data['pairs'] = json.load(file).get("keys", [])
            except (json.JSONDecodeError, FileNotFoundError):
                print("Error: Invalid or missing pairs file. Falling back to empty list.")
        if args.qsek_query_path:
            with open(args.qsek_query_path, 'r') as file:
                data['qsek_query'] = json.load(file).get("keys", [])
        # Load preprocessed data if available
        if args.preprocessed:
            with open(args.preprocessed[0], 'r') as json_file:
                preprocessed_data = json.load(json_file)
            if args.task in ['7', '8']:
                if not preprocessed_data.get("Question 6", {}).get("Pair Matches"):
                    print("WARNING: Preprocessed file does not contain 'Pair Matches'. Using original data instead.")
                    data['pair_matches'] = []
                data['pair_matches'] = preprocessed_data["Question 6"]["Pair Matches"]
            else:
                if not preprocessed_data.get("Question 1", {}).get("Processed Sentences") or \
                        not preprocessed_data.get("Question 1", {}).get("Processed Names"):
                    print("ERROR: Preprocessed file does not contain 'Processed Sentences' or "
                          "'Processed Names'. Falling back to original data.")
                    exit()
                data['sentences'] = preprocessed_data["Question 1"]["Processed Sentences"]
                data['names'] = preprocessed_data["Question 1"]["Processed Names"]
        else:
            if args.task in ['1', '3', '5', '6', '7', '8'] and not data['names']:
                print("Error: Task", args.task, "requires a valid names file. Please check your input.")
                exit()
            if not data.get('sentences') or not isinstance(data['sentences'], list):
                print("Error: No valid sentences found in input files. Please check your sentence file.")
                exit()
        return data
    except json.JSONDecodeError:
        print("Error: One of the provided JSON files has an invalid format.")
    except IOError:
        print("Error: Could not read one of the files.")
    except Exception as e:
        print("An unexpected error occurred while validating files:", str(e))
    return None


def main():
    """
    Main function to execute the program based on the provided task number.
    """
    try:
        args = readargs()
        if args is None:
            print("Error: Failed to parse command-line arguments.")
            exit()
        data = validate_files(args)
        if not data:
            print("Error: Input validation failed. Exiting program.")
            exit()
        # Initialize variables to avoid uninitialized reference errors
        tokenized_sentences = []
        cleaned_names = []
        # Handling preprocessed vs. regular data
        if args.preprocessed:
            if args.task in ['7', '8']:
                if 'pairs' not in data or not isinstance(data['pairs'], list):
                    print("Error: No valid 'Pair Matches' found in preprocessed data. Please check your Task 6 output.")
                    exit()
            else:
                tokenized_sentences = data['sentences']
                cleaned_names = data['names']
        else:  # If not preprocessed, process the raw input
            cleaned_sentences = Preprocessor.clean_sentences(data['sentences'], data['removewords'])
            tokenized_sentences = Preprocessor.sentences_to_words(cleaned_sentences)
            preprocessor = Preprocessor(data['sentences'], data['names'], data['removewords'], args.task)
            cleaned_names = preprocessor.clean_names_and_other_names(data['names'], data['removewords'])
        # Execute tasks based on task number
        if args.task == '1':
            preprocessor = Preprocessor(data['sentences'], data['names'], data['removewords'], args.task)
            preprocessor.preprocess_data()
        elif args.task == '2':
            sequence_counter = SequenceCounter(tokenized_sentences, data['removewords'], args.maxk, args.task)
            sequence_counter.count_all_sequences()
        elif args.task == '3':
            counter = CountingPersonMentions(tokenized_sentences, cleaned_names, args.task)
            counter.count_mentions()
        elif args.task == '4':
            searcher = BasicSearchEngine(data['qsek_query'], tokenized_sentences, args.task)
            searcher.search()
        elif args.task == '5':
            context_kseq = ContextKSeqExtractor(tokenized_sentences, cleaned_names, args.maxk, args.task)
            context_kseq.find_person_contexts()
        elif args.task == '6':
            find_connection = BaseGraph(tokenized_sentences, cleaned_names, args.windowsize, args.threshold, args.task)
            find_connection.count_connections()
            find_connection.export_results()
        elif args.task == '7':
            if args.preprocessed:
                if 'pair_matches' not in data or not isinstance(data['pair_matches'], list):
                    print("Error: No valid 'Pair Matches' found in preprocessed data.")
                    exit()
                # Extract names from Pair Matches
                extracted_names = {tuple(sorted(entity)) for pair in data['pair_matches'] for entity in pair}
                cleaned_names = sorted([list(name) for name in extracted_names])
                check_connection = IndirectConnectionFinder([], cleaned_names, args.windowsize,
                                                            data['pairs'], args.threshold, args.maximal_distance,
                                                            args.task)
                check_connection.check_indirect_connections()
            else:
                check_connection = IndirectConnectionFinder(tokenized_sentences, cleaned_names, args.windowsize,
                                                            data['pairs'], args.threshold, args.maximal_distance,
                                                            args.task)
                check_connection.check_indirect_connections()
        elif args.task == '8':
            if args.preprocessed:
                if 'pair_matches' not in data or not isinstance(data['pair_matches'], list):
                    print("Error: No valid 'Pair Matches' found in preprocessed data.")
                    exit()
                # Extract names from Pair Matches
                extracted_names = {tuple(sorted(entity)) for pair in data['pair_matches'] for entity in pair}
                cleaned_names = sorted([list(name) for name in extracted_names])
                find_connection = FindConnection([], cleaned_names, args.windowsize, args.threshold,
                                                 data['pairs'], args.fixed_length, args.task)
                find_connection.export_results()
                # runtimes = find_connection.analyze_runtime()
                # plt.plot(list(runtimes.keys()), list(runtimes.values()), marker='o', linestyle='-')
                # plt.xlabel("K (Path Length)")
                # plt.ylabel("Runtime (seconds)")
                # plt.title("Effect of K on Runtime")
                # plt.grid(True)
                # plt.show()
            else:
                find_connection = FindConnection(tokenized_sentences, cleaned_names, args.windowsize, args.threshold,
                                                 data['pairs'], args.fixed_length, args.task)
                find_connection.export_results()
                # runtimes = find_connection.analyze_runtime()
                # plt.plot(list(runtimes.keys()), list(runtimes.values()), marker='o', linestyle='-')
                # plt.xlabel("K (Path Length)")
                # plt.ylabel("Runtime (seconds)")
                # plt.title("Effect of K on Runtime")
                # plt.grid(True)
                # plt.show()
        elif args.task == '9':
            grouping_sentences = SentenceGrouping(tokenized_sentences, args.threshold, args.task)
            grouping_sentences.export_results()
            # runtimes = grouping_sentences.analyze_runtime()
            # plt.plot(list(runtimes.keys()), list(runtimes.values()), marker='o', linestyle='-')
            # plt.xlabel("K (Path Length)")
            # plt.ylabel("Runtime (seconds)")
            # plt.title("Effect of K on Runtime")
            # plt.grid(True)
            # plt.show()
        else:
            print("Error: Invalid task number specified.")
            exit()
    except Exception as e:
        print("Critical Error during execution: " + str(e))
        exit()


if __name__ == "__main__":
    main()
