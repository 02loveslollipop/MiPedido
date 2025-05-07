package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

data class SearchRestaurantsResponse(
    @SerializedName("count") val count: Int,
    @SerializedName("results") val results: List<Restaurant>
)