package uk.app02loveslollipop.mipedido.cliente.models

/**
 * Generic structure for messages received via WebSocket.
 * @param T The type of the payload object.
 */
data class WebSocketMessage<T>(
    val type: String,
    val topic: String,
    val payload: T
)

/**
 * Sealed class representing the different types of payloads
 * that can be received via WebSocket.
 */
sealed class WebSocketPayload {
    /**
     * Payload for the 'welcome' message type.
     */
    data class Welcome(
        val message: String,
        val order_id: String,
        val time: String // ISO DateTime format
    ) : WebSocketPayload()

    /**
     * Payload for the 'order_completed' message type.
     */
    data class OrderCompleted(
        val order_id: String,
        val restaurant_id: String,
        val status: String, // Should be "fulfilled"
        val timestamp: String, // ISO DateTime format
        val message: String
    ) : WebSocketPayload()
}
