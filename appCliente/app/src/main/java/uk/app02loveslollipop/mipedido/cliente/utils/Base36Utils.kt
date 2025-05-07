package uk.app02loveslollipop.mipedido.cliente.utils

import uk.app02loveslollipop.mipedido.cliente.utils.Base36Utils.encodeObjectIdToShortFormat
import java.math.BigInteger

/**
 * Utility class for Base36 encoding operations
 */
object Base36Utils {
    private const val BASE36_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    /**
     * Encodes a BSON ObjectId string into its truncated timestamp and counter parts.
     * ObjectId structure:
     * - 4 bytes: timestamp
     * - 5 bytes: machine identifier + process id
     * - 3 bytes: counter
     *
     * Encoding takes:
     * - Lower 22 bits of the timestamp
     * - Lower 16 bits of the counter
     *
     * @param objectIdHex The MongoDB ObjectID string (24 hex characters).
     * @return A Pair containing the truncated timestamp (Int) and counter (Int), or null if invalid input.
     */
    private fun encodeObjectIdParts(objectIdHex: String): Pair<Int, Int>? {
        if (objectIdHex.length != 24) return null

        return try {
            // Extract timestamp (first 8 hex chars = 4 bytes)
            val timestampHex = objectIdHex.substring(0, 8)
            val timestamp = timestampHex.toLong(16).toInt() // Convert hex to Long then Int
            val timestampTruncated = timestamp and 0x3FFFFF // Keep lower 22 bits

            // Extract counter (last 6 hex chars = 3 bytes)
            val counterHex = objectIdHex.substring(18, 24)
            val counter = counterHex.toLong(16).toInt() // Convert hex to Long then Int
            val counterTruncated = counter and 0xFFFF // Keep lower 16 bits

            Pair(timestampTruncated, counterTruncated)
        } catch (e: NumberFormatException) {
            null // Handle invalid hex characters
        }
    }

    /**
     * Converts an integer to a base36 string.
     * @param number The integer to convert.
     * @return The base36 string representation.
     */
    private fun intToBase36(number: Int): String {
        if (number < 0) throw IllegalArgumentException("Number must be non-negative")
        if (number == 0) return BASE36_CHARS[0].toString()

        var num = number
        val base = BASE36_CHARS.length
        val sb = StringBuilder()

        while (num > 0) {
            sb.insert(0, BASE36_CHARS[num % base])
            num /= base
        }
        return sb.toString()
    }

    /**
     * Encodes a MongoDB ObjectId string into a shortened Base36 string format "T-C".
     * Where T is the Base36 of the truncated timestamp and C is the Base36 of the truncated counter.
     * Each part is padded with leading zeros to ensure a minimum of 4 characters.
     *
     * @param objectIdHex The MongoDB ObjectID string (24 hex characters).
     * @return The shortened Base36 encoded string (e.g., "ABC0-123D"), or the original ID if encoding fails.
     */
    fun encodeObjectIdToShortFormat(objectIdHex: String): String {
        val parts = encodeObjectIdParts(objectIdHex)
        return if (parts != null) {
            val (timestampTruncated, counterTruncated) = parts
            val timestampBase36 = intToBase36(timestampTruncated).padStart(4, '0')
            val counterBase36 = intToBase36(counterTruncated).padStart(4, '0')
            "$timestampBase36-$counterBase36"
        } else {
            // Fallback or error handling: return original or a placeholder
            objectIdHex // Or consider throwing an exception or returning a specific error string
        }
    }

    /**
     * Converts a hexadecimal MongoDB ObjectID to a Base36 string representation (LEGACY - uses full ID).
     * @param objectId The MongoDB ObjectID string (typically 24 hex characters)
     * @param length The desired length of the output string (default: 6)
     * @return A Base36 encoded string of the requested length
     */
    @Deprecated("Use encodeObjectIdToShortFormat for the new encoding", ReplaceWith("encodeObjectIdToShortFormat(objectId)"))
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
    @Deprecated("Use encodeObjectIdToShortFormat for the new encoding", ReplaceWith("encodeObjectIdToShortFormat(this)"))
    fun String.hexToBase36(length: Int = 6): String {
        return encodeObjectIdToShortFormat(this)
    }
}