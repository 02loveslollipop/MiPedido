import 'dart:math';

/// Utility class for Base36 encoding and decoding operations
class Base36Utils {
  static const String _base36Chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  /// Converts a hexadecimal MongoDB ObjectID to a Base36 string representation
  /// @param objectId The MongoDB ObjectID string (typically 24 hex characters)
  /// @param length The desired length of the output string (default: 6)
  /// @return A Base36 encoded string of the requested length
  static String encodeOrderId(String objectId, {int length = 6}) {
    try {
      // Convert hex string to BigInt
      final bigInt = BigInt.parse(objectId, radix: 16);

      // Convert to base36 string
      final base36 = _bigIntToBase36(bigInt).toUpperCase();

      // Ensure the result has exactly the specified length
      if (base36.length > length) {
        return base36.substring(base36.length - length);
      } else if (base36.length < length) {
        return base36.padLeft(length, '0');
      }
      return base36;
    } catch (e) {
      // For any parsing errors, return a fallback string
      return objectId
          .substring(0, objectId.length < length ? objectId.length : length)
          .padRight(length, '0')
          .toUpperCase();
    }
  }

  /// Converts a decimal number to a Base36 string representation
  /// @param number The decimal number to convert
  /// @param length The desired length of the output string
  /// @return A Base36 encoded string of the requested length
  static String encodeNumber(int number, {int length = 6}) {
    final base36 = _intToBase36(number).toUpperCase();

    // Ensure the result has exactly the specified length
    if (base36.length > length) {
      return base36.substring(base36.length - length);
    } else if (base36.length < length) {
      return base36.padLeft(length, '0');
    }
    return base36;
  }

  /// Decodes a Base36 string to its decimal (integer) value
  /// @param base36String The Base36 string to decode
  /// @return The decimal value represented by the Base36 string
  static int decodeToInt(String base36String) {
    base36String = base36String.toUpperCase();
    int result = 0;

    for (int i = 0; i < base36String.length; i++) {
      final charValue = _base36Chars.indexOf(base36String[i]);
      if (charValue == -1) {
        throw FormatException('Invalid Base36 character: ${base36String[i]}');
      }

      result = result * 36 + charValue;
    }

    return result;
  }

  /// Decodes a Base36 string to a hexadecimal string (for ObjectID conversion)
  /// @param base36String The Base36 string to decode
  /// @return The hexadecimal string represented by the Base36 string
  static String decodeToHex(String base36String) {
    try {
      final BigInt value = _base36ToBigInt(base36String);
      String hex = value.toRadixString(16);
      // MongoDB ObjectIDs are typically 24 characters
      return hex.padLeft(24, '0');
    } catch (e) {
      throw FormatException('Failed to decode Base36 string: $base36String');
    }
  }

  // Helper methods
  static String _intToBase36(int number) {
    if (number == 0) return '0';

    String result = '';
    int value = number;

    while (value > 0) {
      result = _base36Chars[value % 36] + result;
      value ~/= 36;
    }

    return result;
  }

  static String _bigIntToBase36(BigInt number) {
    if (number == BigInt.zero) return '0';

    String result = '';
    final base = BigInt.from(36);
    BigInt value = number;

    while (value > BigInt.zero) {
      final remainder = (value % base).toInt();
      result = _base36Chars[remainder] + result;
      value = value ~/ base;
    }

    return result;
  }

  static BigInt _base36ToBigInt(String base36String) {
    base36String = base36String.toUpperCase();
    BigInt result = BigInt.zero;
    final base = BigInt.from(36);

    for (int i = 0; i < base36String.length; i++) {
      final charValue = _base36Chars.indexOf(base36String[i]);
      if (charValue == -1) {
        throw FormatException('Invalid Base36 character: ${base36String[i]}');
      }

      result = result * base + BigInt.from(charValue);
    }

    return result;
  }
}

// Extension methods to make usage more convenient
extension Base36StringExtension on String {
  /// Convert a hexadecimal string to Base36
  String hexToBase36({int length = 6}) {
    return Base36Utils.encodeOrderId(this, length: length);
  }

  /// Decode a Base36 string to an integer
  int fromBase36toInt() {
    return Base36Utils.decodeToInt(this);
  }

  /// Decode a Base36 string to a hexadecimal string
  String fromBase36toHex() {
    return Base36Utils.decodeToHex(this);
  }
}

extension Base36IntExtension on int {
  /// Convert an integer to Base36
  String toBase36({int length = 6}) {
    return Base36Utils.encodeNumber(this, length: length);
  }
}
