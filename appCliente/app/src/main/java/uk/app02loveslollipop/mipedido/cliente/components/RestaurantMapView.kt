package uk.app02loveslollipop.mipedido.cliente.components

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.preference.PreferenceManager
import android.util.Log
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.infowindow.InfoWindow
import uk.app02loveslollipop.mipedido.cliente.R
import uk.app02loveslollipop.mipedido.cliente.models.Restaurant

/**
 * A composable that displays a map with the restaurant's location.
 * When the marker is clicked, it launches Google Maps for navigation.
 */
@Composable
fun RestaurantMapView(
    restaurant: Restaurant,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val position = GeoPoint(restaurant.position.latitude, restaurant.position.longitude)
    
    // Configure the map
    DisposableEffect(Unit) {
        Configuration.getInstance().load(context, PreferenceManager.getDefaultSharedPreferences(context))
        onDispose { }
    }
    
    AndroidView(
        factory = { ctx ->
            MapView(ctx).apply {
                setTileSource(TileSourceFactory.MAPNIK)
                setMultiTouchControls(true)
                controller.setZoom(15.0)
                controller.setCenter(position)
                
                // Add a marker for the restaurant
                val marker = createRestaurantMarker(this, restaurant, position, context)
                overlays.add(marker)
            }
        },
        update = { mapView ->
            mapView.controller.setCenter(position)
        },
        modifier = modifier
            .fillMaxWidth()
            .height(200.dp)
    )
}

/**
 * Creates a marker for the restaurant on the map.
 */
private fun createRestaurantMarker(
    mapView: MapView,
    restaurant: Restaurant,
    position: GeoPoint,
    context: Context
): Marker {
    return Marker(mapView).apply {
        this.position = position
        this.title = restaurant.name
        this.snippet = restaurant.description
        
        // Use a default icon or set a custom one
        // icon = ContextCompat.getDrawable(context, R.drawable.ic_restaurant_marker)
        
        // Set click listener to open Google Maps
        setOnMarkerClickListener { marker, mapView ->
            openGoogleMaps(context, restaurant)
            true // Return true to indicate the click was handled
        }
        
        // Customize info window (optional)
        infoWindow = object : InfoWindow(R.layout.marker_info_window, mapView) {
            override fun onOpen(item: Any?) {
                val view = mView
                view.setOnClickListener {
                    openGoogleMaps(context, restaurant)
                    close()
                }
            }
            
            override fun onClose() {
                // Nothing to do on close
            }
        }
    }
}

/**
 * Opens Google Maps app for navigation to the restaurant.
 */
private fun openGoogleMaps(context: Context, restaurant: Restaurant) {
    try {
        val gmmIntentUri = Uri.parse(
            "geo:${restaurant.position.latitude},${restaurant.position.longitude}" +
            "?q=${restaurant.position.latitude},${restaurant.position.longitude}" +
            "(${Uri.encode(restaurant.name)})"
        )
        val mapIntent = Intent(Intent.ACTION_VIEW, gmmIntentUri)
        mapIntent.setPackage("com.google.android.apps.maps")
        
        // Check if Google Maps is installed
        if (mapIntent.resolveActivity(context.packageManager) != null) {
            context.startActivity(mapIntent)
        } else {
            // Fallback to browser if Google Maps is not installed
            val browserIntent = Intent(Intent.ACTION_VIEW, 
                Uri.parse("https://www.google.com/maps/search/?api=1&query=${restaurant.position.latitude},${restaurant.position.longitude}")
            )
            context.startActivity(browserIntent)
        }
    } catch (e: Exception) {
        Log.e("RestaurantMapView", "Error opening Google Maps", e)
    }
}