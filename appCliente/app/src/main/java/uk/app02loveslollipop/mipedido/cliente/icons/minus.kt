package uk.app02loveslollipop.mipedido.cliente.icons

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp



public val minus: ImageVector
    get() {
        if (_minus != null) {
            return _minus!!
        }
        _minus = ImageVector.Builder(
            name = "Minus",
            defaultWidth = 20.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(
                fill = null,
                fillAlpha = 1.0f,
                stroke = SolidColor(Color(0xFF0F172A)),
                strokeAlpha = 1.0f,
                strokeLineWidth = 2f,
                strokeLineCap = StrokeCap.Round,
                strokeLineJoin = StrokeJoin.Round,
                strokeLineMiter = 2.0f,
                pathFillType = PathFillType.NonZero
            ) {
                moveTo(5f, 12f)
                horizontalLineTo(19f)
            }
        }.build()
        return _minus!!
    }

private var _minus: ImageVector? = null