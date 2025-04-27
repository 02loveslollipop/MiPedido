package uk.app02loveslollipop.mipedido.cliente

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import uk.app02loveslollipop.mipedido.cliente.screens.ProductsScreen
import uk.app02loveslollipop.mipedido.cliente.screens.QrCodeScreen
import uk.app02loveslollipop.mipedido.cliente.screens.QrScannerScreen
import uk.app02loveslollipop.mipedido.cliente.screens.RestaurantsScreen
import uk.app02loveslollipop.mipedido.cliente.ui.theme.MiPedidoTheme

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
    
    NavHost(
        navController = navController,
        startDestination = "restaurants",
        modifier = Modifier.fillMaxSize()
    ) {
        // Restaurants Screen
        composable("restaurants") {
            RestaurantsScreen(
                onNavigateToProductsScreen = { restaurantId, orderId, userId ->
                    navController.navigate("products/$restaurantId/$orderId/$userId")
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
            route = "products/{restaurantId}/{orderId}/{userId}",
            arguments = listOf(
                navArgument("restaurantId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val restaurantId = backStackEntry.arguments?.getString("restaurantId") ?: ""
            val orderId = backStackEntry.arguments?.getString("orderId") ?: ""
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            ProductsScreen(
                restaurantId = restaurantId,
                orderId = orderId,
                userId = userId,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        
        // QR Code Screen
        composable(
            route = "qr/{restaurantId}/{orderId}/{userId}",
            arguments = listOf(
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
                onNavigateBack = { navController.popBackStack() },
                onNavigateToProducts = { resId, oId, uId ->
                    navController.navigate("products/$resId/$oId/$uId")
                }
            )
        }
        
        // QR Scanner Screen
        composable("qr-scanner") {
            QrScannerScreen(
                onNavigateBack = { navController.popBackStack() },
                onNavigateToProductsScreen = { restaurantId, orderId, userId ->
                    // Pop the scanner screen and navigate to products screen
                    navController.popBackStack()
                    navController.navigate("products/$restaurantId/$orderId/$userId")
                }
            )
        }
    }
}