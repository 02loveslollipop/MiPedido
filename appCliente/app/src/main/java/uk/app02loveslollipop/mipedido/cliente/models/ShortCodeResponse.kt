package uk.app02loveslollipop.mipedido.cliente.models

import com.google.gson.annotations.SerializedName

/**
 * Response model for short code to object ID conversion
 */
data class ShortCodeResponse(
    @SerializedName("object_id")
    val objectId: String
)