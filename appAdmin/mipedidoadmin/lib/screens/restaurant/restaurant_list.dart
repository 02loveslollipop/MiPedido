import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';

class RestaurantListScreen extends StatefulWidget {
  const RestaurantListScreen({super.key});

  @override
  State<RestaurantListScreen> createState() => _RestaurantListScreenState();
}

class _RestaurantListScreenState extends State<RestaurantListScreen> {
  bool _isLoading = true;
  List<dynamic> _restaurants = [];
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadRestaurants();
  }

  Future<void> _loadRestaurants() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.listRestaurants();

    setState(() {
      _isLoading = false;
      if (result['success']) {
        _restaurants = result['restaurants'];
      } else {
        _errorMessage = result['error'] ?? 'Failed to load restaurants';
      }
    });
  }

  void showSnackbar(BuildContext context, InfoBar infoBar) {
    displayInfoBar(
      context,
      builder: (context, close) {
        return infoBar;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      header: const PageHeader(title: Text('Listado de Restaurantes')),
      content:
          _isLoading
              ? const Center(child: ProgressRing())
              : _errorMessage != null
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                  action: FilledButton(
                    child: const Text('Reintentar'),
                    onPressed: _loadRestaurants,
                  ),
                ),
              )
              : _restaurants.isEmpty
              ? const Center(child: Text('No hay restaurantes registrados'))
              : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  const SizedBox(height: 12),
                  CommandBar(
                    mainAxisAlignment: MainAxisAlignment.end,
                    primaryItems: [
                      CommandBarButton(
                        icon: const Icon(FluentIcons.refresh),
                        label: const Text('Refrescar'),
                        onPressed: _loadRestaurants,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 16,
                    runSpacing: 16,
                    children:
                        _restaurants.map((restaurant) {
                          return SizedBox(
                            width: 350,
                            height: 250,
                            child: Card(
                              padding: EdgeInsets.zero,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  ClipRRect(
                                    borderRadius: const BorderRadius.only(
                                      topLeft: Radius.circular(4),
                                      topRight: Radius.circular(4),
                                    ),
                                    child: SizedBox(
                                      height: 150,
                                      width: double.infinity,
                                      child:
                                          restaurant['img_url'] != null &&
                                                  restaurant['img_url']
                                                      .toString()
                                                      .isNotEmpty
                                              ? Image.network(
                                                restaurant['img_url'],
                                                fit: BoxFit.cover,
                                                errorBuilder: (
                                                  context,
                                                  error,
                                                  stackTrace,
                                                ) {
                                                  return const Center(
                                                    child: Icon(
                                                      FluentIcons
                                                          .picture_center,
                                                      size: 48,
                                                      color: Colors.grey,
                                                    ),
                                                  );
                                                },
                                              )
                                              : const Center(
                                                child: Icon(
                                                  FluentIcons.picture_center,
                                                  size: 48,
                                                  color: Colors.grey,
                                                ),
                                              ),
                                    ),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.all(12),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          restaurant['name'] ?? 'Sin nombre',
                                          style: const TextStyle(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        const SizedBox(height: 4),
                                        Text(
                                          restaurant['description'] ??
                                              'Sin descripción',
                                          style: const TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey,
                                          ),
                                          maxLines: 2,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        const SizedBox(height: 8),
                                        Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.end,
                                          children: [
                                            Button(
                                              child: const Text('Editar'),
                                              onPressed: () {
                                                // Navigate to edit screen (implement later)
                                              },
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                  ),
                ],
              ),
    );
  }
}
