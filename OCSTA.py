import argparse

# Load the known username:password pairs
def load_known_credentials(file_path):
    known_credentials = {}
    with open(file_path, 'r') as f:
        for line in f:
            username, password = line.strip().split(':')
            known_credentials[password] = username
    return known_credentials

# Load the hash:password pairs
def load_hashes(file_path):
    hash_passwords = {}
    with open(file_path, 'r') as f:
        for line in f:
            hash_value, password = line.strip().split(':')
            hash_passwords[hash_value] = password
    return hash_passwords

# Create a new file with the format username:hash:password
def correlate_credentials(known_file, hash_file, output_file):
    known_credentials = load_known_credentials(known_file)
    hash_passwords = load_hashes(hash_file)

    with open(output_file, 'w') as f_out:
        for hash_value, password in hash_passwords.items():
            if password in known_credentials:
                username = known_credentials[password]
                f_out.write(f"{username}:{hash_value}:{password}\n")

# Main function to handle user input
def main():
    parser = argparse.ArgumentParser(description='Correlate credentials from known passwords and hashes')
    parser.add_argument('--known', required=True, help='File containing known credentials (username:password)')
    parser.add_argument('--hashes', required=True, help='File containing hash:password pairs')
    parser.add_argument('--output', required=True, help='Output file (username:hash:password)')

    args = parser.parse_args()

    correlate_credentials(args.known, args.hashes, args.output)

# Entry point
if __name__ == '__main__':
    main()
