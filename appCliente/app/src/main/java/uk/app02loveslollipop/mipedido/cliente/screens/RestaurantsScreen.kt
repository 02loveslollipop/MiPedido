package uk.app02loveslollipop.mipedido.cliente.screens

import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberPermissionState
import android.Manifest
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Person
import uk.app02loveslollipop.mipedido.cliente.models.Position
import androidx.compose.material.ExperimentalMaterialApi
import androidx.compose.material.pullrefresh.PullRefreshIndicator
import androidx.compose.material.pullrefresh.pullRefresh
import androidx.compose.material.pullrefresh.rememberPullRefreshState
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.api.ApiConnector
import uk.app02loveslollipop.mipedido.cliente.components.NavBar
import uk.app02loveslollipop.mipedido.cliente.components.RestaurantCard
import uk.app02loveslollipop.mipedido.cliente.models.Restaurant
import uk.app02loveslollipop.mipedido.cliente.utils.LocationUtils
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.provider.Settings

@OptIn(ExperimentalMaterial3Api::class, ExperimentalMaterialApi::class, ExperimentalPermissionsApi::class)
@Composable
fun RestaurantsScreen(
    onNavigateToProductsScreen: (restaurantId: String, orderId: String, userId: String, isCreator: Boolean) -> Unit,
    onNavigateToQrScreen: (restaurantId: String, orderId: String, userId: String) -> Unit,
    onNavigateToQrScanner: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val apiConnector = ApiConnector.getInstance()
    
    var isLoading by remember { mutableStateOf(false) }
    var restaurants by remember { mutableStateOf<List<Restaurant>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    var userLocation by remember { mutableStateOf<Position?>(null) }
    var showLocationDialog by remember { mutableStateOf(false) }
    
    var restaurantSearchQuery by remember { mutableStateOf("") }
    var isRestaurantSearching by remember { mutableStateOf(false) }
    var restaurantSearchResults by remember { mutableStateOf<List<Restaurant>>(emptyList()) }
    var restaurantSearchError by remember { mutableStateOf<String?>(null) }
    
    // Add state for restaurant type filtering
    var selectedType by remember { mutableStateOf<String?>(null) }
    
    // Extract unique restaurant types
    val restaurantTypes = remember(restaurants) {
        restaurants.map { it.type }.distinct().sorted()
    }
    
    // Filter restaurants based on selected type
    val filteredRestaurants = remember(restaurants, selectedType) {
        if (selectedType == null) {
            restaurants
        } else {
            restaurants.filter { it.type == selectedType }
        }
    }
    
    // Location permission state
    val locationPermissionState = rememberPermissionState(
        Manifest.permission.ACCESS_FINE_LOCATION
    ) { isGranted ->
        if (isGranted) {
            userLocation = LocationUtils.getCurrentLocation(context)
        } else {
            showLocationDialog = true
        }
    }

    // Check location permission on first composition and after returning from settings
    LaunchedEffect(Unit) {
        if (!LocationUtils.hasLocationPermission(context)) {
            showLocationDialog = true
        }
        locationPermissionState.launchPermissionRequest()
    }
    
    // Location Permission Dialog
    if (showLocationDialog) {
        AlertDialog(
            onDismissRequest = { showLocationDialog = false },
            title = { Text("Permiso de ubicación") },
            text = { 
                Text(
                    "Para ver la distancia a los restaurantes, necesitas habilitar el permiso de ubicación. " +
                    "Sin este permiso, no podrás ver qué tan lejos están los restaurantes."
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        // Open app settings
                        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
                            data = Uri.fromParts("package", context.packageName, null)
                        }
                        (context as? Activity)?.startActivity(intent)
                        showLocationDialog = false
                    }
                ) {
                    Text("Ir a Ajustes")
                }
            },
            dismissButton = {
                TextButton(onClick = { showLocationDialog = false }) {
                    Text("Más tarde")
                }
            }
        )
    }

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
                        error = throwable.message ?: "No se pudieron cargar los restaurantes"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Error desconocido"
            } finally {
                isLoading = false
            }
        }
    }
    
    fun searchRestaurants(query: String) {
        coroutineScope.launch {
            isRestaurantSearching = true
            restaurantSearchError = null
            try {
                val result = apiConnector.searchRestaurants(query)
                result.fold(
                    onSuccess = { list ->
                        restaurantSearchResults = list
                    },
                    onFailure = { throwable ->
                        restaurantSearchError = throwable.message ?: "No se pudieron buscar restaurantes"
                        restaurantSearchResults = emptyList()
                    }
                )
            } catch (e: Exception) {
                restaurantSearchError = e.message ?: "Error desconocido"
                restaurantSearchResults = emptyList()
            } finally {
                isRestaurantSearching = false
            }
        }
    }

    LaunchedEffect(restaurantSearchQuery) {
        if (restaurantSearchQuery.length >= 3) {
            searchRestaurants(restaurantSearchQuery)
        } else if (restaurantSearchQuery.isEmpty()) {
            restaurantSearchResults = emptyList()
            restaurantSearchError = null
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
                        error = throwable.message ?: "No se pudo crear la orden"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Error desconocido"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Create normal order function
    fun createNormalOrder(restaurantId: String) {
        coroutineScope.launch {
            isLoading = true
            error = null
            
            try {
                val result = apiConnector.createOrder(restaurantId)
                result.fold(
                    onSuccess = { response ->
                        // Navigate to Products screen with restaurant ID, order ID and user ID
                        onNavigateToProductsScreen(
                            restaurantId, 
                            response.orderId, 
                            response.userId,
                            true // Creator for normal orders
                        )
                    },
                    onFailure = { throwable ->
                        error = throwable.message ?: "No se pudo crear la orden"
                    }
                )
            } catch (e: Exception) {
                error = e.message ?: "Error desconocido"
            } finally {
                isLoading = false
            }
        }
    }
    
    // Load restaurants and location on first composition
    LaunchedEffect(key1 = Unit) {
        loadRestaurants()
        if (LocationUtils.hasLocationPermission(context)) {
            userLocation = LocationUtils.getCurrentLocation(context)
        }
    }
    
    // Modern pull refresh state
    val pullRefreshState = rememberPullRefreshState(
        refreshing = isLoading,
        onRefresh = { loadRestaurants() }
    )
    
    Scaffold(
        topBar = {
            NavBar(
                title = "Mi Pedido - Restaurantes"
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = {
                    onNavigateToQrScanner()
                },
                icon = { 
                    Icon(
                        imageVector = Icons.Default.Person,
                        contentDescription = "Escanear código QR"
                    )
                },
                text = { Text("Unirse a la orden") },
                containerColor = MaterialTheme.colorScheme.primaryContainer,
                contentColor = MaterialTheme.colorScheme.onPrimaryContainer
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
                    
                    Button(onClick = { loadRestaurants() }) {
                        Text("Reintentar")
                    }
                }
            } else if (restaurants.isEmpty() && !isLoading) {
                Text(
                    text = "No se encontraron restaurantes",
                    style = MaterialTheme.typography.bodyLarge,
                    textAlign = TextAlign.Center,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp)
                        .align(Alignment.Center)
                )
            } else {
                Column {
                    OutlinedTextField(
                        value = restaurantSearchQuery,
                        onValueChange = { newValue -> restaurantSearchQuery = newValue },
                        label = { Text("Buscar restaurantes") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        singleLine = true,
                        trailingIcon = {
                            if (restaurantSearchQuery.isNotEmpty()) {
                                IconButton(onClick = { restaurantSearchQuery = "" }) {
                                    Icon(Icons.Default.Refresh, contentDescription = "Limpiar búsqueda")
                                }
                            }
                        }
                    )
                    val showRestaurantSearch = restaurantSearchQuery.length >= 3
                    if (showRestaurantSearch) {
                        if (isRestaurantSearching) {
                            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                                CircularProgressIndicator()
                            }
                        } else if (restaurantSearchError != null) {
                            Column(
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(16.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Text(
                                    text = restaurantSearchError ?: "Error desconocido",
                                    style = MaterialTheme.typography.bodyLarge,
                                    textAlign = TextAlign.Center,
                                    color = MaterialTheme.colorScheme.error
                                )
                            }
                        } else if (restaurantSearchResults.isEmpty()) {
                            Text(
                                text = "No se encontraron restaurantes",
                                style = MaterialTheme.typography.bodyLarge,
                                textAlign = TextAlign.Center,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(16.dp)
                            )
                        } else {
                            LazyVerticalGrid(
                                columns = GridCells.Adaptive(minSize = 300.dp),
                                contentPadding = PaddingValues(16.dp),
                                horizontalArrangement = Arrangement.spacedBy(16.dp),
                                verticalArrangement = Arrangement.spacedBy(16.dp)
                            ) {
                                items(restaurantSearchResults) { restaurant ->
                                    RestaurantCard(
                                        restaurant = restaurant,
                                        onClick = {
                                            selectedRestaurant = restaurant
                                            showOrderTypeDialog = true
                                        },
                                        userLocation = userLocation
                                    )
                                }
                            }
                        }
                    } else {
                        // Restaurant type filter section
                        if (restaurantTypes.isNotEmpty()) {
                            Card(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 8.dp),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Column(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(8.dp)
                                ) {
                                    Text(
                                        text = "Filtrar por tipo:",
                                        style = MaterialTheme.typography.labelLarge,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                    
                                    LazyRow(
                                        contentPadding = PaddingValues(4.dp),
                                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        // "All" filter option
                                        item {
                                            FilterChip(
                                                selected = selectedType == null,
                                                onClick = { selectedType = null },
                                                label = { Text("Todos") },
                                                colors = FilterChipDefaults.filterChipColors(
                                                    selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                                    selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer
                                                )
                                            )
                                        }
                                        
                                        // Restaurant type filters
                                        items(restaurantTypes) { type ->
                                            FilterChip(
                                                selected = selectedType == type,
                                                onClick = { selectedType = type },
                                                label = { Text(type) },
                                                colors = FilterChipDefaults.filterChipColors(
                                                    selectedContainerColor = MaterialTheme.colorScheme.primaryContainer,
                                                    selectedLabelColor = MaterialTheme.colorScheme.onPrimaryContainer
                                                )
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Restaurant grid
                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(minSize = 300.dp),
                            contentPadding = PaddingValues(16.dp),
                            horizontalArrangement = Arrangement.spacedBy(16.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            items(filteredRestaurants) { restaurant ->
                                RestaurantCard(
                                    restaurant = restaurant,
                                    onClick = {
                                        selectedRestaurant = restaurant
                                        showOrderTypeDialog = true
                                    },
                                    userLocation = userLocation
                                )
                            }
                        }
                    }
                }
            }
            
            // Pull Refresh Indicator - must be at the end of the Box
            PullRefreshIndicator(
                refreshing = isLoading,
                state = pullRefreshState,
                modifier = Modifier.align(Alignment.TopCenter)
            )
            
            // Order Type Dialog
            if (showOrderTypeDialog) {
                AlertDialog(
                    onDismissRequest = { 
                        showOrderTypeDialog = false
                        selectedRestaurant = null
                    },
                    title = { Text("Selecciona el tipo de pedido") },
                    text = { 
                        Text("¿Deseas hacer un pedido normal o grupal?")
                    },
                    confirmButton = {
                        Button(
                            onClick = {
                                showOrderTypeDialog = false
                                selectedRestaurant?.let { restaurant ->
                                    createNormalOrder(restaurant.id)
                                }
                            }
                        ) {
                            Text("Orden Normal")
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
                            Text("Orden Grupal")
                        }
                    }
                )
            }
        }
    }
}
