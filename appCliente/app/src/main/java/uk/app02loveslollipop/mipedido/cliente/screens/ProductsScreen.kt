package uk.app02loveslollipop.mipedido.cliente.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.snapshots.SnapshotStateMap
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.ProductCard
import uk.app02loveslollipop.mipedido.cliente.models.Product
import uk.app02loveslollipop.mipedido.cliente.models.OrderModificationRequest

@OptIn(ExperimentalMaterial3Api::class, ExperimentalMaterialApi::class)
@Composable
fun ProductsScreen(
    restaurantId: String,
    orderId: String,
    userId: String,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()
    
    var isLoading by remember { mutableStateOf(false) }
    var products by remember { mutableStateOf<List<Product>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    
    // Cart items (productId -> quantity)
    val cartItems = remember { mutableStateMapOf<String, Int>() }
    val totalCartItems = remember { derivedStateOf { cartItems.values.sum() } }
    
    // Function to modify order in the API
    fun modifyOrderInAPI(product: Product, quantity: Int) {
        coroutineScope.launch {
            try {
                // Create request with empty ingredients list (can be enhanced to include selected ingredients)
                val modificationRequest = OrderModificationRequest(
                    productId = product.id,
                    quantity = quantity,
                    ingredients = emptyList() // Default to empty ingredients list
                )
                
                val result = apiConnector.modifyOrderForUser(orderId, userId, modificationRequest)
                result.fold(
                    onSuccess = { _ ->
                        Log.d("ProductsScreen", "Successfully modified order for product ${product.name}, quantity: $quantity")
                    },
                    onFailure = { throwable ->
                        Log.e("ProductsScreen", "Error modifying order: ${throwable.message}")
                        error = throwable.message ?: "No se pudo modificar el pedido"
                    }
                )
            } catch (e: Exception) {
                Log.e("ProductsScreen", "Exception modifying order: ${e.message}")
                error = e.message ?: "Error desconocido al modificar el pedido"
            }
        }
    }
    
    // Cart handling functions
    fun handleAddToCart(product: Product) {
        cartItems[product.id] = 1
        modifyOrderInAPI(product, 1)
        Log.d("ProductsScreen", "Added ${product.name}. Cart: $cartItems")
    }
    
    fun handleIncreaseQuantity(product: Product) {
        val newQuantity = (cartItems[product.id] ?: 0) + 1
        cartItems[product.id] = newQuantity
        modifyOrderInAPI(product, newQuantity)
        Log.d("ProductsScreen", "Increased ${product.name}. Cart: $cartItems")
    }
    
    fun handleDecreaseQuantity(product: Product) {
        val currentQuantity = cartItems[product.id] ?: 0
        if (currentQuantity > 1) {
            val newQuantity = currentQuantity - 1
            cartItems[product.id] = newQuantity
            modifyOrderInAPI(product, newQuantity)
            Log.d("ProductsScreen", "Decreased ${product.name}. Cart: $cartItems")
        } else {
            cartItems.remove(product.id)
            // Send 0 quantity to remove the product from the order
            modifyOrderInAPI(product, 0)
            Log.d("ProductsScreen", "Removed ${product.name}. Cart: $cartItems")
        }
    }
    
    // Function to load products
    fun loadProducts() {
        coroutineScope.launch {
            isLoading = true
            error = null
            
            try {
                val result = apiConnector.getProductsByRestaurant(restaurantId)
                result.fold(
                    onSuccess = { productsList ->
                        products = productsList
                    },
                    onFailure = { throwable ->
                        error = throwable.message ?: "No se pudieron cargar los productos"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Error desconocido"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Load products on first composition
    LaunchedEffect(key1 = restaurantId) {
        loadProducts()
    }

    // Modern pull refresh state
    val pullRefreshState = rememberPullRefreshState(
        refreshing = isLoading,
        onRefresh = { loadProducts() }
    )
    
    Scaffold(
        topBar = {
            NavBar(
                title = "Menú",
                onBackPressed = onNavigateBack,
                actions = {
                    // Shopping cart icon with badge
                    BadgedBox(
                        badge = {
                            if (totalCartItems.value > 0) {
                                Badge { Text("${totalCartItems.value}") }
                            }
                        }
                    ) {
                        IconButton(onClick = { /* TODO: Navigate to Cart Screen */ }) {
                            Icon(
                                imageVector = Icons.Default.ShoppingCart,
                                contentDescription = "Carrito de Compras"
                            )
                        }
                    }
                }
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
                    
                    Button(onClick = { loadProducts() }) {
                        Text("Reintentar")
                    }
                }
            } else if (products.isEmpty() && !isLoading) {
                Text(
                    text = "No se encontraron productos",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .align(Alignment.Center)
                )
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 300.dp),
                    contentPadding = PaddingValues(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(products) { product ->
                        ProductCard(
                            product = product,
                            quantityInCart = cartItems[product.id] ?: 0,
                            onAddToCart = { handleAddToCart(product) },
                            onIncrease = { handleIncreaseQuantity(product) },
                            onDecrease = { handleDecreaseQuantity(product) }
                        )
                    }
                }
            }
            
            // PullRefreshIndicator must be the last composable in the Box 
            // so it shows up on top of the content
            PullRefreshIndicator(
                refreshing = isLoading,
                state = pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
        }
    }
}