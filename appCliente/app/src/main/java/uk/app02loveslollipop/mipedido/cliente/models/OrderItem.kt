package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing an order item with quantity and selected ingredients
 */
data class OrderItem(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("price") val price: Double,
    @SerializedName("img_url") val imageUrl: String,
    @SerializedName("quantity") val quantity: Int,
    @SerializedName("ingredients") val ingredients: List<String>
)