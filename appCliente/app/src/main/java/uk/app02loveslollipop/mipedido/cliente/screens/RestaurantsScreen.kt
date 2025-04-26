package uk.app02loveslollipop.mipedido.cliente.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.RestaurantCard
import uk.app02loveslollipop.mipedido.cliente.models.Restaurant

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RestaurantsScreen(
    onNavigateToProductsScreen: (restaurantId: String) -> Unit,
    onNavigateToQrScreen: (restaurantId: String, orderId: String, userId: String) -> Unit,
    modifier: Modifier = Modifier
) {
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()
    
    var isLoading by remember { mutableStateOf(false) }
    var restaurants by remember { mutableStateOf<List<Restaurant>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    
    // Selected restaurant for the dialog
    var selectedRestaurant by remember { mutableStateOf<Restaurant?>(null) }
    var showOrderTypeDialog by remember { mutableStateOf(false) }
    
    // Function to load restaurants
    fun loadRestaurants() {
        coroutineScope.launch {
            isLoading = true
            error = null
            
            try {
                val result = apiConnector.getRestaurants()
                result.fold(
                    onSuccess = { restaurantsList ->
                        restaurants = restaurantsList
                    },
                    onFailure = { throwable ->
                        error = throwable.message ?: "Failed to load restaurants"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Unknown error occurred"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Create collaborative order function
    fun createCollaborativeOrder(restaurantId: String) {
        coroutineScope.launch {
            isLoading = true
            error = null
            
            try {
                val result = apiConnector.createOrder(restaurantId)
                result.fold(
                    onSuccess = { response ->
                        // Navigate to QR screen with order ID and user ID
                        onNavigateToQrScreen(restaurantId, response.orderId, response.userId)
                    },
                    onFailure = { throwable ->
                        error = throwable.message ?: "Failed to create order"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Unknown error occurred"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Load restaurants on first composition
    LaunchedEffect(key1 = Unit) {
        loadRestaurants()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Restaurants") },
                actions = {
                    IconButton(onClick = { loadRestaurants() }) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Refresh"
                        )
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
                CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
            } else if (error != null) {
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
                    
                    Button(onClick = { loadRestaurants() }) {
                        Text("Retry")
                    }
                }
            } else if (restaurants.isEmpty()) {
                Text(
                    text = "No restaurants found",
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
                    items(restaurants) { restaurant ->
                        RestaurantCard(
                            restaurant = restaurant,
                            onClick = {
                                selectedRestaurant = restaurant
                                showOrderTypeDialog = true
                            }
                        )
                    }
                }
            }
            
            // Order Type Dialog
            if (showOrderTypeDialog) {
                AlertDialog(
                    onDismissRequest = { 
                        showOrderTypeDialog = false
                        selectedRestaurant = null
                    },
                    title = { Text("Select Order Type") },
                    text = { 
                        Text("Do you want to create a normal order or a collaborative order?") 
                    },
                    confirmButton = {
                        Button(
                            onClick = {
                                showOrderTypeDialog = false
                                selectedRestaurant?.let { restaurant ->
                                    onNavigateToProductsScreen(restaurant.id)
                                }
                            }
                        ) {
                            Text("Normal Order")
                        }
                    },
                    dismissButton = {
                        Button(
                            onClick = {
                                showOrderTypeDialog = false
                                selectedRestaurant?.let { restaurant ->
                                    createCollaborativeOrder(restaurant.id)
                                }
                            }
                        ) {
                            Text("Collaborative Order")
                        }
                    }
                )
            }
        }
    }
}