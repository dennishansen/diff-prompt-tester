import hashlib

def deterministic_hash(data):
    # Encode the input data as bytes if it's a string
    if isinstance(data, str):
        data = data.encode('utf-8')

    # Create a new SHA-256 hash object
    hasher = hashlib.sha256()

    # Update the hash object with the input data
    hasher.update(data)

    # Get the hexadecimal digest of the hash
    hash_hex = hasher.hexdigest()

    return hash_hex