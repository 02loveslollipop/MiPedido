package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderAcceptedScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    navController: NavController? = null
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Pedido aceptado") })
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "Pedido aceptado",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Tu pedido a sido aceptado por el negocio, ahora espera para disfrutar tu comida",
                style = MaterialTheme.typography.bodyLarge,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(48.dp))
            Text(
                text = "Ya disfrutaste tu pedido?",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
                modifier = Modifier.padding(bottom = 8.dp)
            )
            Button(
                onClick = {
                    navController?.navigate("review/$restaurantId/$orderId/$userId")
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Hacer Review")
            }
        }
    }
}
