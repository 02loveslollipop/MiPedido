package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CheckoutSlaveScreen(
    orderId: String, // May be needed for future reference or logging
    userId: String, // May be needed for future reference or logging
    totalPrice: Double,
    onFinish: () -> Unit,
    modifier: Modifier = Modifier
) {
    val currencyFormatter = NumberFormat.getCurrencyInstance(Locale.getDefault())

    Scaffold(
        topBar = {
            NavBar(
                title = "Pedido Agregado",
                onBackPressed = { onFinish() } // Navigate back to home screen
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = Icons.Filled.CheckCircle,
                contentDescription = "Éxito",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(80.dp)
            )

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "Tu pedido se ha agregado",
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "El pedido principal aún no se ha completado. Se te notificará cuando esté listo.",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(32.dp))

            Text(
                text = "Tu parte del pedido es:",
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = currencyFormatter.format(totalPrice),
                style = MaterialTheme.typography.displaySmall,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.secondary
            )

            Spacer(modifier = Modifier.height(48.dp))

            Button(
                onClick = onFinish,
                modifier = Modifier.fillMaxWidth(0.8f)
            ) {
                Text("Finalizar")
            }
        }
    }
    
    // Handle system back button to also return to home screen
    BackHandler(onBack = { onFinish() })
}