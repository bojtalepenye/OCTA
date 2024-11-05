import argparse

# Load the known username:hash:password triples
def load_known_credentials(file_path):
    known_credentials = {}
    with open(file_path, 'r') as f:
        for line in f:
            username, hash_value, password = line.strip().split(':')
            known_credentials[(username, hash_value)] = password  # Use (username, hash) as the key
    return known_credentials

# Load the username:hash pairs
def load_hashes(file_path):
    hash_pairs = {}
    with open(file_path, 'r') as f:
        for line in f:
            username, hash_value = line.strip().split(':')
            hash_pairs[username] = hash_value
    return hash_pairs

# Create a new file with the format username:hash:password
def correlate_credentials(known_file, hash_file, output_file):
    known_credentials = load_known_credentials(known_file)
    hash_pairs = load_hashes(hash_file)

    with open(output_file, 'w') as f_out:
        for username, hash_value in hash_pairs.items():
            if (username, hash_value) in known_credentials:
                # Exact match found, write to output
                password = known_credentials[(username, hash_value)]
                f_out.write(f"{username}:{hash_value}:{password}\n")
            else:
                # Check if the username exists with a different hash
                matching_usernames = [key for key in known_credentials if key[0] == username]
                if matching_usernames:
                    # Warning for hash mismatch
                    print(f"Warning: Username '{username}' found, but hash does not match. Password may be different.")

# Main function to handle user input
def main():
    parser = argparse.ArgumentParser(description='Correlate credentials from known username:hash:password and username:hash')
    parser.add_argument('--known', required=True, help='File containing known credentials (username:hash:password)')
    parser.add_argument('--hashes', required=True, help='File containing username:hash pairs')
    parser.add_argument('--output', required=True, help='Output file (username:hash:password)')

    args = parser.parse_args()

    correlate_credentials(args.known, args.hashes, args.output)

# Entry point
if __name__ == '__main__':
    main()
