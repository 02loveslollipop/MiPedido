import 'package:flutter/material.dart';

class NavBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final VoidCallback? onBackPressed;
  final List<Widget>? actions;
  final bool isBackButtonAlert;

  const NavBar({
    super.key,
    required this.title,
    this.onBackPressed,
    this.actions,
    this.isBackButtonAlert = false,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return AppBar(
      title: Text(
        title,
        style: TextStyle(
          color: colorScheme.onPrimary,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      leading:
          onBackPressed != null
              ? IconButton(
                icon: Icon(
                  Icons.arrow_back_sharp,
                  color:
                      isBackButtonAlert
                          ? colorScheme.errorContainer
                          : colorScheme.onPrimary,
                ),
                onPressed: onBackPressed,
              )
              : null,
      actions: actions,
      backgroundColor: colorScheme.primary,
      elevation: 4,
      shadowColor: colorScheme.shadow.withValues(alpha: 0.3),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
