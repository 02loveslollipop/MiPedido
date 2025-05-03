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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReviewScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    navController: NavController? = null
) {
    var rating by remember { mutableStateOf(0) }
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Califica tu pedido") })
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
                    navController?.popBackStack()
                },
                enabled = rating > 0,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Enviar Review")
            }
        }
    }
}
