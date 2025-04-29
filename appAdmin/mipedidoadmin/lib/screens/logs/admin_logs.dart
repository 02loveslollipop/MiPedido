import 'package:fluent_ui/fluent_ui.dart';
import '../../api/api_connector.dart';

class AdminLogsScreen extends StatefulWidget {
  const AdminLogsScreen({super.key});

  @override
  State<AdminLogsScreen> createState() => _AdminLogsScreenState();
}

class _AdminLogsScreenState extends State<AdminLogsScreen> {
  bool _isLoading = true;
  List<dynamic> _logs = [];
  String? _errorMessage;
  int _page = 0;
  static const int _logsPerPage = 20;
  bool _hasMore = true;

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  Future<void> _loadLogs({bool reset = false}) async {
    if (reset) {
      setState(() {
        _page = 0;
        _logs = [];
        _hasMore = true;
      });
    }

    if (!_hasMore && !reset) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiConnector = ApiConnector();
    final result = await apiConnector.getAdminLogs(
      limit: _logsPerPage,
      skip: _page * _logsPerPage,
    );

    setState(() {
      _isLoading = false;
      if (result['success']) {
        final newLogs = result['logs'];
        if (newLogs.length < _logsPerPage) {
          _hasMore = false;
        }
        if (reset) {
          _logs = newLogs;
        } else {
          _logs = [..._logs, ...newLogs];
        }
        _page++;
      } else {
        _errorMessage = result['error'] ?? 'Failed to load admin logs';
      }
    });
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return 'N/A';

    try {
      final date = DateTime.parse(dateStr);
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year} ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateStr.substring(0, 19).replaceAll('T', ' ');
    }
  }

  @override
  Widget build(BuildContext context) {
    return ScaffoldPage(
      header: const PageHeader(title: Text('Registros de Administración')),
      content:
          _errorMessage != null
              ? Center(
                child: InfoBar(
                  title: const Text('Error'),
                  content: Text(_errorMessage!),
                  severity: InfoBarSeverity.error,
                  isLong: true,
                  action: FilledButton(
                    child: const Text('Reintentar'),
                    onPressed: () => _loadLogs(reset: true),
                  ),
                ),
              )
              : Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: CommandBar(
                      mainAxisAlignment: MainAxisAlignment.end,
                      primaryItems: [
                        CommandBarButton(
                          icon: const Icon(FluentIcons.refresh),
                          label: const Text('Refrescar'),
                          onPressed: () => _loadLogs(reset: true),
                        ),
                      ],
                    ),
                  ),
                  Expanded(
                    child:
                        _logs.isEmpty && !_isLoading
                            ? const Center(
                              child: Text('No hay registros disponibles'),
                            )
                            : ListView.builder(
                              padding: const EdgeInsets.all(8),
                              itemCount:
                                  _logs.length +
                                  (_isLoading ? 1 : 0) +
                                  (_hasMore ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (index == _logs.length && _isLoading) {
                                  return const Center(
                                    child: Padding(
                                      padding: EdgeInsets.all(16.0),
                                      child: ProgressRing(),
                                    ),
                                  );
                                } else if (index == _logs.length && _hasMore) {
                                  return Padding(
                                    padding: const EdgeInsets.all(16.0),
                                    child: Center(
                                      child: FilledButton(
                                        child: const Text('Cargar más'),
                                        onPressed: () => _loadLogs(),
                                      ),
                                    ),
                                  );
                                } else if (index < _logs.length) {
                                  final log = _logs[index];
                                  return Card(
                                    margin: const EdgeInsets.symmetric(
                                      vertical: 4,
                                      horizontal: 8,
                                    ),
                                    child: Padding(
                                      padding: const EdgeInsets.all(12.0),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Row(
                                            children: [
                                              Container(
                                                padding:
                                                    const EdgeInsets.symmetric(
                                                      horizontal: 8,
                                                      vertical: 4,
                                                    ),
                                                decoration: BoxDecoration(
                                                  color: Colors.blue,
                                                  borderRadius:
                                                      BorderRadius.circular(4),
                                                ),
                                                child: Text(
                                                  log['action'] ??
                                                      'Acción desconocida',
                                                  style: const TextStyle(
                                                    color: Colors.white,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ),
                                              const Spacer(),
                                              Text(
                                                _formatDate(log['timestamp']),
                                                style: const TextStyle(
                                                  color: Colors.grey,
                                                ),
                                              ),
                                            ],
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            'Admin: ${log['admin_username'] ?? 'Desconocido'}',
                                          ),
                                          if (log['details'] != null) ...[
                                            const SizedBox(height: 4),
                                            Text('Detalles: ${log['details']}'),
                                          ],
                                          if (log['target_id'] != null) ...[
                                            const SizedBox(height: 4),
                                            Text(
                                              'ID Objetivo: ${log['target_id']}',
                                            ),
                                          ],
                                          if (log['target_type'] != null) ...[
                                            const SizedBox(height: 4),
                                            Text('Tipo: ${log['target_type']}'),
                                          ],
                                        ],
                                      ),
                                    ),
                                  );
                                }
                                return null;
                              },
                            ),
                  ),
                ],
              ),
    );
  }
}
