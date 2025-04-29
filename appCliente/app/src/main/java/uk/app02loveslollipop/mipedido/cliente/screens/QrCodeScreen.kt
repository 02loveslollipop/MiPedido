package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.QrCodeGenerator
import uk.app02loveslollipop.mipedido.cliente.utils.Base36Utils

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrCodeScreen(
    restaurantId: String,
    orderId: String, // This is the full MongoDB ObjectId hex string
    userId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier,
    onNavigateToProducts: (restaurantId: String, orderId: String, userId: String) -> Unit = { _, _, _ -> }
) {
    // Use the new short format encoding for Order ID display
    val shortOrderId = Base36Utils.encodeObjectIdToShortFormat(orderId)

    Scaffold(
        topBar = {
            NavBar(
                title = "Comparte el pedido",
                onBackPressed = onNavigateBack
            )
        }
    ) { paddingValues ->

        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Title
            Text(
                text = "Orden grupal",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary,
                textAlign = TextAlign.Center
            )
            
            // Description
            Text(
                text = "Comparte este código QR con otros para unirse a tu pedido",
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
                        text = "Orden: $shortOrderId",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))
            
            // View Order Button
            Button(
                onClick = { 
                    onNavigateToProducts(restaurantId, orderId, userId)
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 24.dp)
            ) {
                Text("Iniciar mi pedido")
            }
            
            // Add padding at the bottom to ensure everything is visible when scrolling
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}