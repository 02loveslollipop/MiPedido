package uk.app02loveslollipop.mipedido.cliente.screens

import android.Manifest
import android.content.pm.PackageManager
import android.util.Log
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScanner
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import java.io.IOException
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrScannerScreen(
    onNavigateBack: () -> Unit,
    onNavigateToProductsScreen: (restaurantId: String, orderId: String, userId: String, isCreator: Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
        )
    }

    val requestPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasCameraPermission = isGranted
        if (!isGranted) {
            Toast.makeText(context, "Se requiere permiso de cámara para escanear códigos QR", Toast.LENGTH_LONG).show()
        }
    }

    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var showErrorDialog by remember { mutableStateOf(false) }
    var isScanningPausedByCodeInput by remember { mutableStateOf(false) }
    var showManualCodeDialog by remember { mutableStateOf(false) }
    var manualCodeInput by remember { mutableStateOf("") }
    var isScanningPaused by remember { mutableStateOf(false) }

    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }
    val options = remember {
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build()
    }
    val scanner = remember { BarcodeScanning.getClient(options) }

    fun showError(message: String) {
        errorMessage = message
        showErrorDialog = true
    }

    fun processQrCode(qrContent: String) {
        if ((isScanningPaused || isLoading) && !isScanningPausedByCodeInput) {
            return
        }

        isScanningPaused = true
        isLoading = true

        coroutineScope.launch {
            try {
                executeQrJoin(
                    apiConnector = apiConnector,
                    qrContent = qrContent,
                    onSuccess = { restaurantId, orderId, userId ->
                        onNavigateToProductsScreen(restaurantId, orderId, userId, false)
                    },
                    onError = ::showError
                )
            } finally {
                isLoading = false
                isScanningPausedByCodeInput = false
            }
        }
    }

    fun processShortCode(shortCode: String) {
        if (shortCode.trim().length != 9) {
            showError("Por favor ingresa un código válido (exactamente 8 caracteres sin contar guiones)")
            return
        }

        if (isLoading) return
        isLoading = true
        isScanningPausedByCodeInput = true

        coroutineScope.launch {
            executeShortCodeResolution(
                apiConnector = apiConnector,
                shortCode = shortCode,
                onSuccess = ::processQrCode,
                onError = { message ->
                    showError(message)
                    isLoading = false
                    isScanningPausedByCodeInput = false
                }
            )
        }
    }

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            requestPermissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            cameraExecutor.shutdown()
        }
    }

    Scaffold(
        topBar = {
            NavBar(
                title = "Escanear código QR",
                onBackPressed = onNavigateBack,
                actions = {
                    IconButton(onClick = {
                        showManualCodeDialog = true
                        isScanningPaused = true
                    }) {
                        Icon(
                            Icons.Filled.Add,
                            contentDescription = "Ingresar código manualmente"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (hasCameraPermission) {
                CameraPreviewSection(
                    scanner = scanner,
                    cameraExecutor = cameraExecutor,
                    onQrCodeDetected = { qrContent -> processQrCode(qrContent) },
                    isScanningPaused = { isScanningPaused },
                    isLoading = isLoading
                )
            } else {
                NoCameraPermissionContent(
                    onRequestPermission = {
                        requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                    }
                )
            }

            if (showManualCodeDialog) {
                QrManualCodeDialog(
                    manualCodeInput = manualCodeInput,
                    onManualCodeInputChange = { manualCodeInput = it },
                    onConfirm = {
                        showManualCodeDialog = false
                        processShortCode(manualCodeInput.trim())
                    },
                    onDismiss = {
                        showManualCodeDialog = false
                        isScanningPaused = false
                        manualCodeInput = ""
                    }
                )
            }

            if (showErrorDialog) {
                QrErrorDialog(
                    errorMessage = errorMessage,
                    onDismiss = {
                        showErrorDialog = false
                        errorMessage = null
                        isScanningPaused = false
                    }
                )
            }
        }
    }
}

private fun resolveQrErrorMessage(throwable: Throwable): String {
    val errorCode = when (throwable) {
        is Exception -> {
            when {
                throwable.message?.contains("404") == true -> 404
                throwable.message?.contains("409") == true -> 409
                throwable.message?.contains("422") == true -> 422
                else -> 0
            }
        }
        else -> 0
    }

    return when (errorCode) {
        404 -> "La orden no existe."
        409 -> "La orden ha sido cumplida o cerrada."
        422 -> "El código QR es inválido."
        else -> when (throwable) {
            is IOException -> "Error de conexión. Verifica tu conexión a internet."
            else -> throwable.message ?: "Error desconocido al unirse a la orden."
        }
    }
}

private class QrCodeAnalyzer(
    private val scanner: BarcodeScanner,
    private val onQrCodeDetected: (String) -> Unit,
    private val isScanningPaused: () -> Boolean
) : ImageAnalysis.Analyzer {
    private var lastAnalyzedTimestamp = 0L

    @androidx.camera.core.ExperimentalGetImage
    override fun analyze(imageProxy: ImageProxy) {
        if (isScanningPaused()) {
            imageProxy.close()
            return
        }

        val currentTimestamp = System.currentTimeMillis()
        if (currentTimestamp - lastAnalyzedTimestamp >= 500) {
            imageProxy.image?.let { mediaImage ->
                val image = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
                scanner.process(image)
                    .addOnSuccessListener { barcodes ->
                        for (barcode in barcodes) {
                            barcode.rawValue?.let { qrContent ->
                                onQrCodeDetected(qrContent)
                                return@addOnSuccessListener
                            }
                        }
                    }
                    .addOnFailureListener {
                        Log.e("QrCodeAnalyzer", "Error scanning QR code: ${it.message}")
                    }
                    .addOnCompleteListener {
                        imageProxy.close()
                    }

                lastAnalyzedTimestamp = currentTimestamp
            } ?: imageProxy.close()
        } else {
            imageProxy.close()
        }
    }
}

@Composable
private fun CameraPreviewSection(
    scanner: BarcodeScanner,
    cameraExecutor: ExecutorService,
    onQrCodeDetected: (String) -> Unit,
    isScanningPaused: () -> Boolean,
    isLoading: Boolean,
    modifier: Modifier = Modifier
) {
    val lifecycleOwner = LocalLifecycleOwner.current

    Box(modifier = modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                val previewView = PreviewView(ctx).apply {
                    implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                }
                val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                cameraProviderFuture.addListener({
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    val imageAnalysis = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .also {
                            it.setAnalyzer(
                                cameraExecutor,
                                QrCodeAnalyzer(
                                    scanner,
                                    onQrCodeDetected,
                                    isScanningPaused
                                )
                            )
                        }

                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            CameraSelector.DEFAULT_BACK_CAMERA,
                            preview,
                            imageAnalysis
                        )
                    } catch (e: Exception) {
                        Log.e("QrScannerScreen", "Error binding camera use cases: ${e.message}")
                    }
                }, ContextCompat.getMainExecutor(ctx))
                previewView
            },
            modifier = Modifier.fillMaxSize()
        )

        // Scanning frame to guide users where to position the QR code
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Box(
                modifier = Modifier
                    .size(250.dp)
                    .border(
                        width = 2.dp,
                        color = MaterialTheme.colorScheme.primary,
                        shape = RoundedCornerShape(16.dp)
                    )
            )
        }

        if (isLoading) {
            ScanningLoadingIndicator()
        } else {
            ScanningGuidanceCard()
        }
    }
}

@Composable
private fun ScanningLoadingIndicator(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Procesando código...",
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(16.dp))
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun ScanningGuidanceCard(
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.BottomCenter
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.9f)
            )
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "Coloca el código QR dentro del recuadro o usa el botón de teclado para ingresar el código manualmente",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun NoCameraPermissionContent(
    onRequestPermission: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Info,
            contentDescription = "Info",
            tint = MaterialTheme.colorScheme.error,
            modifier = Modifier.size(48.dp)
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Se necesita permiso de cámara para escanear códigos QR",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onRequestPermission) {
            Text("Conceder permiso")
        }
    }
}

@Composable
private fun QrManualCodeDialog(
    manualCodeInput: String,
    onManualCodeInputChange: (String) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Ingresar Código") },
        text = {
            Column {
                Text("Ingrese el código de 8 caracteres del pedido")
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = manualCodeInput,
                    onValueChange = { onManualCodeInputChange(it.uppercase()) },
                    singleLine = true,
                    label = { Text("Código") },
                    placeholder = { Text("Ej: A1B2-7YA3") }
                )
            }
        },
        confirmButton = {
            Button(onClick = onConfirm) {
                Text("Procesar")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Cancelar")
            }
        }
    )
}

@Composable
private fun QrErrorDialog(
    errorMessage: String?,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Error") },
        text = {
            Text(errorMessage ?: "Error desconocido")
        },
        confirmButton = {
            Button(onClick = onDismiss) {
                Text("Aceptar")
            }
        }
    )
}

private suspend fun executeQrJoin(
    apiConnector: ApiConnector,
    qrContent: String,
    onSuccess: (restaurantId: String, orderId: String, userId: String) -> Unit,
    onError: (String) -> Unit
) {
    try {
        Log.d("QrScannerScreen", "Attempting to join order with ID: $qrContent")
        val result = apiConnector.joinOrder(qrContent)
        result.fold(
            onSuccess = { response ->
                if (response.restaurantId.isNullOrEmpty()) {
                    Log.e("QrScannerScreen", "Error: Received empty restaurant ID from server")
                    onError("Error: No se recibió ID de restaurante válido")
                } else {
                    Log.d("QrScannerScreen", "Success joining order: restaurantId=${response.restaurantId}, userId=${response.userId}")
                    onSuccess(response.restaurantId, qrContent, response.userId)
                }
            },
            onFailure = { throwable ->
                onError(resolveQrErrorMessage(throwable))
            }
        )
    } catch (e: Exception) {
        onError(resolveQrErrorMessage(e))
    }
}

private suspend fun executeShortCodeResolution(
    apiConnector: ApiConnector,
    shortCode: String,
    onSuccess: (String) -> Unit,
    onError: (String) -> Unit
) {
    try {
        Log.d("QrScannerScreen", "Resolving short code: $shortCode")
        val shortCodeResult = apiConnector.getFullOrderIdFromShortCode(shortCode)
        shortCodeResult.fold(
            onSuccess = { response ->
                Log.d("QrScannerScreen", "Short code resolved to order ID: ${response.objectId}")
                onSuccess(response.objectId)
            },
            onFailure = { throwable ->
                Log.e("QrScannerScreen", "Error resolving short code: ${throwable.message}")
                onError(resolveQrErrorMessage(throwable))
            }
        )
    } catch (e: Exception) {
        Log.e("QrScannerScreen", "Exception in executeShortCodeResolution: ${e.message}")
        onError(resolveQrErrorMessage(e))
    }
}