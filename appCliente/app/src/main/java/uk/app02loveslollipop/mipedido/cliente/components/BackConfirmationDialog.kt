package uk.app02loveslollipop.mipedido.cliente.components

import androidx.activity.compose.BackHandler
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.text.style.TextAlign

/**
 * A reusable component that handles back navigation with a confirmation dialog.
 *
 * @param showDialog Whether the dialog is currently shown or not
 * @param onShowDialogChange Callback to update the dialog visibility state
 * @param onConfirm Action to perform when the user confirms (usually navigation)
 * @param onDismiss Action to perform when the user dismisses the dialog (usually stay on screen)
 * @param title Dialog title text
 * @param message Dialog message text
 * @param confirmButtonText Text for the confirm button (usually "Salir")
 * @param dismissButtonText Text for the dismiss button (usually "Volver")
 */
@Composable
fun BackConfirmationDialog(
    showDialog: Boolean,
    onShowDialogChange: (Boolean) -> Unit,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit = { onShowDialogChange(false) },
    title: String = "¿Estás seguro que deseas salir?",
    message: String,
    confirmButtonText: String = "Salir",
    dismissButtonText: String = "Volver"
) {
    if (showDialog) {
        AlertDialog(
            onDismissRequest = { onShowDialogChange(false) },
            title = { Text(title) },
            text = { Text(message, textAlign = TextAlign.Start) },
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
                    Text(confirmButtonText)
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
                    Text(dismissButtonText)
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
            title = title,
            message = message,
            confirmButtonText = confirmButtonText,
            dismissButtonText = dismissButtonText
        )
    }
    
    return Pair(handleBackPress, dialogContent)
}