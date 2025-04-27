package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a response from joining an existing order
 */
data class JoinOrderResponse(
    @SerializedName("user_id") val userId: String,
    @SerializedName("restaurant_id") val restaurantId: String
)