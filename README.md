# Offline Credential STuffing Attack

# Overview
This script allows you to correlate known `username:password` pairs with `username:hash` pairs, producing an output in the format username:hash:password.
- Online Credential Stuffing Attack is a type of cyber attack where attackers use stolen username and password combinations (often obtained from data breaches) to gain unauthorized access to user accounts on various online platform.
- Offline Credential Stuffing Attacks on the other hand, deal with checking/correlating/corresponding already cracked username:password pairs leaked from one srouce against another, once the latter has been cracked.
This way it's easy to identify vulnarable accounts that have been reusing passwords on multiple platforms.

### Why Not Crack Passwords in the Script?
While some offline credential stuffing attacks use custom-built crackers in their scripts, this is inefficient and slow. Hashcat, on the other hand, is designed to efficiently crack hashes and is highly optimized for various hash functions. By using this Python script for correlation and leaving the cracking to Hashcat, you ensure that your credential stuffing workflow is much faster and more reliable.

### Usage
Run the following command to display the help menu:
```bash
python3 OCSTA.py --help
usage: test.py [-h] --known KNOWN --hashes HASHES --output OUTPUT

Correlate credentials from known passwords and hashes

options:
  -h, --help       show this help message and exit
  --known KNOWN    File containing known credentials (username:password)
  --hashes HASHES  File containing username:hash pairs
  --output OUTPUT  Output file (username:hash:password)
```

#### Example command:
```bash
python OCSTA.py --known known_credentials.txt --hashes hashes.txt --output correlated_credentials.txt
```

### Recommended Workflow
- Use Hashcat to try and crack as many hashes as you can from your list.
- Run this script to correlate the cracked passwords with the known usernames and passwords.
- The output file will give you a list of matched credentials (username:hash:password) that can be used for further analysis.
