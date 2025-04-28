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
    onNavigateToCart: (String, String, String) -> Unit = { _, _, _ -> },
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
    
    // State for the currently selected product for personalization
    var selectedProduct by remember { mutableStateOf<Product?>(null) }
    
    // Function to modify order in the API
    fun modifyOrderInAPI(product: Product, quantity: Int, ingredients: List<String>) {
        coroutineScope.launch {
            try {
                val modificationRequest = OrderModificationRequest(
                    productId = product.id,
                    quantity = quantity,
                    ingredients = ingredients
                )
                
                val result = apiConnector.modifyOrderForUser(orderId, userId, modificationRequest)
                result.fold(
                    onSuccess = { _ ->
                        if (quantity > 0) {
                            cartItems[product.id] = quantity
                        } else {
                            cartItems.remove(product.id)
                        }
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
    
    // Function to load current cart items
    fun loadCartItems() {
        coroutineScope.launch {
            try {
                val result = apiConnector.getUserOrder(orderId, userId)
                result.fold(
                    onSuccess = { orderItems ->
                        // Reset and refill cart items
                        cartItems.clear()
                        orderItems.forEach { item ->
                            cartItems[item.id] = item.quantity
                        }
                        Log.d("ProductsScreen", "Successfully loaded ${orderItems.size} items in cart")
                    },
                    onFailure = { throwable ->
                        Log.e("ProductsScreen", "Error loading cart items: ${throwable.message}")
                        // Don't show error to user as this might be an empty cart
                    }
                )
            } catch (e: Exception) {
                Log.e("ProductsScreen", "Exception loading cart items: ${e.message}")
            }
        }
    }
    
    // Load products and cart items on first composition
    LaunchedEffect(key1 = restaurantId) {
        loadProducts()
        loadCartItems()
    }

    // Pull refresh state
    val pullRefreshState = rememberPullRefreshState(
        refreshing = isLoading,
        onRefresh = { 
            loadProducts()
            loadCartItems()
        }
    )
    
    if (selectedProduct != null) {
        PersonalizeProductScreen(
            product = selectedProduct!!,
            quantity = cartItems[selectedProduct!!.id] ?: 0,
            onQuantityChange = { newQuantity -> 
                if (newQuantity == 0) {
                    cartItems.remove(selectedProduct!!.id)
                } else {
                    cartItems[selectedProduct!!.id] = newQuantity
                }
            },
            onConfirm = { selectedIngredients ->
                modifyOrderInAPI(
                    selectedProduct!!, 
                    cartItems[selectedProduct!!.id] ?: 0,
                    selectedIngredients
                )
                selectedProduct = null
            },
            onNavigateBack = { selectedProduct = null }
        )
    } else {
        Scaffold(
            topBar = {
                NavBar(
                    title = "Menú",
                    onBackPressed = onNavigateBack,
                    actions = {
                        BadgedBox(
                            badge = {
                                if (totalCartItems.value > 0) {
                                    Badge { Text("${totalCartItems.value}") }
                                }
                            }
                        ) {
                            IconButton(
                                onClick = { 
                                    onNavigateToCart(restaurantId, orderId, userId)
                                }
                            ) {
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
                            val quantity = cartItems[product.id] ?: 0
                            
                            ProductCard(
                                product = product,
                                onClick = { selectedProduct = product },
                                cartQuantity = quantity,
                                onIncreaseQuantity = {
                                    if (quantity > 0) {
                                        // If already in cart, just increase the quantity with existing ingredients
                                        modifyOrderInAPI(
                                            product = product,
                                            quantity = quantity + 1,
                                            ingredients = product.ingredients
                                        )
                                    } else {
                                        // If not in cart, go to personalize screen
                                        selectedProduct = product
                                    }
                                },
                                onDecreaseQuantity = {
                                    if (quantity > 0) {
                                        // If quantity would go to 0, remove from cart
                                        // Otherwise reduce quantity
                                        modifyOrderInAPI(
                                            product = product,
                                            quantity = quantity - 1,
                                            ingredients = product.ingredients
                                        )
                                    }
                                }
                            )
                        }
                    }
                }
                
                PullRefreshIndicator(
                    refreshing = isLoading,
                    state = pullRefreshState,
                    modifier = Modifier.align(Alignment.TopCenter)
                )
            }
        }
    }
}