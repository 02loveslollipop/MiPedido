package uk.app02loveslollipop.mipedido.cliente.models

data class ReviewResponse(
    val id: String?,
    val restaurant_id: String?,
    val rating: Int?,
    val status: String?,
    val created_at: String?
)