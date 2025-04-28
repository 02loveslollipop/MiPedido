package uk.app02loveslollipop.mipedido.cliente.components

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.foundation.clickable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import coil.request.ImageRequest
import uk.app02loveslollipop.mipedido.cliente.icons.minus
import uk.app02loveslollipop.mipedido.cliente.models.Product
import java.text.NumberFormat
import java.util.Locale

@Composable
fun ProductCard(
    product: Product,
    onClick: () -> Unit,
    cartQuantity: Int = 0,
    onIncreaseQuantity: (() -> Unit)? = null,
    onDecreaseQuantity: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    val currencyFormatter = NumberFormat.getCurrencyInstance(Locale.getDefault())

    Card(
        modifier = modifier
            .fillMaxWidth(),
        colors = CardDefaults.cardColors(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column {
            // Product Image
            Box(modifier = Modifier.clickable { onClick() }) {
                AsyncImage(
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
            }

            // Product Details
            Column(
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Product Name
                Text(
                    text = product.name,
                    style = MaterialTheme.typography.titleLarge,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.clickable { onClick() }
                )

                // Product Price
                Text(
                    text = currencyFormatter.format(product.price),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.clickable { onClick() }
                )

                // Product Ingredients
                if (product.ingredients.isNotEmpty()) {
                    Text(
                        text = product.ingredients.joinToString(", "),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.clickable { onClick() }
                    )
                }

                // Quantity controls (only shown if product is in cart)
                if (cartQuantity > 0 && onIncreaseQuantity != null && onDecreaseQuantity != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "En carrito:",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            IconButton(
                                onClick = { onDecreaseQuantity() },
                                modifier = Modifier.size(32.dp),
                            ) {
                                Icon(
                                    if (cartQuantity <= 1) Icons.Default.Delete else minus,
                                    contentDescription = if (cartQuantity <= 1) "Eliminar" else "Reducir cantidad"
                                )
                            }
                            
                            Text(
                                text = cartQuantity.toString(),
                                style = MaterialTheme.typography.bodyLarge
                            )
                            
                            IconButton(
                                onClick = { onIncreaseQuantity() },
                                modifier = Modifier.size(32.dp),
                            ) {
                                Icon(
                                    Icons.Default.Add, 
                                    contentDescription = "Aumentar cantidad"
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}