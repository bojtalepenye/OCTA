import argparse
from pathlib import Path
import os
from typing import Dict, Tuple, List

class CredentialMatcher:
    def __init__(self, base_file: str, match_files: List[str], output_dir: str):
        self.base_file = base_file
        self.match_files = match_files
        self.output_dir = output_dir
        self.base_name = Path(base_file).stem

    def load_credentials(self, file_path: str) -> Dict[str, Tuple[str, str]]:
        """Load credentials from a file. Returns dict with username as key and (hash, password) as value."""
        credentials = {}
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    username = parts[0]
                    hash_value = parts[1]
                    password = parts[2] if len(parts) > 2 else ''
                    credentials[username] = (hash_value, password)
        return credentials

    def create_markdown_table(self, data: List[Tuple[str, str, str]], comment_data: List[Tuple[str, str, str, str]]) -> str:
        """Create formatted markdown tables for matches and warnings with adjustable column widths."""
        if not data and not comment_data:
            return ""

        all_data = data + comment_data
        max_lengths = [max(len(str(item)) for item in column) for column in zip(*all_data)]

        # Ensure the headers are included in the max length calculation
        headers = ["Username/Email", "Hash", "Password", "Comments"]
        for i, header in enumerate(headers):
            if i < len(max_lengths):
                max_lengths[i] = max(max_lengths[i], len(header))
            else:
                max_lengths.append(len(header))

        # Create header with adjusted width
        table = ""
        table += "| " + " | ".join(f"{header:{max_lengths[i]}}" for i, header in enumerate(headers)) + " |\n"
        table += "| " + " | ".join(f"{'-'*max_lengths[i]}" for i in range(len(headers))) + " |\n"

        # Add data rows
        for row in data:
            table += "| " + " | ".join(f"{str(item):{max_lengths[i]}}" for i, item in enumerate(row)) + " |\n"

        # Add comment rows
        for row in comment_data:
            table += "| " + " | ".join(f"{str(item):{max_lengths[i]}}" for i, item in enumerate(row)) + " |\n"

        return table

    def write_matches(self, matches: List[Tuple[str, str, str]], warnings: List[Tuple[str, str, str, str]], source_file: str):
        """Write matches and warnings to separate files."""
        source_name = Path(source_file).stem

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Create matches directory
        matches_dir = os.path.join(self.output_dir, "matches")
        os.makedirs(matches_dir, exist_ok=True)

        # Create warnings directory
        warnings_dir = os.path.join(self.output_dir, "warnings")
        os.makedirs(warnings_dir, exist_ok=True)

        # Write matches
        if matches:
            match_file = os.path.join(matches_dir, f"{self.base_name}_vs_{source_name}_matches.txt")
            with open(match_file, 'w') as f:
                f.write(f"# Matches found in {self.base_name} vs {source_name}\n\n")
                match_table = self.create_markdown_table(matches, [])
                f.write(match_table)

        # Write warnings
        if warnings:
            warning_file = os.path.join(warnings_dir, f"{self.base_name}_vs_{source_name}_warnings.txt")
            with open(warning_file, 'w') as f:
                f.write(f"# Warnings for {self.base_name} vs {source_name}\n\n")
                warning_table = self.create_markdown_table([], warnings)
                f.write(warning_table)

    def process_matches(self):
        """Process matches between base file and all match files."""
        base_credentials = self.load_credentials(self.base_file)

        for match_file in self.match_files:
            match_credentials = self.load_credentials(match_file)
            matches = []
            warnings = []

            # Compare credentials
            for username, (hash_value, _) in match_credentials.items():
                if username in base_credentials:
                    base_hash, base_password = base_credentials[username]
                    if hash_value == base_hash:
                        matches.append((username, hash_value, base_password))
                    else:
                        comment = ""
                        password_display = "Hash mismatch"
                        if "@" in username:
                            comment = "Email found as username; password may match."
                            password_display = base_password
                        warnings.append((username, hash_value, password_display, comment))

            # Write results
            self.write_matches(matches, warnings, match_file)

def main():
    parser = argparse.ArgumentParser(description='Multi-source credential matcher')
    parser.add_argument('-b', '--base', required=True,
                        help='Base credential file (username:hash:password)')
    parser.add_argument('-m', '--match', required=True, nargs='+',
                        help='One or more files to match against the base file')
    parser.add_argument('-o', '--outdir', default='matches',
                        help='Output directory for match files (default: matches)')

    args = parser.parse_args()

    matcher = CredentialMatcher(args.base, args.match, args.outdir)
    matcher.process_matches()

if __name__ == '__main__':
    main()
