package uk.app02loveslollipop.mipedido.cliente.api

import android.util.Log
import com.google.gson.Gson
import com.google.gson.JsonSyntaxException
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.*
import okhttp3.*
import okio.ByteString
import uk.app02loveslollipop.mipedido.cliente.models.WebSocketMessage
import uk.app02loveslollipop.mipedido.cliente.models.WebSocketPayload
import java.util.concurrent.TimeUnit

/**
 * Handles WebSocket connections for real-time order notifications.
 * Follows the Singleton pattern.
 */
class WebSocketConnector private constructor() {

    /**
     * Interface for receiving WebSocket events.
     */
    interface WebSocketListener {
        /** Called when the WebSocket connection is established and the server sends a welcome message. */
        fun onWelcome(orderId: String, time: String)
        /** Called when the server sends a notification that the order is completed. */
        fun onOrderCompleted(orderId: String, restaurantId: String, timestamp: String)
        /** Called when an error occurs during message processing or parsing. */
        fun onError(message: String)
        /** Called when the WebSocket connection is closed (by server or client). */
        fun onClosed(reason: String)
        /** Called when the WebSocket connection fails to establish or encounters a fatal error. */
        fun onConnectionFailure(message: String)
    }

    private val client: OkHttpClient = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS) // Essential for long-lived connections
        .pingInterval(30, TimeUnit.SECONDS) // Keep connection alive
        .build()

    private var webSocket: WebSocket? = null
    private var listener: WebSocketListener? = null
    private val gson = Gson()
    // Use IO dispatcher for network operations and SupervisorJob to prevent child failures from cancelling the scope
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var currentOrderId: String? = null
    private var isManuallyClosed = false

    companion object {
        private const val TAG = "WebSocketConnector"
        // Use the same host as REST API but port 8080 and ws protocol
        private const val BASE_URL = "ws://wattson.02loveslollipop.uk/ws/orderNotification"
        private const val NORMAL_CLOSURE_STATUS = 1000
        private const val DEFAULT_TOPIC = "orders"

        @Volatile
        private var instance: WebSocketConnector? = null

        /** Returns the singleton instance of the WebSocketConnector. */
        fun getInstance(): WebSocketConnector {
            return instance ?: synchronized(this) {
                instance ?: WebSocketConnector().also { instance = it }
            }
        }
    }

    /** Sets the listener to receive WebSocket events. */
    fun setListener(listener: WebSocketListener) {
        this.listener = listener
    }

    /**
     * Connects to the WebSocket server for the specified order ID.
     * If already connected to a different order, the existing connection is closed first.
     * @param orderId The ID of the order to monitor.
     */
    fun connect(orderId: String) {
        if (webSocket != null && currentOrderId == orderId) {
            Log.w(TAG, "Already connected or connecting to order: $orderId")
            // Optionally, you could check the WebSocket state here and reconnect if needed
            return
        }
        // Close existing connection if connecting to a new order
        if (webSocket != null) {
             disconnect("Starting new connection for order $orderId")
        }


        currentOrderId = orderId
        isManuallyClosed = false
        // Construct the URL with query parameters as per documentation
        val requestUrl = "$BASE_URL?order_id=$orderId&topic=$DEFAULT_TOPIC"
        val request = Request.Builder().url(requestUrl).build()
        Log.d(TAG, "Attempting to connect to: $requestUrl")

        // Create the WebSocket connection
        webSocket = client.newWebSocket(request, object : okhttp3.WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.i(TAG, "WebSocket connection opened for order: $orderId")
                // The 'welcome' message will be handled in onMessage
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d(TAG, "Received message: $text")
                // Process the message off the main thread
                scope.launch { handleMessage(text) }
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                Log.d(TAG, "Received bytes: ${bytes.hex()} (Ignoring)")
                // Ignore binary messages unless needed
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket closing: Code=$code, Reason=$reason")
                // Server is initiating the close. Often happens after 'order_completed'.
                // We'll notify the listener in onClosed unless it's an unexpected closure code.
                if (code != NORMAL_CLOSURE_STATUS && !isManuallyClosed) {
                     scope.launch { listener?.onClosed("Server closed connection unexpectedly: $reason (Code: $code)") }
                }
                 cleanupWebSocket() // Clean up resources immediately
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket closed: Code=$code, Reason=$reason")
                 // Notify listener only if the closure wasn't initiated by our disconnect() call
                if (!isManuallyClosed) {
                    scope.launch { listener?.onClosed("Connection closed: $reason (Code: $code)") }
                }
                cleanupWebSocket() // Ensure cleanup happens
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                val errorMsg = "WebSocket connection failure: ${t.message}"
                Log.e(TAG, errorMsg, t)

                // Try to get more details from the HTTP response if available (e.g., during handshake)
                val httpErrorCode = response?.code
                val httpErrorMessage = response?.message ?: "N/A"
                // Read response body carefully, it might be consumed already
                val responseBody = try { response?.body?.string() } catch (e: Exception) { "Could not read body" }
                Log.e(TAG, "HTTP Error (if applicable): Code=$httpErrorCode, Message=$httpErrorMessage, Body=$responseBody")

                // Map HTTP error codes to specific messages based on API docs
                val detailedError = when (httpErrorCode) {
                    400 -> "Connection failed: Bad Request (Invalid order ID format or missing parameter?). Server detail: $responseBody"
                    404 -> "Connection failed: Order not found. Server detail: $responseBody"
                    409 -> "Connection failed: Conflict (Order already notified?). Server detail: $responseBody"
                    else -> errorMsg // General failure message
                }

                scope.launch { listener?.onConnectionFailure(detailedError) }
                cleanupWebSocket() // Clean up resources after failure
            }
        })
    }

    /** Parses incoming JSON messages and notifies the listener. */
    private fun handleMessage(json: String) {
        try {
            // First, parse the generic structure to get the type
            val messageTypeToken = object : TypeToken<WebSocketMessage<Any>>() {}.type
            val genericMessage = gson.fromJson<WebSocketMessage<Any>>(json, messageTypeToken)

            // Then, parse the specific payload based on the type
            when (genericMessage.type) {
                "welcome" -> {
                    val welcomePayloadType = object : TypeToken<WebSocketMessage<WebSocketPayload.Welcome>>() {}.type
                    val welcomeMessage = gson.fromJson<WebSocketMessage<WebSocketPayload.Welcome>>(json, welcomePayloadType)
                    // Notify listener on the main thread if UI updates are needed, otherwise keep here
                     listener?.onWelcome(welcomeMessage.payload.order_id, welcomeMessage.payload.time)

                }
                "order_completed" -> {
                    val completedPayloadType = object : TypeToken<WebSocketMessage<WebSocketPayload.OrderCompleted>>() {}.type
                    val completedMessage = gson.fromJson<WebSocketMessage<WebSocketPayload.OrderCompleted>>(json, completedPayloadType)
                     listener?.onOrderCompleted(
                        completedMessage.payload.order_id,
                        completedMessage.payload.restaurant_id,
                        completedMessage.payload.timestamp
                    )
                    // Documentation states the server closes the connection after this message.
                    // No need to call disconnect() here, let onClosing/onClosed handle it.
                }
                else -> {
                    Log.w(TAG, "Received unknown message type: ${genericMessage.type}")
                    listener?.onError("Received unknown message type: ${genericMessage.type}")
                }
            }
        } catch (e: JsonSyntaxException) {
            Log.e(TAG, "Failed to parse WebSocket message: $json", e)
            listener?.onError("Failed to parse message from server.")
        } catch (e: Exception) { // Catch other potential errors during processing
            Log.e(TAG, "Error handling WebSocket message: $json", e)
            listener?.onError("Error processing message: ${e.message}")
        }
    }

    /**
     * Closes the WebSocket connection gracefully.
     * @param reason A description of why the connection is being closed.
     */
    fun disconnect(reason: String = "Client initiated disconnect") {
        if (webSocket != null) {
            Log.i(TAG, "Disconnecting WebSocket: $reason")
            isManuallyClosed = true // Set flag to prevent onClosed/onClosing from sending redundant events
            webSocket?.close(NORMAL_CLOSURE_STATUS, reason)
            // cleanupWebSocket() will be called by onClosing or onClosed callback
        } else {
            Log.d(TAG, "WebSocket already null, cannot disconnect.")
        }
    }

    /** Resets WebSocket state variables. */
    private fun cleanupWebSocket() {
         // Check if still on the IO thread, if not switch? Usually callbacks are on background threads.
        if (webSocket != null) {
             Log.d(TAG, "Cleaning up WebSocket resources for order: $currentOrderId")
             webSocket = null // Allow the WebSocket object to be garbage collected
        }
        currentOrderId = null
        isManuallyClosed = false // Reset flag for potential future connections
    }

    /**
     * Shuts down the connector, closing any active connection and cancelling background tasks.
     * Call this when the connector is no longer needed (e.g., in ViewModel's onCleared).
     */
    fun shutdown() {
        Log.i(TAG, "Shutting down WebSocketConnector")
        disconnect("Connector shutting down")
        scope.cancel() // Cancel all coroutines started by this connector
        // Optional: Clean up OkHttpClient if it's exclusively used here and won't be needed anymore.
        // client.dispatcher.executorService.shutdown()
        // client.connectionPool.evictAll()
        instance = null // Allow the singleton instance to be garbage collected if needed
    }
}