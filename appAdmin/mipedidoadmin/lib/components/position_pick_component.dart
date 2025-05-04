import 'package:fluent_ui/fluent_ui.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../api/nominatim_api_connector.dart';

class PositionPickComponent extends StatefulWidget {
  final void Function(double lat, double lon) onPositionSelected;
  const PositionPickComponent({Key? key, required this.onPositionSelected})
    : super(key: key);

  @override
  State<PositionPickComponent> createState() => _PositionPickComponentState();
}

class _PositionPickComponentState extends State<PositionPickComponent> {
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _streetController = TextEditingController();
  final TextEditingController _cityController = TextEditingController();
  final TextEditingController _stateController = TextEditingController();
  final TextEditingController _countryController = TextEditingController();
  final TextEditingController _postalCodeController = TextEditingController();
  final NominatimApiConnector _nominatim = NominatimApiConnector();
  List<Map<String, dynamic>> _searchResults = [];
  LatLng? _selectedPosition;
  bool _loading = false;
  String? _error;
  String _queryType = 'Normal'; // 'Normal' or 'Structured'

  Future<void> _searchNormal() async {
    setState(() {
      _loading = true;
      _error = null;
      _searchResults = [];
    });
    try {
      final results = await _nominatim.searchAddress(
        _addressController.text,
        limit: 5,
      );
      setState(() {
        _searchResults = results;
        if (results.isNotEmpty) {
          final lat = double.parse(results[0]['lat']);
          final lon = double.parse(results[0]['lon']);
          _selectedPosition = LatLng(lat, lon);
        }
      });
    } catch (e) {
      setState(() {
        _error = 'Error: [31m${e.toString()}[0m';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  Future<void> _searchStructured() async {
    setState(() {
      _loading = true;
      _error = null;
      _searchResults = [];
    });
    try {
      final results = await _nominatim.searchAddressStructured(
        street: _streetController.text,
        city: _cityController.text,
        state: _stateController.text,
        country: _countryController.text,
        postalCode: _postalCodeController.text,
        limit: 5,
      );
      setState(() {
        _searchResults = results;
        if (results.isNotEmpty) {
          final lat = double.parse(results[0]['lat']);
          final lon = double.parse(results[0]['lon']);
          _selectedPosition = LatLng(lat, lon);
        }
      });
    } catch (e) {
      setState(() {
        _error = 'Error: [31m${e.toString()}[0m';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  void _selectResult(Map<String, dynamic> result) {
    final lat = double.parse(result['lat']);
    final lon = double.parse(result['lon']);
    setState(() {
      _selectedPosition = LatLng(lat, lon);
    });
    widget.onPositionSelected(lat, lon);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('Tipo de búsqueda:'),
            const SizedBox(width: 12),
            ComboBox<String>(
              value: _queryType,
              items: const [
                ComboBoxItem(value: 'Normal', child: Text('Normal')),
                ComboBoxItem(value: 'Structured', child: Text('Estructurada')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _queryType = value;
                    _searchResults = [];
                    _error = null;
                    _selectedPosition = null;
                    // Reset all input fields
                    _addressController.clear();
                    _streetController.clear();
                    _cityController.clear();
                    _stateController.clear();
                    _countryController.clear();
                    _postalCodeController.clear();
                  });
                }
              },
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (_queryType == 'Normal') ...[
          Row(
            children: [
              SizedBox(
                width: 220,
                child: TextBox(
                  controller: _addressController,
                  placeholder: 'Dirección/Lugar (libre)',
                ),
              ),
              const SizedBox(width: 8),
              Button(
                onPressed: _loading ? null : _searchNormal,
                child: const Icon(FluentIcons.search),
              ),
            ],
          ),
        ] else ...[
          Row(
            children: [
              SizedBox(
                width: 160,
                child: TextBox(
                  controller: _streetController,
                  placeholder: 'Calle y número',
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                width: 120,
                child: TextBox(
                  controller: _cityController,
                  placeholder: 'Ciudad',
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                width: 140,
                child: TextBox(
                  controller: _stateController,
                  placeholder: 'Estado/Provincia',
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              SizedBox(
                width: 120,
                child: TextBox(
                  controller: _countryController,
                  placeholder: 'País',
                ),
              ),
              const SizedBox(width: 8),
              SizedBox(
                width: 120,
                child: TextBox(
                  controller: _postalCodeController,
                  placeholder: 'Código Postal',
                ),
              ),
              const SizedBox(width: 8),
              Button(
                onPressed: _loading ? null : _searchStructured,
                child: const Icon(FluentIcons.search),
              ),
            ],
          ),
        ],
        if (_loading) ...[const SizedBox(height: 8), const ProgressRing()],
        if (_error != null) ...[
          const SizedBox(height: 8),
          InfoBar(
            title: const Text('Error'),
            content: Text(_error!),
            severity: InfoBarSeverity.error,
            isLong: true,
          ),
        ],
        if (_searchResults.isNotEmpty)
          Container(
            height: 120,
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[120]),
              borderRadius: BorderRadius.circular(4),
            ),
            child: ListView.builder(
              itemCount: _searchResults.length,
              itemBuilder: (context, index) {
                final result = _searchResults[index];
                return ListTile.selectable(
                  title: Text(result['display_name'] ?? ''),
                  selected:
                      _selectedPosition != null &&
                      double.parse(result['lat']) ==
                          _selectedPosition!.latitude &&
                      double.parse(result['lon']) ==
                          _selectedPosition!.longitude,
                  onSelectionChange: (selected) {
                    if (selected) _selectResult(result);
                  },
                );
              },
            ),
          ),
        if (_selectedPosition != null)
          Container(
            height: 250,
            margin: const EdgeInsets.only(top: 12),
            child: FlutterMap(
              options: MapOptions(
                initialCenter: _selectedPosition!,
                initialZoom: 16.0,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                ),
                MarkerLayer(
                  markers: [
                    Marker(
                      width: 40.0,
                      height: 40.0,
                      point: _selectedPosition!,
                      child: Icon(
                        FluentIcons.location,
                        color: Colors.red,
                        size: 40,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
      ],
    );
  }
}
