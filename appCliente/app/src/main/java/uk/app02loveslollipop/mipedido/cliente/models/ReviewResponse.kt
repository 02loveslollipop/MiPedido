package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

data class ReviewResponse(
    val id: String?,
    @SerializedName("restaurant_id")
    val restaurantId: String?,
    val rating: Int?,
    val status: String?,
    @SerializedName("created_at")
    val createdAt: String?
)