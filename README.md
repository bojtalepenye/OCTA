# Offline Credential Stuffing Attack

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
$ python3 OCSTA.py --help
usage: OCSTA.py [-h] -b BASE -m MATCH [MATCH ...] [-o OUTDIR]

Multi-source credential matcher

options:
  -h, --help            show this help message and exit
  -b BASE, --base BASE  Base credential file (username:hash:password)
  -m MATCH [MATCH ...], --match MATCH [MATCH ...]
                        One or more files to match against the base file
  -o OUTDIR, --outdir OUTDIR
                        Output directory for match files (default: matches)
```

#### Example command:
```bash
python OCSTA.py -b base -m list1
```

### Recommended Workflow
- Use Hashcat to try and crack as many hashes as you can from a list.
- Run this script to correlate the cracked `username/email:hash:password` pairs with another list containing usernames and unknown hashes.
- The output file will give you a list of matched credentials (`username:hash:password`) that can be used for further analysis.

## Features of this script
The script is essentially a multi-source credential matcher, because it not only supports checking credentials against one list, but multiple. It takes one basefile as an input `-b` and matches the basefile against the specified matchfiles. You can give matchfiles or lists to OCSTA with `-m` or `--match`. You are able to define as many as you like rigth after one another. Like so:

```bash
python3 OCSTA.py -b base -m list1 list2 list3
```

### Folder Organization


### The mismatches you may get
When a mismatch occurs between hashes for the same username or email address, it can be attributed to several factors, including:
- Different Hashing Algorithms: The two systems may employ different hashing algorithms, such as SHA-256, bcrypt, or Argon2. Each algorithm produces different hash outputs even for the same input, which leads to mismatches.
- Salting: Salting is a technique used to enhance security by adding a unique value (the salt) to each password before hashing it. Usually, all salts are randomly generated for each user, therefore, most likely, if salting is used, the resulting hashes will differ, even for identical passwords.
- Password Variants: Users may change their passwords across different platforms, resulting in different hashes for the same username or email address.
- Encoding Differences: Variations in how characters are encoded (e.g., UTF-8 vs. ASCII) can also lead to differing hashes for the same password.

> [!important]
> It's important to note that if a hash mismatch occurs but the email address remains the same, it is more likely that the password will still match.
> This is because users that use email addressess as usernames use that email specifically, and chances are if that same email is used on a different platform/service/server the password is the same.

### Mismatches and comments
There will be times when the script will find mismatches. In that case, under the `folder/warnings` a `base_vs_list_warnings.txt` will be created.
This file will be created when:
    - A username from the basefile matches a username from a matchfile, but the hash associated with that username differs from what is found in the basefile. The script identifies at least one such mismatch and adds the entry in the format `username:hash:password` to the respective warnings list.
- A username from the basefile matches a username from a matchfile, but the hash differs, and the username contains an "@" character (indicating that it is likely an email address). The script adds the entry to the warnings file and appends the comment: `Email found as username. Password may match.`
