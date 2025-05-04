package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import uk.app02loveslollipop.mipedido.cliente.api.WebSocketConnector
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.QrCodeGenerator
import uk.app02loveslollipop.mipedido.cliente.components.useBackConfirmation
import uk.app02loveslollipop.mipedido.cliente.utils.Base36Utils

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CheckoutQRScreen(
    restaurantId: String,
    orderId: String, // This is the full MongoDB ObjectId hex string
    userId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,
    navController: NavController? = null // Optional for navigation
) {
    // Use the new short format encoding for Order ID display
    val shortOrderId = Base36Utils.encodeObjectIdToShortFormat(orderId)
    val context = LocalContext.current
    var orderCompleted by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val wsConnector = remember { WebSocketConnector.getInstance() }
    
    // Function to navigate back to restaurants screen
    val navigateToRestaurants = {
        navController?.popBackStack("restaurants", false)
    }
    
    // Using the shared back confirmation hook
    val (handleBackPress, BackConfirmationDialogContent) = useBackConfirmation(
        message = "Si sales de esta pestaña perderás tu pedido y tendrás que empezar el proceso nuevamente",
        onConfirmNavigation = { navigateToRestaurants() }
    )

    DisposableEffect(orderId) {
        val listener = object : WebSocketConnector.WebSocketListener {
            override fun onWelcome(orderId: String, time: String) {}
            override fun onOrderCompleted(orderId: String, restaurantId: String, timestamp: String) {
                orderCompleted = true
            }
            override fun onError(message: String) {
                errorMessage = message
            }
            override fun onClosed(reason: String) {}
            override fun onConnectionFailure(message: String) {
                errorMessage = message
            }
        }
        wsConnector.setListener(listener)
        wsConnector.connect(orderId)
        onDispose {
            wsConnector.disconnect("Leaving CheckoutQRScreen")
        }
    }

    if (orderCompleted) {
        navController?.navigate("order-accepted/$restaurantId/$orderId/$userId")
        return
    }

    Scaffold(
        topBar = {
            NavBar(
                title = "Finalizar Pedido",
                onBackPressed = { handleBackPress() }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),  // Make the column scrollable
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Title
            Text(
                text = "Tu pedido está listo",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary,
                textAlign = TextAlign.Center
            )
            
            // Description
            Text(
                text = "Muestra este código QR al personal del restaurante para completar tu pedido",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // QR Code
            Card(
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.padding(24.dp)
                ) {
                    // QR Code generator
                    QrCodeGenerator(
                        content = orderId,
                        size = 250,
                        padding = 12,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )

                    // Order ID - using the new short format
                    Text(
                        text = "Pedido: $shortOrderId",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
            
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.secondaryContainer
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Instrucciones",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSecondaryContainer
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "1. Muestra este código QR al personal del restaurante\n" +
                               "2. Espera a que escaneen el código\n" +
                               "3. Paga el pedido\n" +
                               "4. Recoge tu comida cuando esté lista",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSecondaryContainer,
                        textAlign = TextAlign.Start
                    )
                }
            }
            
            // Order status message
            Text(
                text = "El restaurante recibirá tu orden al mostrar el código QR",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.outline
            )
            
            // Add extra padding at the bottom to ensure everything is accessible when scrolling
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
    
    // Include the confirmation dialog
    BackConfirmationDialogContent()
}