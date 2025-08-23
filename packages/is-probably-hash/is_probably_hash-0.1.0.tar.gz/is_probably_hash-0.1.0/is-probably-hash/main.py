import re

# Known hash lengths by algorithm
HASH_LENGTHS = {
    "MD5": 32,
    "SHA1": 40,
    "SHA256": 64,
    "SHA512": 128
}

HEX_PATTERN = re.compile(r"^[a-fA-F0-9]+$")


def is_probably_hash(s: str):
    """
    Check if the string is a potential hash based on length and allowed characters.
    Returns: (bool, algorithm or None)
    """
    s = s.strip()

    if HEX_PATTERN.fullmatch(s):
        for algo, length in HASH_LENGTHS.items():
            if len(s) == length:
                return True, algo
        return True, None
    return False, None


def hello():
    print("mytool hash detector is ready! Use is_probably_hash() to check strings.")


if __name__ == "__main__":
    test_strings = [
        "5d41402abc4b2a76b9719d911017c592",  # MD5
        "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",  # SHA1
        "notahash"
    ]
    for s in test_strings:
        result, algo = is_probably_hash(s)
        if result:
            print(f"{s} looks like a hash ({algo or 'Unknown'})")
        else:
            print(f"{s} is NOT a hash")
