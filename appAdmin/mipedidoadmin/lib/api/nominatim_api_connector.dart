import 'dart:convert';
import 'package:http/http.dart' as http;

class NominatimApiConnector {
  static const String _baseUrl = 'https://nominatim.openstreetmap.org/search';

  /// Geocode an address using Nominatim (returns a list of results)
  Future<List<Map<String, dynamic>>> searchAddress(
    String query, {
    int limit = 5,
  }) async {
    final uri = Uri.parse(_baseUrl).replace(
      queryParameters: {
        'q': query,
        'format': 'json',
        'limit': limit.toString(),
        'addressdetails': '1',
      },
    );
    final response = await http.get(
      uri,
      headers: {
        'Accept': 'application/json',
        'User-Agent':
            'MiPedidoApp/1.0 (your@email.com)', // Replace with your contact info
      },
    );
    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      // Extract city, country, state, and postal code from address
      return data.map<Map<String, dynamic>>((item) {
        final address = item['address'] ?? {};
        return {
          ...item,
          'city':
              address['city'] ??
              address['town'] ??
              address['village'] ??
              address['hamlet'],
          'country': address['country'],
          'state': address['state'],
          'postal_code': address['postcode'],
        };
      }).toList();
    } else {
      throw Exception('Failed to fetch geocoding results');
    }
  }

  /// Geocode an address using Nominatim structured query (returns a list of results)
  Future<List<Map<String, dynamic>>> searchAddressStructured({
    String? street,
    String? city,
    String? state,
    String? country,
    String? postalCode,
    int limit = 5,
  }) async {
    final params = <String, String>{
      'format': 'json',
      'limit': limit.toString(),
      'addressdetails': '1',
    };
    if (street != null && street.isNotEmpty) params['street'] = street;
    if (city != null && city.isNotEmpty) params['city'] = city;
    if (state != null && state.isNotEmpty) params['state'] = state;
    if (country != null && country.isNotEmpty) params['country'] = country;
    if (postalCode != null && postalCode.isNotEmpty)
      params['postalcode'] = postalCode;

    final uri = Uri.parse(_baseUrl).replace(queryParameters: params);
    final response = await http.get(
      uri,
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'MiPedidoApp/1.0 (your@email.com)',
      },
    );
    if (response.statusCode == 200) {
      final List data = json.decode(response.body);
      return data.map<Map<String, dynamic>>((item) {
        final address = item['address'] ?? {};
        return {
          ...item,
          'city':
              address['city'] ??
              address['town'] ??
              address['village'] ??
              address['hamlet'],
          'country': address['country'],
          'state': address['state'],
          'postal_code': address['postcode'],
        };
      }).toList();
    } else {
      throw Exception('Failed to fetch geocoding results');
    }
  }
}
