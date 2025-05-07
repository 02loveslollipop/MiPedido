package uk.app02loveslollipop.mipedido.cliente.components

import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * NavBar component that mimics the Flutter app's AppBar style
 */
@OptIn(ExperimentalMaterial3Api::class) //ExperimentalMaterial3Api is used for Material3 components
@Composable
fun NavBar(
    title: String,
    onBackPressed: (() -> Unit)? = null,
    actions: @Composable () -> Unit = {},
    isBackButtonAlert: Boolean = false,
    modifier: Modifier = Modifier
) {
    TopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge.copy(
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                ),
                color = MaterialTheme.colorScheme.onPrimary
            )
        },
        navigationIcon = {
            if (onBackPressed != null) {
                IconButton(onClick = onBackPressed) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back",
                        tint = if (isBackButtonAlert) 
                            MaterialTheme.colorScheme.errorContainer
                        else 
                            MaterialTheme.colorScheme.onPrimary
                    )
                }
            }
        },
        actions = { actions() },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primary,
            titleContentColor = MaterialTheme.colorScheme.onPrimary,
            navigationIconContentColor = MaterialTheme.colorScheme.onPrimary,
            actionIconContentColor = MaterialTheme.colorScheme.onPrimary
        ),
        modifier = modifier,
        // Adding shadow for elevation effect
        scrollBehavior = TopAppBarDefaults.pinnedScrollBehavior(),
    )
}