package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a product
 */
data class Product(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String,
    @SerializedName("price") val price: Double,
    @SerializedName("img_url") val imageUrl: String,
    @SerializedName("ingredients") val ingredients: List<String>,
    @SerializedName("isEnabled") val isEnabled: Boolean = true
)