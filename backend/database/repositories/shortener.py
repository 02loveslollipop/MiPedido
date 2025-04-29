from bson import ObjectId
from typing import Optional, Dict, Any
from database import db

class ShortenerRepository:
    
    @staticmethod
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
     
    @staticmethod
    def base36_decode(number):
        """Converts a base36 string to an integer."""
        return int(number, 36)

    @staticmethod
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

    @staticmethod
    def to_str(counter: int, timestamp: int) -> str:
        """
        Converts the binary representation of the counter and timestamp to a string in base36
        """
        # Convert the integers to base36 strings
        c_base36 = ShortenerRepository.base36_encode(counter)
        t_base36 = ShortenerRepository.base36_encode(timestamp)

        return f"{t_base36}-{c_base36}"

    @staticmethod
    def from_str(encoded: str) -> tuple[str, str]:
        """
        Converts the base36 string representation back to the binary representation 
        of the counter and timestamp
        """
        if not isinstance(encoded, str):
            raise TypeError('encoded must be a string')
        # Split the encoded string into timestamp and counter parts
        t_str, c_str = encoded.split('-')
        
        # Convert the base36 strings back to integers
        t_int = ShortenerRepository.base36_decode(t_str)
        c_int = ShortenerRepository.base36_decode(c_str)

        # Convert the integers to binary strings
        t_bin = bin(t_int)[2:].zfill(22)  # 22 bits for timestamp
        c_bin = bin(c_int)[2:].zfill(16)  # 16 bits for counter

        return t_bin, c_bin

    @classmethod
    async def get_object_id(cls, short_code: str, collection_name: str = "orders") -> Dict[str, str]:
        """
        Decode a base36 shortened code back to a MongoDB ObjectID.
        
        Args:
            short_code: The shortened code in format "timestamp-counter" (both in base36)
            collection_name: The collection to search in (defaults to "users")
            
        Returns:
            A dictionary containing the object_id if found, otherwise None
        """
        try:
            # Parse the base36 encoded string and convert to binary values
            t_bin_decoded, c_bin_decoded = cls.from_str(short_code)
            timestamp = int(t_bin_decoded, 2)
            counter = int(c_bin_decoded, 2)
            
            # Get database connection
            collection = db.db.db[collection_name]
            
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
            cursor = collection.find(query)
            
            async for doc in cursor:
                # Check if the document's ObjectId timestamp matches our timestamp
                if int.from_bytes(doc["_id"].binary[:4], 'big') & 0x3FFFFF == timestamp:
                    return {"object_id": str(doc["_id"])}
            
            raise ValueError(f"No matching ObjectId found for the short code {short_code}")
            
        except Exception as e:
            raise e

    @classmethod
    async def create_short_code(cls, obj_id: str, collection_name: str = "users") -> Dict[str, str]:
        """
        Create a shortened code from a MongoDB ObjectID.
        
        Args:
            obj_id: The ObjectID as a string
            collection_name: The collection to verify the ObjectID exists in
            
        Returns:
            A dictionary containing the shortened code
        """
        try:
            # Convert string to ObjectId
            object_id = ObjectId(obj_id)
            
            # Verify object exists in the collection
            collection = db.db.db[collection_name]
            doc = await collection.find_one({"_id": object_id})
            
            if not doc:
                raise ValueError(f"Object with ID {obj_id} not found in collection {collection_name}")
            
            # Encode the ObjectId
            timestamp, counter = cls.encode(object_id)
            
            # Convert to string representation
            short_code = cls.to_str(counter, timestamp)
            
            return {"short_code": short_code}
            
        except Exception as e:
            raise e