package uk.app02loveslollipop.mipedido.cliente.components

import androidx.activity.compose.BackHandler
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.text.style.TextAlign

/**
 * Configuration for texts shown in the back confirmation dialog.
 */
data class BackConfirmationDialogTexts(
    val message: String,
    val title: String = "¿Estás seguro que deseas salir?",
    val confirmButtonText: String = "Salir",
    val dismissButtonText: String = "Volver"
)

/**
 * A reusable component that handles back navigation with a confirmation dialog.
 *
 * @param showDialog Whether the dialog is currently shown or not
 * @param onShowDialogChange Callback to update the dialog visibility state
 * @param onConfirm Action to perform when the user confirms (usually navigation)
 * @param texts Text configuration for the dialog
 * @param onDismiss Action to perform when the user dismisses the dialog (usually stay on screen)
 */
@Composable
fun BackConfirmationDialog(
    showDialog: Boolean,
    onShowDialogChange: (Boolean) -> Unit,
    onConfirm: () -> Unit,
    texts: BackConfirmationDialogTexts,
    onDismiss: () -> Unit = { onShowDialogChange(false) }
) {
    if (showDialog) {
        AlertDialog(
            onDismissRequest = { onShowDialogChange(false) },
            title = { Text(texts.title) },
            text = { Text(texts.message, textAlign = TextAlign.Start) },
            confirmButton = {
                Button(
                    onClick = {
                        onShowDialogChange(false)
                        onConfirm()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text(texts.confirmButtonText)
                }
            },
            dismissButton = {
                Button(
                    onClick = {
                        onShowDialogChange(false)
                        onDismiss()
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    )
                ) {
                    Text(texts.dismissButtonText)
                }
            }
        )
    }
}

/**
 * A composable function that handles both the back button and the dialog state.
 * Use this in screens that need back navigation confirmation.
 *
 * @param message The message to show in the confirmation dialog
 * @param onConfirmNavigation The action to perform when back navigation is confirmed
 * @param title Dialog title text
 * @param confirmButtonText Text for the confirm button
 * @param dismissButtonText Text for the dismiss button
 * @return A lambda that can be used for NavBar's onBackPressed parameter
 */
@Composable
fun useBackConfirmation(
    message: String,
    onConfirmNavigation: () -> Unit,
    title: String = "¿Estás seguro que deseas salir?",
    confirmButtonText: String = "Salir",
    dismissButtonText: String = "Volver"
): Pair<() -> Unit, @Composable () -> Unit> {
    var showConfirmationDialog by remember { mutableStateOf(false) }
    
    val handleBackPress = {
        showConfirmationDialog = true
    }
    
    val dialogContent = @Composable {
        // Handle system back button
        BackHandler(onBack = handleBackPress)
        
        // Show the confirmation dialog when needed
        BackConfirmationDialog(
            showDialog = showConfirmationDialog,
            onShowDialogChange = { showConfirmationDialog = it },
            onConfirm = onConfirmNavigation,
            texts = BackConfirmationDialogTexts(
                title = title,
                message = message,
                confirmButtonText = confirmButtonText,
                dismissButtonText = dismissButtonText
            )
        )
    }
    
    return Pair(handleBackPress, dialogContent)
}