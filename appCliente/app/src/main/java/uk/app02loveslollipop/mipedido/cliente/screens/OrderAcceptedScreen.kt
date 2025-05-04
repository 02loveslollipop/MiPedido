package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import uk.app02loveslollipop.mipedido.cliente.components.NavBar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderAcceptedScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    navController: NavController? = null
) {
    // State for showing back navigation confirmation dialog
    var showExitConfirmation by remember { mutableStateOf(false) }
    
    // Function to navigate back to restaurants screen
    val navigateToRestaurants = {
        navController?.popBackStack("restaurants", false)
    }
    
    // Exit Confirmation Dialog
    if (showExitConfirmation) {
        AlertDialog(
            onDismissRequest = { showExitConfirmation = false },
            title = { Text("¿Estás seguro que deseas salir?") },
            text = { 
                Text("Se te enviará una notificación en aproximadamente 30 minutos para revisar este pedido. Si no quieres esperar, permanece en esta página y presiona el botón de revisión cuando desees calificar el pedido.") 
            },
            confirmButton = {
                Button(
                    onClick = {
                        showExitConfirmation = false
                        navigateToRestaurants()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text("Salir")
                }
            },
            dismissButton = {
                Button(
                    onClick = { showExitConfirmation = false },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text("Volver")
                }
            }
        )
    }

    Scaffold(
        topBar = {
            NavBar(
                title = "Pedido aceptado",
                onBackPressed = { showExitConfirmation = true }
            )
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
    
    // Handle system back button press
    BackHandler(onBack = { showExitConfirmation = true })
}
