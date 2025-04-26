package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Data class representing a restaurant
 */
data class Restaurant(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("img_url") val imageUrl: String
)