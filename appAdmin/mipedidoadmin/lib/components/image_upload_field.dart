import 'dart:io';
import 'package:fluent_ui/fluent_ui.dart';
import 'package:file_picker/file_picker.dart';
import '../api/api_connector.dart';

class ImageUploadField extends StatefulWidget {
  final String? initialUrl;
  final void Function(String url)? onImageUploaded;
  final String label;

  const ImageUploadField({
    super.key,
    this.initialUrl,
    this.onImageUploaded,
    this.label = '',
  });

  @override
  State<ImageUploadField> createState() => _ImageUploadFieldState();
}

class _ImageUploadFieldState extends State<ImageUploadField> {
  String? _imageUrl;
  File? _selectedFile;
  bool _isUploading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _imageUrl = widget.initialUrl;
  }

  Future<void> _pickFile() async {
    setState(() {
      _error = null;
    });
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['jpg', 'jpeg', 'png'],
      withData: false,
    );
    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
      });
    }
  }

  Future<void> _uploadFile() async {
    if (_selectedFile == null) return;
    setState(() {
      _isUploading = true;
      _error = null;
    });
    final api = ApiConnector();
    final response = await api.uploadFileToBlobStorage(_selectedFile!.path);
    setState(() {
      _isUploading = false;
    });
    if (response['success'] == true && response['data']?['url'] != null) {
      setState(() {
        _imageUrl = response['data']['url'];
        _selectedFile = null;
      });
      if (widget.onImageUploaded != null) {
        widget.onImageUploaded!(_imageUrl!);
      }
    } else {
      setState(() {
        _error = response['error'] ?? 'Error al subir la imagen';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        InfoLabel(
          label: widget.label,
          child: Row(
            children: [
              Button(
                onPressed: _isUploading ? null : _pickFile,
                child: const Text('Seleccionar archivo'),
              ),
              if (_selectedFile != null) ...[
                const SizedBox(width: 8),
                Text(_selectedFile!.path.split(Platform.pathSeparator).last),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: _isUploading ? null : _uploadFile,
                  child:
                      _isUploading
                          ? const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              ProgressRing(strokeWidth: 2),
                              SizedBox(width: 8),
                              Text('Subiendo...'),
                            ],
                          )
                          : const Text('Subir'),
                  
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: 8),
        if (_imageUrl != null && _imageUrl!.isNotEmpty) ...[
          const Text('Vista previa de la imagen:'),
          const SizedBox(height: 8),
          Container(
            height: 200,
            width: double.infinity,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[130]),
              borderRadius: BorderRadius.circular(4),
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: Image.network(
                _imageUrl!,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return const Center(child: Text('Error al cargar la imagen'));
                },
              ),
            ),
          ),
        ],
        if (_error != null) ...[
          const SizedBox(height: 8),
          InfoBar(
            title: const Text('Error'),
            content: Text(_error!),
            severity: InfoBarSeverity.error,
            isLong: true,
          ),
        ],
      ],
    );
  }
}
