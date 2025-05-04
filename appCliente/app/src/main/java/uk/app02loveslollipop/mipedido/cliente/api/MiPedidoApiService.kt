package uk.app02loveslollipop.mipedido.cliente.api

import retrofit2.Response
import retrofit2.http.*
import uk.app02loveslollipop.mipedido.cliente.models.*


interface MiPedidoApiService {
    
    // Restaurant endpoints
    @GET("restaurant/")
    suspend fun getRestaurants(): Response<List<Restaurant>>
    
    // Product endpoints
    @GET("products/{restaurantId}")
    suspend fun getProductsByRestaurant(
        @Path("restaurantId") restaurantId: String
    ): Response<List<Product>>
    
    @GET("products/{restaurantId}/{productId}/")
    suspend fun getProductDetails(
        @Path("restaurantId") restaurantId: String,
        @Path("productId") productId: String
    ): Response<Product>
    
    // Order endpoints
    @POST("order/")
    suspend fun createOrder(
        @Body request: Map<String, String>
    ): Response<OrderCreationResponse>
    
    @PUT("order/{orderId}")
    suspend fun joinOrder(
        @Path("orderId") orderId: String
    ): Response<JoinOrderResponse>
    
    @GET("order/{orderId}/{userId}/")
    suspend fun getUserOrder(
        @Path("orderId") orderId: String,
        @Path("userId") userId: String
    ): Response<List<OrderItem>>
    
    @PUT("order/{orderId}/{userId}")
    suspend fun modifyOrderForUser(
        @Path("orderId") orderId: String,
        @Path("userId") userId: String,
        @Body modificationRequest: OrderModificationRequest
    ): Response<Map<String, String>>
    
    // Shortener endpoint
    @GET("shortener/{shortCode}")
    suspend fun resolveShortCode(
        @Path("shortCode") shortCode: String
    ): Response<ShortCodeResponse>
}