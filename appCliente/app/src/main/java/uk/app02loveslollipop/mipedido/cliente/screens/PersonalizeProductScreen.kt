package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.models.Product
import uk.app02loveslollipop.mipedido.cliente.icons.minus
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PersonalizeProductScreen(
    product: Product,
    quantity: Int,
    onQuantityChange: (Int) -> Unit,
    onConfirm: (List<String>) -> Unit,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val selectedIngredients = remember { mutableStateListOf<String>() }
    var showExitDialog by remember { mutableStateOf(false) }
    var currentQuantity by remember(quantity) { mutableStateOf(if (quantity > 0) quantity else 1) }

    // Initialize ingredients if the product has any
    LaunchedEffect(product) {
        if (product.ingredients.isNotEmpty()) {
            selectedIngredients.clear()
            selectedIngredients.addAll(product.ingredients)
        }
    }

    fun handleBackPress() {
        if (quantity > 0 || currentQuantity > 0 || selectedIngredients.isNotEmpty()) {
            showExitDialog = true
        } else {
            onNavigateBack()
        }
    }
    
    // Handle back button/gesture for the entire screen
    BackHandler(onBack = { handleBackPress() })

    if (showExitDialog) {
        AlertDialog(
            onDismissRequest = { showExitDialog = false },
            title = { Text("¿Desea salir?") },
            text = { Text("Si sale ahora, perderá los cambios realizados en este producto.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showExitDialog = false
                        onNavigateBack()
                    }
                ) {
                    Text("Salir")
                }
            },
            dismissButton = {
                TextButton(onClick = { showExitDialog = false }) {
                    Text("Cancelar")
                }
            }
        )
    }

    Scaffold(
        topBar = {
            NavBar(
                title = "Personalizar Producto",
                onBackPressed = { handleBackPress() },
                isBackButtonAlert = true
            )
        },
        bottomBar = {
            BottomAppBar(
                actions = {
                    // Quantity controls
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        IconButton(
                            onClick = { 
                                if (currentQuantity <= 1) {
                                    currentQuantity = 0
                                    onQuantityChange(0)
                                } else {
                                    currentQuantity--
                                }
                            }
                        ) {
                            Icon(
                                if (currentQuantity <= 1) Icons.Default.Delete else minus,
                                contentDescription = if (currentQuantity <= 1) "Eliminar" else "Reducir cantidad"
                            )
                        }
                        
                        Text(
                            text = currentQuantity.toString(),
                            style = MaterialTheme.typography.titleMedium
                        )
                        
                        IconButton(onClick = { currentQuantity++ }) {
                            Icon(Icons.Default.Add, contentDescription = "Aumentar cantidad")
                        }
                    }
                },
                floatingActionButton = {
                    Button(
                        onClick = { 
                            onQuantityChange(currentQuantity)
                            onConfirm(selectedIngredients.toList()) 
                        },
                        enabled = currentQuantity > 0
                    ) {
                        Text("Agregar al carrito")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                // Product Image
                AsyncImage(
                    model = ImageRequest.Builder(LocalContext.current)
                        .data(product.imageUrl)
                        .crossfade(true)
                        .build(),
                    contentDescription = product.name,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp),
                    contentScale = ContentScale.Crop
                )
            }

            item {
                Column(
                    modifier = Modifier.padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = product.name,
                        style = MaterialTheme.typography.headlineMedium
                    )
                    
                    Text(
                        text = NumberFormat.getCurrencyInstance(Locale.getDefault())
                            .format(product.price),
                        style = MaterialTheme.typography.titleLarge,
                        color = MaterialTheme.colorScheme.primary
                    )

                    Text(
                        text = product.description,
                        style = MaterialTheme.typography.bodyLarge
                    )

                }
            }

            item {
                Text(
                    text = "Ingredientes",
                    style = MaterialTheme.typography.titleLarge,
                    modifier = Modifier.padding(horizontal = 16.dp)
                )
            }

            items(product.ingredients) { ingredient ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = ingredient in selectedIngredients,
                        onCheckedChange = { checked ->
                            if (checked) {
                                selectedIngredients.add(ingredient)
                            } else {
                                selectedIngredients.remove(ingredient)
                            }
                        }
                    )
                    Text(
                        text = ingredient,
                        style = MaterialTheme.typography.bodyLarge,
                        modifier = Modifier.padding(start = 8.dp)
                    )
                }
            }
        }
    }
}