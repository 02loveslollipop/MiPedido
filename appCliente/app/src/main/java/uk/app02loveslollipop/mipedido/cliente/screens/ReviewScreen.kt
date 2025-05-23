package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.useBackConfirmation

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReviewScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    navController: NavController? = null
) {
    var rating by remember { mutableStateOf(0) }
    val (isSubmitting, setIsSubmitting) = remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()

    val navigateToRestaurants = {
        navController?.popBackStack("restaurants", false)
    }
    
    // Using the shared back confirmation hook
    val (handleBackPress, BackConfirmationDialogContent) = useBackConfirmation(
        message = "Si sales sin enviar una reseña, no podrás calificar este pedido más adelante.",
        onConfirmNavigation = { navigateToRestaurants() }
    )

    Scaffold(
        topBar = {
            NavBar(
                title = "Califica tu pedido",
                onBackPressed = handleBackPress
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
                text = "¿Cómo calificarías tu experiencia?",
                style = MaterialTheme.typography.titleLarge,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(32.dp))
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                for (i in 1..5) {
                    IconButton(onClick = { rating = i }) {
                        Icon(
                            imageVector = Icons.Default.Star,
                            contentDescription = "$i estrellas",
                            tint = if (i <= rating) Color(0xFFFFC107) else Color.LightGray,
                            modifier = Modifier.size(48.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(32.dp))
            Button(
                onClick = {
                    setIsSubmitting(true)
                    errorMessage = null
                    coroutineScope.launch {
                        try {
                            val apiConnector = uk.app02loveslollipop.mipedido.cliente.api.ApiConnector.getInstance()
                            val result = apiConnector.submitReview(restaurantId, rating)
                            result.fold(
                                onSuccess = {
                                    // On success, return to main menu
                                    navigateToRestaurants()
                                },
                                onFailure = { throwable ->
                                    errorMessage = throwable.message ?: "No se pudo enviar la reseña"
                                }
                            )
                        } catch (e: Exception) {
                            errorMessage = e.message ?: "Error desconocido"
                        } finally {
                            setIsSubmitting(false)
                        }
                    }
                },
                enabled = rating > 0 && !isSubmitting,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (isSubmitting) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                } else {
                    Text("Enviar Review")
                }
            }
            if (errorMessage != null) {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = errorMessage!!,
                    color = Color.Red,
                    style = MaterialTheme.typography.bodyMedium,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
    }
    
    // Include the confirmation dialog
    BackConfirmationDialogContent()
}
