package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import uk.app02loveslollipop.mipedido.cliente.components.NavBar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CartScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    onNavigateBack: () -> Unit,
    onCheckout: (restaurantId: String, orderId: String, userId: String) -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            NavBar(
                title = "Tu Carrito",
                onBackPressed = onNavigateBack
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = { onCheckout(restaurantId, orderId, userId) },
                icon = { 
                    Icon(
                        imageVector = Icons.Default.ShoppingCart,
                        contentDescription = "Realizar Pedido"
                    )
                },
                text = { Text("Pedir") },
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.onPrimaryContainer
            )
        },
        floatingActionButtonPosition = FabPosition.End
    ) { paddingValues ->
        // Dummy content for the cart
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Dummy cart content
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Resumen del Pedido",
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Esta es una pantalla de carrito de demostración.",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Text(
                        text = "Pulsa el botón flotante \"Pedir\" para continuar con el pedido.",
                        style = MaterialTheme.typography.bodyMedium,
                        textAlign = TextAlign.Center
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    // Dummy order items and prices
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Total Items:")
                        Text("5")
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Subtotal:")
                        Text("$45.90")
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Divider()
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            "Total:",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            "$45.90",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                }
            }
        }
    }
}