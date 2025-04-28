package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

data class Position(
    @SerializedName("lat") val latitude: Double,
    @SerializedName("lng") val longitude: Double
)

/**
 * Data class representing a restaurant
 */
data class Restaurant(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("img_url") val imageUrl: String,
    @SerializedName("rating") val rating: Double,
    @SerializedName("type") val type: String,
    @SerializedName("description") val description: String,
    @SerializedName("position") val position: Position
)