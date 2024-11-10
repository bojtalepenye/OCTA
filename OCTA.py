import argparse
from pathlib import Path
import os
import shutil
from typing import Dict, Tuple, List
from tqdm import tqdm
from collections import defaultdict
import re

def is_email(username):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", username))

class CredentialMatcher:
    def __init__(self, base_files: List[str], match_files: List[str], directory_dir: str, output_dir: str, debug: bool = False):
        self.base_files = base_files
        self.match_files = match_files
        self.directory_dir = directory_dir
        self.output_dir = output_dir if output_dir else "matches"
        self.aggregated_matches = defaultdict(list)
        self.aggregated_mismatches = defaultdict(list)
        self.failed_files = 0
        self.current_base_credentials = {}
        self.debug = debug

    def load_credentials(self, file_path: str) -> Dict[str, Tuple[str, str]]:
        """Load credentials from a file. Returns dict with username as key and (hash, password) as value."""
        credentials = {}
        if self.debug:
            print(f"\nDEBUG: Loading credentials from {file_path}")
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    hash_value = parts[1]
                    password = parts[2] if len(parts) > 2 else ''
                    credentials[username] = (hash_value, password)
                    if self.debug:
                        print(f"DEBUG: Loaded credential - Username: {username}, Hash: {hash_value}, Password: {password}")
        return credentials

    def create_markdown_table(self, data: List[Tuple[str, str, str]], mismatch_data: List[Tuple[str, str, str, str]]) -> str:
        """Create formatted markdown tables for matches and mismatches with adjustable column widths."""
        if not data and not mismatch_data:
            return ""

        if self.debug:
            print("\nDEBUG: Mismatch data before processing:")
            for entry in mismatch_data:
                print(f"DEBUG: Mismatch entry: {entry}")

        if mismatch_data:
            mismatch_data = sorted(mismatch_data, key=lambda x: (
                x[3],  # Sort by source (list name)
                self._natural_sort_key(x[0])  # Sort by username with natural sorting
            ))
            current_source = None
            temp_data = []
            current_group = []

            for entry in mismatch_data:
                if current_source != entry[3]:
                    if current_group:
                        temp_data.extend(current_group)
                    current_group = []
                    current_source = entry[3]
                current_group.append(entry)
            if current_group:
                temp_data.extend(current_group)

            mismatch_data = temp_data[::-1]

        all_data = data + mismatch_data
        max_lengths = [max(len(str(item)) for item in column) for column in zip(*all_data)]

        headers = ["Usernames/Emails", "Hashes", "Passwords", "Comments"]
        for i, header in enumerate(headers):
            if i < len(max_lengths):
                max_lengths[i] = max(max_lengths[i], len(header))
            else:
                max_lengths.append(len(header))

        table = ""
        table += "| " + " | ".join(f"{header:{max_lengths[i]}}" for i, header in enumerate(headers)) + " |\n"
        table += "| " + " | ".join(f"{'-'*max_lengths[i]}" for i in range(len(headers))) + " |\n"

        for row in data:
            table += "| " + " | ".join(f"{str(item):{max_lengths[i]}}" for i, item in enumerate(row)) + " |\n"

        for row in mismatch_data:
            table += "| " + " | ".join(f"{str(item):{max_lengths[i]}}" for i, item in enumerate(row)) + " |\n"

        return table

    def _natural_sort_key(self, s):
        """Helper function to sort strings with numbers naturally."""
        import re
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', str(s))]

    def write_results(self, matches: List[Tuple[str, str, str]],
                     mismatches: List[Tuple[str, str, str, str]],
                     source_file: str, base_file: str):
        """Write matches and mismatches to appropriate directories."""
        source_name = Path(source_file).stem
        base_name = Path(base_file).stem

        if self.debug:
            print(f"\nDEBUG: Processing mismatches for {source_name} vs {base_name}")
            for m in mismatches:
                print(f"DEBUG: Original mismatch entry: {m}")

        os.makedirs(self.output_dir, exist_ok=True)

        matches_dir = os.path.join(self.output_dir, "matches")
        matches_per_list_dir = os.path.join(matches_dir, "per-list")
        matches_per_basefile_dir = os.path.join(matches_dir, "per-basefile")
        os.makedirs(matches_per_list_dir, exist_ok=True)
        os.makedirs(matches_per_basefile_dir, exist_ok=True)

        mismatches_dir = os.path.join(self.output_dir, "mismatches")
        mismatches_per_list_dir = os.path.join(mismatches_dir, "per-list")
        mismatches_per_basefile_dir = os.path.join(mismatches_dir, "per-basefile")
        os.makedirs(mismatches_per_list_dir, exist_ok=True)
        os.makedirs(mismatches_per_basefile_dir, exist_ok=True)

        if matches:
            match_file = os.path.join(matches_per_list_dir, f"{base_name}_vs_{source_name}_matches.txt")
            with open(match_file, 'w') as f:
                f.write(f"# Matches found in {base_name} vs {source_name}\n\n")
                match_table = self.create_markdown_table(matches, [])
                if match_table:
                    f.write(match_table)

            self.aggregated_matches[base_name].extend(
                (m[0], m[1], m[2], f"File: {source_name}")
                for m in matches
            )

        if mismatches:
            mismatch_file = os.path.join(mismatches_per_list_dir, f"{base_name}_vs_{source_name}_mismatches.txt")
            with open(mismatch_file, 'w') as f:
                f.write(f"# Mismatches found in {base_name} vs {source_name}\n\n")
                
                per_list_mismatches = []
                for m in mismatches:
                    username = m[0]
                    if is_email(username):
                        base_password = self.current_base_credentials.get(username, ('', ''))[1]
                        if self.debug:
                            print(f"DEBUG: Found base password for {username}: {base_password}")
                        comment = f"File: {source_name}: Email found as username. Password may match: {base_password}"
                    else:
                        comment = ""
                    per_list_mismatches.append((username, m[1], "Hash mismatch", comment))
                
                if self.debug:
                    print("DEBUG: Processed mismatches:")
                    for m in per_list_mismatches:
                        print(f"DEBUG: {m}")
                
                mismatch_table = self.create_markdown_table([], per_list_mismatches)
                if mismatch_table:
                    f.write(mismatch_table)

            formatted_mismatches = []
            for m in mismatches:
                if is_email(m[0]):
                    base_password = self.current_base_credentials.get(m[0], ('', ''))[1]
                    comment = f"File: {source_name}: Email found as username. Password may match: {base_password}"
                else:
                    comment = f"File: {source_name}"
                formatted_mismatches.append((m[0], m[1], "Hash mismatch", comment))

            self.aggregated_mismatches[base_name].extend(formatted_mismatches)

    def write_aggregated_results(self):
        """Write aggregated matches and mismatches per basefile."""
        matches_per_basefile_dir = os.path.join(self.output_dir, "matches", "per-basefile")
        for base_name, matches in self.aggregated_matches.items():
            match_file = os.path.join(matches_per_basefile_dir, f"{base_name}_all_matches.txt")
            with open(match_file, 'w') as f:
                f.write(f"# All matches found for {base_name}\n\n")
                match_table = self.create_markdown_table(matches, [])
                if match_table:
                    f.write(match_table)

        mismatches_per_basefile_dir = os.path.join(self.output_dir, "mismatches", "per-basefile")
        for base_name, mismatches in self.aggregated_mismatches.items():
            mismatch_file = os.path.join(mismatches_per_basefile_dir, f"{base_name}_all_mismatches.txt")
            with open(mismatch_file, 'w') as f:
                f.write(f"# All mismatches found for {base_name}\n\n")
                mismatch_table = self.create_markdown_table([], mismatches)
                if mismatch_table:
                    f.write(mismatch_table)

    def process_matches(self):
        """Process matches between basefiles and all matchfiles."""
        total_files_processed = 0
        total_matches = 0
        total_mismatches = 0
        total_unmatched = 0

        if self.match_files:
            match_files = self.match_files
        else:
            match_files = [str(f) for f in Path(self.directory_dir).glob('*')]

        for base_file in self.base_files:
            base_name = Path(base_file).stem
            print(f"\nProcessing basefile: {base_name}")
            self.current_base_credentials = self.load_credentials(base_file)

            for match_file in tqdm(match_files, desc=f"Matching against {base_name}"):
                try:
                    match_credentials = self.load_credentials(match_file)
                    matches = []
                    mismatches = []
                    source_name = Path(match_file).stem

                    for username, (hash_value, password) in match_credentials.items():
                        if username in self.current_base_credentials:
                            base_hash, base_password = self.current_base_credentials[username]
                            if self.debug:
                                print(f"DEBUG: Comparing credentials for {username}")
                                print(f"DEBUG: Base hash: {base_hash}, Match hash: {hash_value}")
                                print(f"DEBUG: Base password: {base_password}")
                            
                            if hash_value == base_hash:
                                matches.append((username, hash_value, base_password))
                                total_matches += 1
                            else:
                                mismatches.append((username, hash_value, password, source_name))
                                total_mismatches += 1
                        else:
                            total_unmatched += 1

                    self.write_results(matches, mismatches, match_file, base_file)
                    total_files_processed += 1

                except Exception as e:
                    print(f"Error processing file {match_file}: {str(e)}")
                    self.failed_files += 1

        self.write_aggregated_results()

        print("\n*** Processing Results ***")
        print(f"Files Processed           : {total_files_processed}")
        print(f"Failed Files              : {self.failed_files}")
        print(f"Total Matches found       : {total_matches}")
        print(f"Total Mismatches found    : {total_mismatches}")
        print(f"Total Unmatched Usernames : {total_unmatched}")

def main():
    parser = argparse.ArgumentParser(description='Offline Credential Stuffing Attack (OCTA): Multi-source credential matcher')
    parser.add_argument('-b', '--base', nargs='+', required=True,
                        help='One or more base credential files (username:hash:password)')
    parser.add_argument('-m', '--match', nargs='*',
                        help='One or more files to match against the basefiles')
    parser.add_argument('-d', '--directory',
                        help='Directory containing multiple credential lists to match against the basefiles')
    parser.add_argument('-o', '--outdir', default=None,
                        help='Output directory for matchfiles (default: matches)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')

    args = parser.parse_args()

    output_dir = args.outdir if args.outdir else "matches"
    if os.path.exists(output_dir):
        overwrite = input(f"The directory '{output_dir}' already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled. Exiting.")
            return
        else:
            shutil.rmtree(output_dir)
            print(f"Directory '{output_dir}' has been cleared and will be recreated.")

    matcher = CredentialMatcher(args.base, args.match, args.directory, output_dir, args.debug)
    matcher.process_matches()

if __name__ == '__main__':
    main()
