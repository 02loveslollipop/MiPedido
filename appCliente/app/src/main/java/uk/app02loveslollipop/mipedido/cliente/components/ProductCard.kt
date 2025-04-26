package uk.app02loveslollipop.mipedido.cliente.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import uk.app02loveslollipop.mipedido.cliente.models.Product
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ProductCard(
    product: Product,
    quantityInCart: Int, // New: Current quantity in cart
    onAddToCart: () -> Unit, // New: Callback for adding
    onIncrease: () -> Unit, // New: Callback for increasing quantity
    onDecrease: () -> Unit, // New: Callback for decreasing quantity
    modifier: Modifier = Modifier
) {
    val currencyFormatter = NumberFormat.getCurrencyInstance(Locale.getDefault())

    Card(
        modifier = modifier
            .fillMaxWidth(),
            // .clickable { onClick() }, // Keep if clicking card should do something else
        colors = CardDefaults.cardColors(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column {
            // Product Image
            AsyncImage(
                // ... existing image code ...
                 model = ImageRequest.Builder(LocalContext.current)
                    .data(product.imageUrl)
                    .crossfade(true)
                    .build(),
                contentDescription = product.name,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(160.dp)
                    .clip(MaterialTheme.shapes.extraSmall),
                contentScale = ContentScale.Crop,
            )

            // Product Details
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Product Name
                Text(
                    // ... existing name code ...
                    text = product.name,
                    style = MaterialTheme.typography.titleLarge,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )

                // Product Price
                Text(
                    // ... existing price code ...
                     text = currencyFormatter.format(product.price),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary
                )

                // Product Ingredients
                if (product.ingredients.isNotEmpty()) {
                    Text(
                        // ... existing ingredients code ...
                        text = product.ingredients.joinToString(", "),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Cart Controls
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = if (quantityInCart == 0) Arrangement.End else Arrangement.SpaceBetween
                ) {
                    if (quantityInCart == 0) {
                        // Add to Cart Button
                        Button(onClick = onAddToCart) {
                            Icon(Icons.Default.Add, contentDescription = "Añadir al Carrito")
                            Spacer(Modifier.size(ButtonDefaults.IconSpacing))
                            Text("Añadir")
                        }
                    } else {
                        // Quantity Controls
                        Row(verticalAlignment = Alignment.CenterVertically) {
                             // Decrease Button (becomes delete if quantity is 1)
                            OutlinedButton(
                                onClick = onDecrease,
                                modifier = Modifier.size(40.dp),
                                contentPadding = PaddingValues(0.dp)
                            ) {
                                Icon(
                                    if (quantityInCart == 1) Icons.Default.Delete else Icons.Default.Close,
                                    contentDescription = if (quantityInCart == 1) "Quitar del carrito" else "Disminuir cantidad"
                                )
                            }

                            // Quantity Text
                            Text(
                                text = "$quantityInCart",
                                style = MaterialTheme.typography.titleMedium,
                                modifier = Modifier.padding(horizontal = 16.dp)
                            )

                            // Increase Button
                            Button(
                                onClick = onIncrease,
                                modifier = Modifier.size(40.dp),
                                contentPadding = PaddingValues(0.dp)
                            ) {
                                Icon(Icons.Default.Add, contentDescription = "Aumentar cantidad")
                            }
                        }
                    }
                }
            }
        }
    }
}