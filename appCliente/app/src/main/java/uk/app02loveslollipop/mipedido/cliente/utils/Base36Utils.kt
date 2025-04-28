package uk.app02loveslollipop.mipedido.cliente.utils

import java.math.BigInteger

/**
 * Utility class for Base36 encoding operations
 */
object Base36Utils {
    private const val BASE36_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    /**
     * Converts a hexadecimal MongoDB ObjectID to a Base36 string representation
     * @param objectId The MongoDB ObjectID string (typically 24 hex characters)
     * @param length The desired length of the output string (default: 6)
     * @return A Base36 encoded string of the requested length
     */
    fun encodeOrderId(objectId: String, length: Int = 6): String {
        try {
            // Convert hex string to BigInteger
            val bigInt = BigInteger(objectId, 16)
            
            // Convert to base36 string
            val base36 = bigInt.toString(36).uppercase()
            
            // Ensure the result has exactly the specified length
            return when {
                base36.length > length -> base36.takeLast(length)
                base36.length < length -> base36.padStart(length, '0')
                else -> base36
            }
        } catch (e: Exception) {
            // For any parsing errors, return a fallback string
            return objectId.take(length).padEnd(length, '0').uppercase()
        }
    }
    
    /**
     * Converts a decimal number to a Base36 string representation
     * @param number The decimal number to convert
     * @param length The desired length of the output string
     * @return A Base36 encoded string of the requested length
     */
    fun encodeNumber(number: Long, length: Int = 6): String {
        val base36 = number.toString(36).uppercase()
        
        // Ensure the result has exactly the specified length
        return when {
            base36.length > length -> base36.takeLast(length)
            base36.length < length -> base36.padStart(length, '0')
            else -> base36
        }
    }
    
    /**
     * Extension function to convert Long to Base36 string
     */
    fun Long.toBase36(length: Int = 6): String {
        return encodeNumber(this, length)
    }
    
    /**
     * Extension function to convert String (assumed to be hex) to Base36 string
     */
    fun String.hexToBase36(length: Int = 6): String {
        return encodeOrderId(this, length)
    }
}