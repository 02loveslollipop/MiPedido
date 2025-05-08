package uk.app02loveslollipop.mipedido.cliente.api

import android.util.Log
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import uk.app02loveslollipop.mipedido.cliente.models.*
import java.lang.reflect.Type
import java.util.concurrent.TimeUnit
import uk.app02loveslollipop.mipedido.cliente.models.ReviewRequest

/**
 * API Connector for MiPedido API
 * Implements all non-authentication required endpoints
 */
class ApiConnector private constructor() {
    companion object {
        private const val BASE_URL = "https://valkyrie.02loveslollipop.uk/v1/"
        private const val TAG = "ApiConnector"
        
        @Volatile
        private var instance: ApiConnector? = null
        
        fun getInstance(): ApiConnector {
            return instance ?: synchronized(this) {
                instance ?: ApiConnector().also { instance = it }
            }
        }
    }
    
    // Create OkHttpClient with logging interceptor
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    // Create Retrofit instance
    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
    
    // Create API service
    private val apiService: MiPedidoApiService = retrofit.create(MiPedidoApiService::class.java)
    
    // Generic error handling function
    private fun <T> handleApiError(response: Response<T>): Result<T> {
        val errorBody = response.errorBody()?.string() ?: "Unknown error"
        
        // Try to parse the error as JSON
        val errorMessage = try {
            val type: Type = object : TypeToken<Map<String, String>>() {}.type
            val errorMap: Map<String, String> = Gson().fromJson(errorBody, type)
            errorMap["error"] ?: errorMap["detail"] ?: "Unknown error"
        } catch (e: Exception) {
            errorBody
        }
        
        Log.e(TAG, "API Error: $errorMessage")
        return Result.failure(Exception(errorMessage))
    }
    
    // Generic API call wrapper with error handling
    private suspend fun <T> apiCall(call: suspend () -> Response<T>): Result<T> {
        return withContext(Dispatchers.IO) {
            try {
                val response = call()
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        Result.success(body)
                    } else {
                        Result.failure(Exception("Response body is null"))
                    }
                } else {
                    handleApiError(response)
                }
            } catch (e: Exception) {
                Log.e(TAG, "API Call failed: ${e.message}", e)
                Result.failure(e)
            }
        }
    }
    
    // Restaurant API endpoints
    
    /**
     * Get all available restaurants
     * @return Result containing a list of restaurants or an error
     */
    suspend fun getRestaurants(): Result<List<Restaurant>> {
        return apiCall { apiService.getRestaurants() }
    }
    
    /**
     * Search for restaurants by query string (minimum 3 characters)
     * @param query The search query
     * @param limit Maximum number of results (default 10)
     * @param offset Number of results to skip (default 0)
     * @return Result containing a list of restaurants or an error
     */
    suspend fun searchRestaurants(query: String, limit: Int = 10, offset: Int = 0): Result<List<Restaurant>> {
        return apiCall { apiService.searchRestaurants(query, limit, offset) }
            .mapCatching { it.results }
    }
    
    // Product API endpoints
    
    /**
     * Get all products for a specific restaurant
     * @param restaurantId ID of the restaurant
     * @return Result containing a list of products or an error
     */
    suspend fun getProductsByRestaurant(restaurantId: String): Result<List<Product>> {
        return apiCall { apiService.getProductsByRestaurant(restaurantId) }
    }
    
    /**
     * Get details of a specific product
     * @param restaurantId ID of the restaurant
     * @param productId ID of the product
     * @return Result containing the product details or an error
     */
    suspend fun getProductDetails(restaurantId: String, productId: String): Result<Product> {
        return apiCall { apiService.getProductDetails(restaurantId, productId) }
    }
    
    /**
     * Search for products by query string (minimum 3 characters)
     * @param query The search query
     * @param restaurantId The restaurant ID to filter products
     * @param limit Maximum number of results (default 10)
     * @param offset Number of results to skip (default 0)
     * @return Result containing a list of products or an error
     */
    suspend fun searchProducts(query: String, restaurantId: String, limit: Int = 10, offset: Int = 0): Result<List<Product>> {
        return apiCall { apiService.searchProducts(query, restaurantId, limit, offset) }
            .mapCatching { it.results }
    }
    
    // Order API endpoints
    
    /**
     * Create a new order at a specific restaurant
     * @param restaurantId ID of the restaurant
     * @return Result containing order creation response (order ID and user ID) or an error
     */
    suspend fun createOrder(restaurantId: String): Result<OrderCreationResponse> {
        return apiCall { 
            apiService.createOrder(mapOf("restaurant_id" to restaurantId))
        }
    }
    
    /**
     * Join an existing order
     * @param orderId ID of the order to join
     * @return Result containing join order response (user ID) or an error
     */
    suspend fun joinOrder(orderId: String): Result<JoinOrderResponse> {
        return apiCall { apiService.joinOrder(orderId) }
    }
    
    /**
     * Get the order items for a specific user in an order
     * @param orderId ID of the order
     * @param userId ID of the user
     * @return Result containing a list of order items or an error
     */
    suspend fun getUserOrder(orderId: String, userId: String): Result<List<OrderItem>> {
        return apiCall { apiService.getUserOrder(orderId, userId) }
    }
    
    /**
     * Modify an order item for a user (add, update, or remove)
     * @param orderId ID of the order
     * @param userId ID of the user
     * @param productId ID of the product to modify
     * @param quantity New quantity (0 to remove)
     * @param ingredients List of ingredients for the product
     * @return Result containing a status response or an error
     */
    suspend fun modifyOrderForUser(
        orderId: String,
        userId: String,
        productId: String,
        quantity: Int,
        ingredients: List<String>
    ): Result<Map<String, String>> {
        val request = OrderModificationRequest(productId, quantity, ingredients)
        return apiCall { 
            apiService.modifyOrderForUser(orderId, userId, request) 
        }
    }
    
    /**
     * Modify an order item for a user using the OrderModificationRequest object
     * @param orderId ID of the order
     * @param userId ID of the user
     * @param modificationRequest OrderModificationRequest containing the product details
     * @return Result containing a status response or an error
     */
    suspend fun modifyOrderForUser(
        orderId: String,
        userId: String,
        modificationRequest: OrderModificationRequest
    ): Result<Map<String, String>> {
        return apiCall { 
            apiService.modifyOrderForUser(orderId, userId, modificationRequest) 
        }
    }
    
    /**
     * Get full order ID from a short code
     * @param shortCode The 8-character short code to resolve
     * @return Result containing the full order ID or an error
     */
    suspend fun getFullOrderIdFromShortCode(shortCode: String): Result<ShortCodeResponse> {
        return apiCall { apiService.resolveShortCode(shortCode) }
    }
    
    /**
     * Submit a review for a restaurant
     * @param restaurantId The restaurant ID
     * @param rating The rating (1-5)
     * @return Result containing the review response or an error
     */
    suspend fun submitReview(restaurantId: String, rating: Int): Result<ReviewResponse> {
        val review = ReviewRequest(
            restaurant_id = restaurantId,
            rating = rating
        )
        return apiCall { apiService.submitReview(review) }
    }
}