package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a request to modify an order item (add/update/remove)
 */
data class OrderModificationRequest(
    @SerializedName("product_id") val productId: String,
    @SerializedName("quantity") val quantity: Int,
    @SerializedName("ingredients") val ingredients: List<String>
)