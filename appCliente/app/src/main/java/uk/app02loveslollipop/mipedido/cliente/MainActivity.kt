package uk.app02loveslollipop.mipedido.cliente

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import uk.app02loveslollipop.mipedido.cliente.screens.*
import uk.app02loveslollipop.mipedido.cliente.ui.theme.MiPedidoTheme

// Navigation utility to prevent multiple rapid back button presses
object NavigationUtils {
    private var isNavigating = false

    suspend fun safeNavigateBack(navController: NavController, onComplete: (() -> Unit)? = null) {
        if (!isNavigating) {
            isNavigating = true
            navController.popBackStack()
            // Add a small delay to prevent multiple rapid navigations
            delay(300)
            isNavigating = false
            onComplete?.invoke()
        }
    }

    // Function to handle back navigation with confirmation
    fun safeNavigateBackWithConfirmation(
        showConfirmation: MutableState<Boolean>,
        confirmationAction: () -> Unit
    ): () -> Unit = {
        if (!isNavigating) {
            showConfirmation.value = true
        }
    }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MiPedidoTheme {
                MiPedidoApp()
            }
        }
    }
}

@Composable
fun MiPedidoApp() {
    val navController = rememberNavController()
    val coroutineScope = rememberCoroutineScope()
    
    // Safe back navigation handler
    val safeNavigateBack: () -> Unit = {
        coroutineScope.launch {
            NavigationUtils.safeNavigateBack(navController)
        }
    }

    NavHost(
        navController = navController,
        startDestination = "restaurants",
        modifier = Modifier.fillMaxSize()
    ) {
        // Restaurants Screen
        composable("restaurants") {
            RestaurantsScreen(
                onNavigateToProductsScreen = { restaurantId, orderId, userId, isCreator ->
                    navController.navigate("products/$restaurantId/$orderId/$userId/$isCreator")
                },
                onNavigateToQrScreen = { restaurantId, orderId, userId ->
                    navController.navigate("qr/$restaurantId/$orderId/$userId")
                },
                onNavigateToQrScanner = {
                    navController.navigate("qr-scanner")
                }
            )
        }

        // Products Screen
        composable(
            route = "products/{restaurantId}/{orderId}/{userId}/{isCreator}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType },
                navArgument("isCreator") { type = NavType.BoolType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            val isCreator = backStackEntry.arguments?.getBoolean("isCreator") ?: false
            ProductsScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                isCreator = isCreator,
                onNavigateBack = safeNavigateBack,
                onNavigateToCart = { resId, oId, uId, isCreator ->
                    navController.navigate("cart/$resId/$oId/$uId/$isCreator")
                }
            )
        }

        // QR Code Screen
        composable(
            route = "qr/{restaurantId}/{orderId}/{userId}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            QrCodeScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                onNavigateBack = safeNavigateBack,
                onNavigateToProducts = { resId, oId, uId, isCreator ->
                    navController.navigate("products/$resId/$oId/$uId/$isCreator")
                }
            )
        }

        // QR Scanner Screen
        composable("qr-scanner") {
            QrScannerScreen(
                onNavigateBack = safeNavigateBack,
                onNavigateToProductsScreen = { restaurantId, orderId, userId, isCreator ->
                    navController.popBackStack()
                    navController.navigate("products/$restaurantId/$orderId/$userId/$isCreator")
                }
            )
        }

        // Cart Screen
        composable(
            route = "cart/{restaurantId}/{orderId}/{userId}/{isCreator}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType },
                navArgument("isCreator") { type = NavType.BoolType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            val isCreator = backStackEntry.arguments?.getBoolean("isCreator") ?: false
            CartScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                isCreator = isCreator,
                onNavigateBack = safeNavigateBack,
                onNavigateToCheckoutQR = { resId, oId, uId ->
                    navController.navigate("checkout-qr/$resId/$oId/$uId")
                },
                onNavigateToCheckoutSlave = { resId, oId, uId, total ->
                    navController.navigate("checkout-slave/$oId/$uId/$total")
                }
            )
        }

        // Checkout QR Screen
        composable(
            route = "checkout-qr/{restaurantId}/{orderId}/{userId}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            CheckoutQRScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                onNavigateBack = safeNavigateBack,
                navController = navController
            )
        }

        // Order Accepted Screen
        composable(
            route = "order-accepted/{restaurantId}/{orderId}/{userId}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            OrderAcceptedScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                navController = navController
            )
        }

        // Review Screen
        composable(
            route = "review/{restaurantId}/{orderId}/{userId}",
            arguments = kotlin.collections.listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            ReviewScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                navController = navController
            )
        }

        // Checkout Slave Screen
        composable(
            route = "checkout-slave/{orderId}/{userId}/{totalPrice}",
            arguments = kotlin.collections.listOf(
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType },
                navArgument("totalPrice") { type = NavType.FloatType }
            )
        ) { backStackEntry ->
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            val totalPrice = backStackEntry.arguments?.getFloat("totalPrice")?.toDouble() ?: 0.0
            CheckoutSlaveScreen(
                orderId = orderId,
                userId = userId,
                totalPrice = totalPrice,
                onFinish = {
                    // Pop back to restaurants screen
                    navController.popBackStack("restaurants", false)
                }
            )
        }
    }
}