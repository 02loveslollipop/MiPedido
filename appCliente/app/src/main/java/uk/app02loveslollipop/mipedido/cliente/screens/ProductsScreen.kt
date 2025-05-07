package uk.app02loveslollipop.mipedido.cliente.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
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
    isCreator: Boolean,
    onNavigateBack: () -> Unit,
    onNavigateToCart: (String, String, String, Boolean) -> Unit = { _, _, _, _ -> },
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()
    
    var isLoading by remember { mutableStateOf(false) }
    var products by remember { mutableStateOf<List<Product>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    
    var searchQuery by remember { mutableStateOf("") }
    var isSearching by remember { mutableStateOf(false) }
    var searchResults by remember { mutableStateOf<List<Product>>(emptyList()) }
    var searchError by remember { mutableStateOf<String?>(null) }
    
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
    
    // Function to search products
    fun searchProducts(query: String) {
        coroutineScope.launch {
            isSearching = true
            searchError = null
            try {
                val result = apiConnector.searchProducts(query, restaurantId)
                result.fold(
                    onSuccess = { productsList ->
                        searchResults = productsList
                    },
                    onFailure = { throwable ->
                        searchError = throwable.message ?: "No se pudieron buscar productos"
                        searchResults = emptyList()
                    }
                )
            } catch (e: Exception) {
                searchError = e.message ?: "Error desconocido"
                searchResults = emptyList()
            } finally {
                isSearching = false
            }
        }
    }
    
    // Watch searchQuery and trigger search if >= 3 chars, else reset
    LaunchedEffect(searchQuery) {
        if (searchQuery.length >= 3) {
            searchProducts(searchQuery)
        } else if (searchQuery.isEmpty()) {
            searchResults = emptyList()
            searchError = null
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
                                    onNavigateToCart(restaurantId, orderId, userId, isCreator)
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
                Column(modifier = Modifier.fillMaxSize()) {
                    OutlinedTextField(
                        value = searchQuery,
                        onValueChange = { newValue ->
                            searchQuery = newValue
                        },
                        label = { Text("Buscar productos") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        singleLine = true,
                        trailingIcon = {
                            if (searchQuery.isNotEmpty()) {
                                IconButton(onClick = { searchQuery = "" }) {
                                    Icon(Icons.Default.Close, contentDescription = "Limpiar búsqueda")
                                }
                            }
                        }
                    )
                    
                    val showSearch = searchQuery.length >= 3
                    if (showSearch) {
                        if (isSearching) {
                            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                CircularProgressIndicator()
                            }
                        } else if (searchError != null) {
                            Column(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(16.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Text(
                                    text = searchError ?: "Error desconocido",
                                    style = MaterialTheme.typography.bodyLarge,
                                    textAlign = TextAlign.Center,
                                    color = MaterialTheme.colorScheme.error
                                )
                            }
                        } else if (searchResults.isEmpty()) {
                            Text(
                                text = "No se encontraron productos",
                                style = MaterialTheme.typography.bodyLarge,
                                textAlign = TextAlign.Center,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp)
                                    .align(Alignment.CenterHorizontally)
                            )
                        } else {
                            LazyVerticalGrid(
                                columns = GridCells.Adaptive(minSize = 300.dp),
                                contentPadding = PaddingValues(16.dp),
                                horizontalArrangement = Arrangement.spacedBy(16.dp),
                                verticalArrangement = Arrangement.spacedBy(16.dp)
                            ) {
                                items(searchResults) { product ->
                                    val quantity = cartItems[product.id] ?: 0
                                    ProductCard(
                                        product = product,
                                        onClick = { selectedProduct = product },
                                        cartQuantity = quantity,
                                        onIncreaseQuantity = {
                                            if (quantity > 0) {
                                                modifyOrderInAPI(
                                                    product = product,
                                                    quantity = quantity + 1,
                                                    ingredients = product.ingredients
                                                )
                                            } else {
                                                selectedProduct = product
                                            }
                                        },
                                        onDecreaseQuantity = {
                                            if (quantity > 0) {
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
                    } else {
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
                                    .align(Alignment.CenterHorizontally)
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