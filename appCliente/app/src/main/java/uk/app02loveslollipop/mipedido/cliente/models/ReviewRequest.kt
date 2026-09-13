package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

data class ReviewRequest(
    @SerializedName("restaurant_id")
    val restaurantId: String,
    val rating: Int
)