from bson import ObjectId
from pymongo import MongoClient
from database import db



def base36_encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')
 
    base36 = ''
    sign = ''
 
    if number < 0:
        sign = '-'
        number = -number
 
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
 
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
 
    return sign + base36
 
def base36_decode(number):
    """Converts a base36 string to an integer."""
    return int(number, 36)

def encode(obj_id: ObjectId) -> tuple[int, int]:
    """
    Encodes a BSON ObjectId:
    - 4 bytes: timestamp
    - 3 bytes: machine identifier
    - 2 bytes: process id
    - 3 bytes: counter
    
    into:
    - timestamp (22 bits)
    - counter (16 bits)
    """
    bin_data = obj_id.binary

    timestamp_truncated = int.from_bytes(bin_data[:4], 'big') & 0x3FFFFF  # 22 bits
    counter_truncated = int.from_bytes(bin_data[9:12], 'big') & 0xFFFF  # 16 bits
    
    return timestamp_truncated, counter_truncated

def to_str(counter: int, timestamp: int) -> str:
    """
    Converts the binary representation of the counter and timestamp to a string in base36
    """
    # Convert the integers to base36 strings
    c_base36 = base36_encode(counter)
    t_base36 = base36_encode(timestamp)

    return f"{t_base36}-{c_base36}"

def from_str(encoded: str) -> tuple[str, str]:
    """
    Converts the base36 string representation back to the binary representation 
    of the counter and timestamp
    """
    # Split the encoded string into timestamp and counter parts
    t_str, c_str = encoded.split('-')
    
    # Convert the base36 strings back to integers
    t_int = base36_decode(t_str)
    c_int = base36_decode(c_str)

    # Convert the integers to binary strings
    t_bin = bin(t_int)[2:].zfill(22)  # 22 bits for timestamp
    c_bin = bin(c_int)[2:].zfill(16)  # 16 bits for counter

    return t_bin, c_bin

def get_object_id(timestamp: int, counter: int, collection_name="users") -> ObjectId:
    """
    Searches for an ObjectId in the database that matches the given timestamp and counter.
    
    Args:
        timestamp: The timestamp value (22 bits)
        counter: The counter value (16 bits)
        collection_name: The collection to search in (defaults to "users")
        
    Returns:
        The matching ObjectId if found, otherwise None
    """
    # Get database connection
    db = db.db.db
    collection = db[collection_name]
    
    # Convert counter to bytes for the query
    counter_bytes = counter.to_bytes(2, 'big')

    # Query to find documents where the ObjectId ends with the counter bytes
    query = {
        "$expr": {
            "$regexMatch": {
                "input": { "$toString": "$_id" },
                "regex": f"^[0-9a-f]{{20}}{counter_bytes.hex()}$",
            }
        } 
    }
    
    # Search for matching documents
    response = collection.find(query)
    for doc in response:
        # Check if the document's ObjectId timestamp matches our timestamp
        if int.from_bytes(doc["_id"].binary[:4], 'big') & 0x3FFFFF == timestamp:
            return doc["_id"]
    
    return None