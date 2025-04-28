package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.QrCodeGenerator
import uk.app02loveslollipop.mipedido.cliente.utils.Base36Utils

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CheckoutQRScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    // Use Base36 encoding for order ID display - converts to a 6-character alphanumeric code
    val encodedOrderId = Base36Utils.encodeOrderId(orderId)
    
    Scaffold(
        topBar = {
            NavBar(
                title = "Finalizar Pedido",
                onBackPressed = onNavigateBack
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
                        content = "$orderId|$userId",
                        size = 250,
                        padding = 12,
                        modifier = Modifier.padding(bottom = 16.dp)
                    )
                    
                    // Order ID - using Base36 encoded version
                    Text(
                        text = "Pedido: $encodedOrderId",
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
}