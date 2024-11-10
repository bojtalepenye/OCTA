# Offline Credential Stuffing Attack (OCTA)

<p align="center">
  <img src="https://github.com/user-attachments/assets/62578142-f120-42c0-8082-de9a7ba6a430" alt="Logo" width="260" height="260" />
</p>

# Overview
OCTA is a Python-based credential correlation tool that helps identify password reuse across different data sources. It compares known `username/email:hash:password` combinations against other credential lists to find matching pairs and potential vulnerabilities (password reuse).

## What is Offline Credential Stuffing?
- While Online Credential Stuffing involves actively testing stolen credentials against live services, Offline Credential Stuffing focuses on analyzing and correlating credential data from different breaches
- OCTA specifically helps correlate cracked `username/email:hash:password` combinations from one source against other credential lists to identify password reuse patterns
- This approach allows for identifying vulnerable accounts without actively attempting authentication

## Features

### Multiple Comparison Modes
- Single file comparison: Match one basefile against one specific target file
- Support for multiple basefiles and multiple match files
- Directory mode: Match one or more basefiles against all files in a directory


### Organized Output Structure
```
output_dir/
├── matches/
│   ├── per-list/
│   │   └── {basefile}_vs_{listfile}_matches.txt  
│   └── per-basefile/
│       └── {basefile}_all_matches.txt
└── mismatches/
    ├── per-list/
    │   └── {basefile}_vs_{listfile}_mismatches.txt
    └── per-basefile/
        └── {basefile}_all_mismatches.txt
```

### Comprehensive Result Tables
- All output is formatted in markdown tables
- Includes usernames/emails, hashes, passwords, and relevant comments
- Special handling for email usernames with potential password matches
- Organized by both individual comparisons and aggregated results

## Usage

### Basic Command Syntax
```bash
python3 OCTA.py [-h] -b BASE [BASE ...] [-m [MATCH ...]] [-d DIRECTORY] [-o OUTDIR]
```

### Help menu
```
$ python3 OCTA.py --help
usage: OCTA.py [-h] -b BASE [BASE ...] [-m [MATCH ...]] [-d DIRECTORY] [-o OUTDIR]

Offline Credential Stuffing Attack (OCTA): Multi-source credential matcher

options:
  -h, --help            show this help message and exit
  -b BASE [BASE ...], --base BASE [BASE ...]
                        One or more base credential files (username:hash:password)
  -m [MATCH ...], --match [MATCH ...]
                        One or more files to match against the basefiles
  -d DIRECTORY, --directory DIRECTORY
                        Directory containing multiple credential lists to match against the basefiles
  -o OUTDIR, --outdir OUTDIR
                        Output directory for match files (default: matches)
```

### Example Commands
```bash
# Match against specific files
python3 OCTA.py -b base.txt -m list1.txt list2.txt

# Match against all files in a directory
python3 OCTA.py -b base.txt -d credential_lists/

# Multiple basefiles with custom output directory
python3 OCTA.py -b base1.txt base2.txt -m list1.txt -o results/
```

## Understanding Mismatches
When a mismatch occurs between hashes for the same username or email address, it can be attributed to several factors, including:
- Different Hashing Algorithms: The two systems may employ different hashing algorithms, such as Argon2id, bcrypt, or Scrypt. Each algorithm produces different hash outputs even for the same input, which leads to mismatches.
- Salting: Salting is a technique used to enhance security by adding a unique value (the salt) to each password before hashing it. Usually, all salts are randomly generated for each user, therefore, most likely, if salting is used, the resulting hashes will differ, even for identical passwords.
- Password Variants: Users may change their passwords across different platforms, resulting in different hashes for the same username or email address.
- Encoding Differences: Variations in how characters are encoded (e.g., UTF-8 vs. ASCII) can also lead to differing hashes for the same password. Although this isn't very common.


> [!important]
> It's important to note that if a hash mismatch occurs but the email address remains the same, it is more likely that the password will still match. This is because users that use email addressess as usernames use that email specifically, and chances are, if that same email is used on a different platform/service/server the password is likely to be the same.

Credentials that don't match at all are ignored. There will plenty of them. However, and this is more vital, there will be also credentials that the script detects as mismatches. Here is what happens if a mismatch is detected. The mismatch files will be created under the `output-dir/mismatches` directory under these conditions:
- A username from the basefile matches a username from a matchfile, but the hash associated with that username differs from what is found in the basefile. The script identifies at least one such mismatch and adds the entry in the format `username:hash:password:comment` to the respective mismatch list. Each entry gets the list it came from as a comment.
- An email from the basefile matches an email from a matchfile. The script identifies at least one such mismatch and adds the entry in the format `username:hash:password:comment` to the respective mismatch list. Each entry gets the list it came from as a comment. Additionally in case of emails, the message:  `Email found as username. Password may match.` is also displayed.

## Processing Results
The script provides simple statistics after the processing of files is done:
- Total files processed
- Number of failed files
- Total matches found
- Total mismatches found

```bash
$ python3 OCTA.py -b base1 base2 -d dir -o output

Processing basefile: base1
Matching against base1: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 703.70it/s]

Processing basefile: base2
Matching against base2: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 1936.13it/s]

*** Processing Results ***
Files Processed        : 6
Failed Files           : 0
Total Matches found    : 1
Total Mismatches found : 30
```

### How output files are formatted: matches and mismatches
#### Matches (per-list, per-basefile)

```bash
kali@kali:~/OCTA/matches/matches/per-list$ cat base1_vs_list1_matches.txt
# Matches found in base1 vs list1

| Usernames/Emails   | Hashes                                                           | Passwords | Comments |
| ------------------ | ---------------------------------------------------------------- | --------- | -------- |
| user6              | e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683 | 6         |
| user7              | 7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451 | 7         |
| user8              | 2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3 | 8         |
| user9              | 19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7 | 9         |
| user10             | 4a44dc15364204a80fe80e9039455cc1608281820fe2b24f1e5233ade6af1dd5 | 10        |
| user11             | 4fc82b26aecb47d2868c4efbe3581732a3e7cbcc6c2efb32062c08170a05eeb8 | 11        |
| user12             | 6b51d431df5d7f141cbececcf79edf3dd861c3b4069f0b11661a3eefacbba918 | 12        |
| user13@example.com | 1db752922be16756086a43fab1791821f8861c9c8cd6a408b96ba6724796f2fd | 13        |
```

```bash
kali@kali:~/OCTA/matches/matches/per-basefile$ cat base1_all_matches.txt
# All matches found for base1

| Usernames/Emails   | Hashes                                                           | Passwords | Comments |
| ------------------ | ---------------------------------------------------------------- | --------- | -------- |
| user6              | e7f6c011776e8db7cd330b54174fd76f7d0216b612387a5ffcfb81e6f0919683 | 6         | list1    |
| user7              | 7902699be42c8a8e46fbbb4501726517e86b22c56a189f7625a6da49081b2451 | 7         | list1    |
| user8              | 2c624232cdd221771294dfbb310aca000a0df6ac8b66b696d90ef06fdefb64a3 | 8         | list1    |
| user9              | 19581e27de7ced00ff1ce50b2047e7a567c76b1cbaebabe5ef03f7c3017bb5b7 | 9         | list1    |
| user10             | 4a44dc15364204a80fe80e9039455cc1608281820fe2b24f1e5233ade6af1dd5 | 10        | list1    |
| user11             | 4fc82b26aecb47d2868c4efbe3581732a3e7cbcc6c2efb32062c08170a05eeb8 | 11        | list1    |
| user12             | 6b51d431df5d7f141cbececcf79edf3dd861c3b4069f0b11661a3eefacbba918 | 12        | list1    |
| user13@example.com | 1db752922be16756086a43fab1791821f8861c9c8cd6a408b96ba6724796f2fd | 13        | list1    |
```

#### Mismatches (per-list, per-basefile)

```bash
kali@kali:~/OCTA/output/mismatches/per-list$ cat base2_vs_list1_mismatches.txt
# Mismatches found in base2 vs list1

| Usernames/Emails | Hashes                                                       | Passwords     | Comments |
| ---------------- | ------------------------------------------------------------ | ------------- | -------- |
| user10           | $2b$05$Qyua7b4CrhKY9BBjsekE2e/anN/TtubAIUbGQmtmrRpZwl4TROka6 | Hash mismatch | list1    |
| user9            | $2b$05$yROOmo887vGtoC4zJns4/OgYg011lT0svR17DfU3IIlEvIKcKkGMa | Hash mismatch | list1    |
| user8            | $2b$05$VgNIx.7vD/aVlZDurePvpeozEwKp8epES0fOIyBP76I.vg.cUIsci | Hash mismatch | list1    |
| user7            | $2b$05$jH/rSwbhzIJXFkepO6sU3uLhOVPhCCqiPzUY18buOCzxpkasNjyPC | Hash mismatch | list1    |
| user6            | $2b$05$Jx3Z3ThH2r6j0CMDmImvdO3H0bHBTcgVSK590B.v5h9DUdznZpIqG | Hash mismatch | list1    |
| user5            | $2b$05$D4ZDmh79xps2Tw3rPoW5r.IWmWZXTkwTADwgNWopq8DJ1Y.pARHMC | Hash mismatch | list1    |
| user4            | $2b$05$ZLfWAb54DOiNBGZmm1vQ2eU3lpWEMErc3aDPyliZXYlvWeKzbG9s2 | Hash mismatch | list1    |
| user3            | $2b$05$zPjnCZM4KB4tLdN8wIZxuu3lhS0zSeOH8wR6EIkbSx9Wt8KIVAZ9W | Hash mismatch | list1    |
| user2            | $2b$05$ZBM9dycLgQ7rp5SPfg1O/eqArDzLNFk07kXqzVx9RV8kpa7av66rO | Hash mismatch | list1    |
| user1            | $2b$05$Oz48gQzsoRLZPCnhPoXwpuCoS5GEl1z3vjMspmKNqyXvAEfUYwM1q | Hash mismatch | list1    |
```


```bash
kali@kali:~/OCTA/output/mismatches/per-basefile$ cat base1_all_mismatches.txt
# All mismatches found for base1

| Usernames/Emails  | Hashes                                                       | Passwords     | Comments                                            |
| ----------------- | ------------------------------------------------------------ | ------------- | --------------------------------------------------- |
| user6@example.com | $2b$05$M8dmEEjm0Xa0d5To0Rj1E.QgbrZd83.vZrwQWv.HKm4K1Zyg/CXZO | Hash mismatch | list1: Email found as username. Password may match. |
| user3@example.com | $2b$05$E2GZcg7Iq0kL6ttoDcqhOeJiPhu1BbtEeWtsA37J.zWF0i3CE8HF2 | Hash mismatch | list1: Email found as username. Password may match. |
| user1@example.com | $2b$05$YFnYdu4YSMq61G.Dqimg7uqF5ciNeSpYJMsLN1pQjhGORk.aDP1wm | Hash mismatch | list1: Email found as username. Password may match. |
```

## Recommended Workflow
1. Use Hashcat to crack hashes from your initial dataset
2. Run OCTA to correlate the cracked credentials against other lists
3. Review both matches and mismatches, paying special attention to email-based usernames
4. Use the organized output structure to analyze results by source or across all sources

## Notes
- Always ensure you have proper authorization before analyzing credential data
- The script requires input files in the format `username/email:hash:password` for basefiles and `username/email:hash` for lists
- Output directories will be created automatically
- Existing output directories can be overwritten with confirmation
