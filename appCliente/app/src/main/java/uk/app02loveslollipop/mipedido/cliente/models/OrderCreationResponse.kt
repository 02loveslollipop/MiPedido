package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a response from creating a new order
 */
data class OrderCreationResponse(
    @SerializedName("order_id") val orderId: String,
    @SerializedName("user_id") val userId: String
)