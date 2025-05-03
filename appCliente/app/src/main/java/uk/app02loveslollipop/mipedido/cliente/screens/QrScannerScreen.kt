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
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.border
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.CircularProgressIndicator
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.Offset
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
import java.util.concurrent.Executors
import java.io.IOException

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrScannerScreen(
    onNavigateBack: () -> Unit,
    onNavigateToProductsScreen: (restaurantId: String, orderId: String, userId: String, isCreator: Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()

    var hasCameraPermission by remember { mutableStateOf(
        ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
    )}

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

    // Once we have a QR code, we stop scanning
    var isScanningPaused by remember { mutableStateOf(false) }

    // Camera executor
    val cameraExecutor = remember { Executors.newSingleThreadExecutor() }

    // Barcode scanner options
    val options = remember {
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build()
    }

    // Barcode scanner
    val scanner = remember { BarcodeScanning.getClient(options) }

    // Store theme colors as regular Color values to use in drawWithContent
    val primaryColor = MaterialTheme.colorScheme.primary
    val errorColor = MaterialTheme.colorScheme.error
    val surfaceColor = MaterialTheme.colorScheme.surface
    val surfaceVariantColor = MaterialTheme.colorScheme.surfaceVariant
    val onSurfaceVariantColor = MaterialTheme.colorScheme.onSurfaceVariant

    // Function to handle errors and show appropriate messages
    fun handleError(throwable: Throwable) {
        val errorCode = when (throwable) {
            is Exception -> {
                // Extract error code from message or exception properties
                when {
                    throwable.message?.contains("404") == true -> 404
                    throwable.message?.contains("409") == true -> 409
                    throwable.message?.contains("422") == true -> 422
                    else -> 0
                }
            }
            else -> 0
        }

        val message = when (errorCode) {
            404 -> "La orden no existe."
            409 -> "La orden ha sido cumplida o cerrada."
            422 -> "El código QR es inválido."
            else -> when (throwable) {
                is IOException -> "Error de conexión. Verifica tu conexión a internet."
                else -> throwable.message ?: "Error desconocido al unirse a la orden."
            }
        }

        Log.e("QrScannerScreen", "Error joining order: $message, code: $errorCode")
        errorMessage = message
        showErrorDialog = true
    }

    // Function to process QR code and join order
    fun processQrCode(qrContent: String) {
        if (isLoading || isScanningPaused) return

        isScanningPaused = true
        isLoading = true

        coroutineScope.launch {
            try {
                Log.d("QrScannerScreen", "Attempting to join order with ID: $qrContent")

                val result = apiConnector.joinOrder(qrContent)
                result.fold(
                    onSuccess = { response ->
                        // Add null safety checks and logging
                        if (response.restaurantId.isNullOrEmpty()) {
                            Log.e("QrScannerScreen", "Error: Received empty restaurant ID from server")
                            errorMessage = "Error: No se recibió ID de restaurante válido"
                            showErrorDialog = true
                        } else {
                            Log.d("QrScannerScreen", "Success joining order: restaurantId=${response.restaurantId}, userId=${response.userId}")
                            // Navigate to products screen with order ID and user ID
                            onNavigateToProductsScreen(
                                response.restaurantId,
                                qrContent, // orderId
                                response.userId, // userId from join response
                                false //Creator for joined order
                            )
                        }
                    },
                    onFailure = { throwable ->
                        handleError(throwable)
                    }
                )
            } catch (e: Exception) {
                handleError(e)
            } finally {
                isLoading = false
                // We don't reset isScanningPaused here to prevent multiple QR code readings
                // It gets reset if the user dismisses an error dialog
            }
        }
    }
    
    // Camera permission check
    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            requestPermissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }
    
    // Component for analyzing camera frames for QR codes
    class QrCodeAnalyzer(
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
            if (currentTimestamp - lastAnalyzedTimestamp >= 500) { // limit processing rate
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
    
    // Cleanup when leaving the screen
    DisposableEffect(Unit) {
        onDispose {
            cameraExecutor.shutdown()
        }
    }
    
    Scaffold(
        topBar = {
            NavBar(
                title = "Escanear código QR",
                onBackPressed = onNavigateBack
            )
        }
    ) { paddingValues ->
        Box(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (hasCameraPermission) {
                // Camera Preview
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
                                            { qrContent -> processQrCode(qrContent) },
                                            { isScanningPaused }
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
                
                // QR code scanning guide box
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    // Scanning frame to guide users where to position the QR code
                    Box(
                        modifier = Modifier
                            .size(250.dp)
                            .border(
                                width = 2.dp,
                                color = primaryColor,
                                shape = RoundedCornerShape(16.dp)
                            )
                    )
                }
                
                // Scanning indicator
                if (isLoading) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Card(
                            modifier = Modifier.padding(16.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = surfaceColor
                            )
                        ) {
                            Column(
                                modifier = Modifier
                                    .padding(16.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Procesando código QR...",
                                    style = MaterialTheme.typography.bodyLarge
                                )
                                Spacer(modifier = Modifier.height(16.dp))
                                CircularProgressIndicator(
                                    color = primaryColor
                                )
                            }
                        }
                    }
                } else {
                    // Guidance text moved to the bottom of the screen
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.BottomCenter
                    ) {
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp),
                            colors = CardDefaults.cardColors(
                                containerColor = surfaceVariantColor.copy(alpha = 0.9f)
                            )
                        ) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "Coloca el código QR dentro del recuadro",
                                    style = MaterialTheme.typography.bodyLarge,
                                    textAlign = TextAlign.Center,
                                    color = onSurfaceVariantColor
                                )
                            }
                        }
                    }
                }
            } else {
                // Camera permission not granted
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.Info,
                        contentDescription = "Info",
                        tint = errorColor,
                        modifier = Modifier.size(48.dp)
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Se necesita permiso de cámara para escanear códigos QR",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Button(
                        onClick = {
                            requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                        }
                    ) {
                        Text("Conceder permiso")
                    }
                }
            }
            
            // Error dialog
            if (showErrorDialog) {
                AlertDialog(
                    onDismissRequest = {
                        showErrorDialog = false
                        errorMessage = null
                        isScanningPaused = false // Resume scanning when the dialog is dismissed
                    },
                    title = { Text("Error") },
                    text = { 
                        Text(errorMessage ?: "Error desconocido")
                    },
                    confirmButton = {
                        Button(
                            onClick = {
                                showErrorDialog = false
                                errorMessage = null
                                isScanningPaused = false // Resume scanning
                            }
                        ) {
                            Text("Aceptar")
                        }
                    }
                )
            }
        }
    }
}