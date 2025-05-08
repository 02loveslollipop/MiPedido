package uk.app02loveslollipop.mipedido.cliente.models

data class ReviewRequest(
    val restaurant_id: String,
    val rating: Int
)