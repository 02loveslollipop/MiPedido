import 'dart:developer';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:qr_code_scanner_plus/qr_code_scanner_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import '../api/api_connector.dart';
import 'order_details_screen.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({Key? key}) : super(key: key);

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen>
    with WidgetsBindingObserver {
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');
  QRViewController? controller;
  bool isScanning = true;
  bool hasPermission = false;
  bool isLoading = false;
  final ApiConnector _apiConnector = ApiConnector();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _requestCameraPermission();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Handle app lifecycle changes to properly manage camera resources
    if (controller == null) return;

    // App in foreground and camera should be active
    if (state == AppLifecycleState.resumed) {
      if (mounted) {
        controller?.resumeCamera();
      }
    }
    // App in background, release camera resources
    else if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.inactive) {
      controller?.pauseCamera();
    }
    // App is being destroyed, ensure camera is released
    else if (state == AppLifecycleState.detached) {
      controller?.dispose();
    }
  }

  @override
  void reassemble() {
    super.reassemble();
    if (Platform.isAndroid) {
      controller?.pauseCamera();
    }

    // Always resume the camera after a short delay to give the system time to reinitialize
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted && controller != null) {
        controller!.resumeCamera();
      }
    });
  }

  Future<void> _requestCameraPermission() async {
    final status = await Permission.camera.request();
    if (mounted) {
      setState(() {
        hasPermission = status.isGranted;
      });

      if (!hasPermission) {
        _showPermissionDeniedAlert();
      }
    }
  }

  void _showPermissionDeniedAlert() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder:
          (context) => AlertDialog(
            title: const Text('Permiso de Cámara Requerido'),
            content: const Text(
              'Esta aplicación necesita acceso a la cámara para escanear códigos QR. Por favor, concede el permiso de la cámara en la configuración de tu dispositivo.',
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  Navigator.of(context).pop(); // Return to previous screen
                },
                child: const Text('Cancelar'),
              ),
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  openAppSettings(); // Open app settings to allow user to enable permission
                },
                child: const Text('Abrir Configuración'),
              ),
            ],
          ),
    );
  }

  void _onQRViewCreated(QRViewController controller) {
    this.controller = controller;

    // Resume the camera immediately after creation
    controller.resumeCamera();

    controller.scannedDataStream.listen((scanData) {
      if (!isScanning || isLoading || !mounted) return;

      // Prevent multiple scans
      setState(() {
        isScanning = false;
        isLoading = true;
      });

      // Pause the camera while processing
      controller.pauseCamera();

      // Process the scanned QR code data
      try {
        _processQrCode(scanData.code);
      } catch (e) {
        _showInvalidQRCodeMessage(
          'Error al procesar el código QR: ${e.toString()}',
        );
      }
    });
  }

  Future<void> _processQrCode(String? orderId) async {
    if (orderId == null || orderId.isEmpty) {
      _showInvalidQRCodeMessage('Formato de código QR inválido');
      return;
    }

    try {
      // Call API to validate the order ID
      final result = await _apiConnector.finalizeOrder(orderId);

      if (result['success']) {
        // Valid order ID, navigate to order details screen
        if (!mounted) return;

        // Add the order_id to the data being passed to OrderDetailsScreen
        final orderData = result['orderData'];
        orderData['order_id'] = orderId; // Add the order_id to the data

        // Navigate to our dedicated OrderDetailsScreen with the order data
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (context) => OrderDetailsScreen(orderData: orderData),
          ),
        );
      } else {
        // Check if the order was already fulfilled
        if (result['code'] == 409 ||
            (result['error'] != null &&
                result['error'].contains('already fulfilled'))) {
          _showOrderAlreadyFulfilledDialog(orderId);
        } else {
          _showInvalidQRCodeMessage(result['error'] ?? 'ID de pedido inválido');
        }
      }
    } catch (e) {
      _showInvalidQRCodeMessage(
        'Error al procesar el código QR: ${e.toString()}',
      );
      debugPrint('Error processing QR code: $e');
    }
  }

  void _showOrderAlreadyFulfilledDialog(String orderId) {
    if (!mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Pedido Ya Completado'),
          content: const Text(
            'Este pedido ya ha sido completado y no puede ser procesado nuevamente.',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop(); // Close dialog
                // Resume camera scanning
                setState(() {
                  isScanning = true;
                  isLoading = false;
                });
                controller?.resumeCamera();
              },
              child: const Text('Entendido'),
            ),
          ],
        );
      },
    );
  }

  void _showInvalidQRCodeMessage(String message) {
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );

    // Reset scanner state
    setState(() {
      isScanning = true;
      isLoading = false;
    });

    // Resume scanning after a delay
    Future.delayed(const Duration(seconds: 2), () {
      if (controller != null && mounted) {
        controller!.resumeCamera();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Escanear Código QR del Pedido'),
        actions: [
          // Button to toggle flash
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed:
                hasPermission
                    ? () async {
                      await controller?.toggleFlash();
                      if (mounted) setState(() {});
                    }
                    : null,
          ),
          // Button to flip camera
          IconButton(
            icon: const Icon(Icons.flip_camera_ios),
            onPressed:
                hasPermission
                    ? () async {
                      await controller?.flipCamera();
                      if (mounted) setState(() {});
                    }
                    : null,
          ),
        ],
      ),
      body: Stack(
        children: [
          // Show QR scanner only if we have camera permission
          if (hasPermission)
            QRView(
              key: qrKey,
              onQRViewCreated: _onQRViewCreated,
              overlay: QrScannerOverlayShape(
                borderColor: Theme.of(context).primaryColor,
                borderRadius: 10,
                borderLength: 30,
                borderWidth: 10,
                cutOutSize: MediaQuery.of(context).size.width * 0.8,
              ),
              // Add formatting options to increase scanning reliability
              formatsAllowed: const [BarcodeFormat.qrcode],
            )
          else
            const Center(
              child: Text(
                'Permiso de cámara no concedido',
                style: TextStyle(fontSize: 18),
              ),
            ),

          // Loading indicator
          if (isLoading)
            Container(
              color: Colors.black54,
              child: const Center(child: CircularProgressIndicator()),
            ),

          // Scan instructions
          Positioned(
            bottom: 20,
            left: 0,
            right: 0,
            child: Container(
              alignment: Alignment.center,
              child: const Text(
                'Alinea el código QR dentro del marco para escanear',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
