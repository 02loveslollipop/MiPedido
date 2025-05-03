package uk.app02loveslollipop.mipedido.cliente.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.models.OrderItem
import uk.app02loveslollipop.mipedido.cliente.models.OrderModificationRequest
import uk.app02loveslollipop.mipedido.cliente.icons.minus
import java.text.NumberFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class, ExperimentalMaterialApi::class)
@Composable
fun CartScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    isCreator: Boolean,
    onNavigateBack: () -> Unit,
    onNavigateToCheckoutQR: (String, String, String) -> Unit,
    onNavigateToCheckoutSlave: (String, String, String, Double) -> Unit,
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()
    
    // State variables
    var isLoading by remember { mutableStateOf(false) }
    var cartItems by remember { mutableStateOf<List<OrderItem>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    
    // Currency formatter
    val currencyFormatter = NumberFormat.getCurrencyInstance(Locale.getDefault())
    
    // Calculate total
    val totalPrice = remember(cartItems) {
        cartItems.sumOf { it.price * it.quantity }
    }
    
    // Calculate total items
    val totalItems = remember(cartItems) {
        cartItems.sumOf { it.quantity }
    }
    
    // Function to load cart items
    fun loadCartItems() {
        coroutineScope.launch {
            isLoading = true
            error = null
            
            try {
                val result = apiConnector.getUserOrder(orderId, userId)
                result.fold(
                    onSuccess = { orderItems ->
                        cartItems = orderItems
                        Log.d("CartScreen", "Successfully loaded ${orderItems.size} items in cart")
                    },
                    onFailure = { throwable ->
                        Log.e("CartScreen", "Error loading cart items: ${throwable.message}")
                        error = throwable.message ?: "No se pudieron cargar los productos del carrito"
                    }
                )
            } catch (e: Exception) {
                Log.e("CartScreen", "Exception loading cart items: ${e.message}")
                error = e.message ?: "Error desconocido"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Function to modify item quantity
    fun modifyItemQuantity(item: OrderItem, newQuantity: Int) {
        coroutineScope.launch {
            try {
                val modificationRequest = OrderModificationRequest(
                    productId = item.id,
                    quantity = newQuantity,
                    ingredients = item.ingredients
                )
                
                val result = apiConnector.modifyOrderForUser(orderId, userId, modificationRequest)
                result.fold(
                    onSuccess = { _ ->
                        // Reload cart after successful modification
                        loadCartItems()
                    },
                    onFailure = { throwable ->
                        Log.e("CartScreen", "Error modifying item: ${throwable.message}")
                        error = throwable.message ?: "No se pudo modificar el producto"
                    }
                )
            } catch (e: Exception) {
                Log.e("CartScreen", "Exception modifying item: ${e.message}")
                error = e.message ?: "Error desconocido"
            }
        }
    }
    
    // Function to handle checkout based on user role
    fun handleCheckout() {
        if (isCreator) {
            // Navigate to QR screen if user is the creator
            onNavigateToCheckoutQR(restaurantId, orderId, userId)
        } else {
            // Navigate to slave screen if user joined the order
            onNavigateToCheckoutSlave(restaurantId, orderId, userId, totalPrice)
        }
    }

    // Load cart items on first composition
    LaunchedEffect(key1 = orderId, key2 = userId) {
        loadCartItems()
    }
    
    // Pull refresh state
    val pullRefreshState = rememberPullRefreshState(
        refreshing = isLoading,
        onRefresh = { loadCartItems() }
    )

    Scaffold(
        topBar = {
            NavBar(
                title = "Tu Carrito",
                onBackPressed = onNavigateBack
            )
        }
    ) { paddingValues ->
        Box(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .pullRefresh(pullRefreshState)
        ) {
            if (error != null) {
                // Error state
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = error ?: "Error desconocido",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.error
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Button(onClick = { loadCartItems() }) {
                        Text("Reintentar")
                    }
                }
            } else if (cartItems.isEmpty() && !isLoading) {
                // Empty cart state
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = "Tu carrito está vacío",
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.primary
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Text(
                        text = "Agrega productos desde el menú para realizar tu pedido",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center
                    )
                }
            } else {
                // Cart content
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp)
                ) {
                    // Order summary card
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "Resumen del Pedido",
                                style = MaterialTheme.typography.titleLarge,
                                color = MaterialTheme.colorScheme.primary
                            )
                            
                            Spacer(modifier = Modifier.height(16.dp))
                            
                            // Items list
                            LazyColumn(
                                modifier = Modifier
                                    .weight(1f)
                                    .fillMaxWidth()
                            ) {
                                items(cartItems) { item ->
                                    CartItemRow(
                                        item = item,
                                        currencyFormatter = currencyFormatter,
                                        onIncreaseQuantity = { modifyItemQuantity(item, item.quantity + 1) },
                                        onDecreaseQuantity = { modifyItemQuantity(item, item.quantity - 1) }
                                    )
                                }
                            }
                            
                            Spacer(modifier = Modifier.height(16.dp))
                            
                            // Summary footer
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    "Total Items:",
                                    style = MaterialTheme.typography.bodyMedium
                                )
                                Text(
                                    "$totalItems",
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                            
                            Spacer(modifier = Modifier.height(8.dp))
                            
                            // Add subtotal row here
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    "Subtotal:",
                                    style = MaterialTheme.typography.bodyMedium
                                )
                                Text(
                                    currencyFormatter.format(totalPrice),
                                    style = MaterialTheme.typography.bodyMedium
                                )
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
                                    currencyFormatter.format(totalPrice),
                                    style = MaterialTheme.typography.titleMedium,
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }
                            
                            // Add space before the button
                            Spacer(modifier = Modifier.height(24.dp))
                            
                            // Update checkout button to use handleCheckout
                            Button(
                                onClick = { handleCheckout() },
                                modifier = Modifier.fillMaxWidth(),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                                    contentColor = MaterialTheme.colorScheme.onPrimaryContainer
                                )
                            ) {
                                Icon(
                                    imageVector = Icons.Default.ShoppingCart,
                                    contentDescription = null,
                                    modifier = Modifier.padding(end = 8.dp)
                                )
                                Text(if (isCreator) "Finalizar Pedido" else "Agregar a Pedido")
                            }
                        }
                    }
                }
            }
            
            // Pull refresh indicator
            PullRefreshIndicator(
                refreshing = isLoading,
                state = pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        }
    }
}

@Composable
private fun CartItemRow(
    item: OrderItem,
    currencyFormatter: NumberFormat,
    onIncreaseQuantity: () -> Unit,
    onDecreaseQuantity: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Product info
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(end = 8.dp)
            ) {
                Text(
                    text = item.name,
                    style = MaterialTheme.typography.titleMedium
                )
                
                Text(
                    text = currencyFormatter.format(item.price),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                
                if (item.ingredients.isNotEmpty()) {
                    Text(
                        text = item.ingredients.joinToString(", "),
                        style = MaterialTheme.typography.bodySmall,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }
            }
            
            // Quantity controls
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                IconButton(
                    onClick = onDecreaseQuantity,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        if (item.quantity <= 1) Icons.Default.Delete else minus,
                        contentDescription = if (item.quantity <= 1) "Eliminar" else "Reducir cantidad"
                    )
                }
                
                Text(
                    text = item.quantity.toString(),
                    style = MaterialTheme.typography.bodyLarge
                )
                
                IconButton(
                    onClick = onIncreaseQuantity,
                    modifier = Modifier.size(32.dp)
                ) {
                    Icon(
                        Icons.Default.Add,
                        contentDescription = "Aumentar cantidad"
                    )
                }
            }
        }
    }
}