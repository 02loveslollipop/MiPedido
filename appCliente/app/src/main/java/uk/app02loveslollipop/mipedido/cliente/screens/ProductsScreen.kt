package uk.app02loveslollipop.mipedido.cliente.screens

import android.util.Log
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.snapshots.SnapshotStateMap // Import needed
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.ProductCard
import uk.app02loveslollipop.mipedido.cliente.models.Product

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductsScreen(
    restaurantId: String,
    onNavigateBack: () -> Unit,
    // onProductSelected: (Product) -> Unit, // Removed - interaction via buttons now
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()

    var isLoading by remember { mutableStateOf(false) }
    var products by remember { mutableStateOf<List<Product>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }

    // New: State to hold cart items (productId -> quantity)
    val cartItems = remember { mutableStateMapOf<String, Int>() }
    val totalCartItems = remember { derivedStateOf { cartItems.values.sum() } } // Calculate total items

    // --- Cart Handling Functions ---
    fun handleAddToCart(product: Product) {
        cartItems[product.id] = 1
        Log.d("ProductsScreen", "Added ${product.name}. Cart: $cartItems")
        // TODO: Persist cart or send update to API if needed immediately
    }

    fun handleIncreaseQuantity(product: Product) {
        cartItems.computeIfPresent(product.id) { _, currentQuantity -> currentQuantity + 1 }
        Log.d("ProductsScreen", "Increased ${product.name}. Cart: $cartItems")
        // TODO: Persist cart or send update to API if needed immediately
    }

    fun handleDecreaseQuantity(product: Product) {
        val currentQuantity = cartItems[product.id]
        if (currentQuantity != null) {
            if (currentQuantity > 1) {
                cartItems[product.id] = currentQuantity - 1
                Log.d("ProductsScreen", "Decreased ${product.name}. Cart: $cartItems")
            } else {
                // Remove item if quantity becomes 0
                cartItems.remove(product.id)
                Log.d("ProductsScreen", "Removed ${product.name}. Cart: $cartItems")
            }
            // TODO: Persist cart or send update to API if needed immediately
        }
    }
    // --- End Cart Handling Functions ---


    // Function to load products
    fun loadProducts() {
        // ... existing loadProducts code ...
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
                        error = throwable.message ?: "Failed to load products"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Unknown error occurred"
            } finally {
                isLoading = false
            }
        }
    }

    // Load products on first composition
    LaunchedEffect(key1 = restaurantId) {
        loadProducts()
        // TODO: Load existing cart items if persisted
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Menu") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                actions = {
                    // Cart icon with badge
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
                                contentDescription = "Shopping Cart"
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
        ) {
            if (isLoading) {
                // ... existing loading indicator ...
                 CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            } else if (error != null) {
                // ... existing error display ...
                 Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = error ?: "Unknown error",
                        style = MaterialTheme.typography.bodyLarge,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.error
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    Button(onClick = { loadProducts() }) {
                        Text("Retry")
                    }
                }
            } else if (products.isEmpty()) {
                // ... existing empty state ...
                 Text(
                    text = "No products found",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .align(Alignment.Center)
                )
            } else {
                LazyVerticalGrid(
                    columns = GridCells.Adaptive(minSize = 300.dp), // Adjusted minSize for controls
                    contentPadding = PaddingValues(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(products) { product ->
                        ProductCard(
                            product = product,
                            quantityInCart = cartItems[product.id] ?: 0, // Pass current quantity
                            onAddToCart = { handleAddToCart(product) },
                            onIncrease = { handleIncreaseQuantity(product) },
                            onDecrease = { handleDecreaseQuantity(product) }
                        )
                    }
                }
            }
        }
    }
}