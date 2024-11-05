# Offline Credential STuffing Attack

# Overview
This script allows you to correlate known `username/email:hash:password` pairs with `username:hash` pairs, producing an output in the format `username:hash:password`.
- Online Credential Stuffing Attack is a type of cyber attack where attackers use stolen username and password combinations (often obtained from data breaches) to gain unauthorized access to user accounts on various online platform.
- Offline Credential Stuffing Attacks on the other hand, deal with checking/correlating/corresponding already cracked `username/email:hash:password` pairs leaked from one srouce against another, once the latter has been cracked.
This way it's easy to identify vulnarable accounts that have been reusing passwords on multiple platforms.

### Why Not Crack Passwords in the Script?
While some offline credential stuffing attacks use custom-built crackers in their scripts, this is inefficient and slow. Hashcat, on the other hand, is designed to efficiently crack hashes and is highly optimized for various hash functions. By using this Python script for correlation and leaving the cracking to Hashcat, you ensure that your credential stuffing workflow is much faster and more reliable.

### Usage
Run the following command to display the help menu:
```bash
python3 OCSTA.py --help
usage: OCSTA.py [-h] --known KNOWN --hashes HASHES --output OUTPUT

Correlate credentials from known username:hash:password and username:hash

options:
  -h, --help       show this help message and exit
  --known KNOWN    File containing known credentials (username:hash:password)
  --hashes HASHES  File containing username:hash pairs
  --output OUTPUT  Output file (username:hash:password)
```

#### Example command:
```bash
python OCSTA.py --known known_credentials.txt --hashes hashes.txt --output correlated_credentials.txt
```

### Recommended Workflow
- Use Hashcat to try and crack as many hashes as you can from a list.
- Run this script to correlate the cracked `username/email:hash:password` pairs with another list containing usernames and unknown hashes.
- The output file will give you a list of matched credentials (`username:hash:password`) that can be used for further analysis.

### The mismatches you may get
When a mismatch occurs between hashes for the same username or email address, it can be attributed to several factors, including:
- Different Hashing Algorithms: The two systems may employ different hashing algorithms, such as SHA-256, bcrypt, or Argon2. Each algorithm produces different hash outputs even for the same input, which leads to mismatches.
- Salting: Salting is a technique used to enhance security by adding a unique value (the salt) to each password before hashing it. Usually, all salts are randomly generated for each user, therefore, most likely, if salting is used, the resulting hashes will differ, even for identical passwords.
- Password Variants: Users may change their passwords across different platforms, resulting in different hashes for the same username or email address.
- Encoding Differences: Variations in how characters are encoded (e.g., UTF-8 vs. ASCII) can also lead to differing hashes for the same password.

> [!important]
> It's important to note that if a hash mismatch occurs but the email address remains the same, it is more likely that the password will still match.
> This is because users that use email addressess as usernames use that email specifically, and chances are if that same email is used on a different platform/service/server the password is the same.

### How are mismatch files created
The two files, hash_mismatch.txt and email_hash_mismatch.txt, will be created under the following conditions:
    hash_mismatch.txt:
        This file will be created when:
            A username from the `hashes` matches a username from the `known` file, but the hash associated with that username differs from what is found in `known`.
            The script identifies at least one such mismatch and adds the entry in the format `username:hash:password` to the list mismatch_entries.
            At the end of processing, if mismatch_entries is not empty, the script writes its contents to `hash_mismatch.txt`.
    email_hash_mismatch.txt:
        This file will be created when:
            A username from the `hashes` file matches a username from the `known` file, but the hash differs, and the username contains an "@" character (indicating that it is likely an email address).
            The script adds the entry to the email_mismatch_entries list.
            At the end of processing, if email_mismatch_entries is not empty, the script writes its contents to `email_hash_mismatch.txt`.
