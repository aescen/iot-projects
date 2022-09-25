package id.ac.plnm.smartcart.ui.common

import android.content.Context
import android.content.res.Configuration
import android.view.View
import android.widget.EditText
import androidx.appcompat.app.AppCompatDelegate
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText


internal object UiUtil {
  fun setRecyclerViewLayoutManager(context: Context, recyclerView: RecyclerView) {
    recyclerView.layoutManager = when (context.resources.configuration.orientation) {
      Configuration.ORIENTATION_LANDSCAPE -> {
        GridLayoutManager(context, 2)
      }
      else -> LinearLayoutManager(context)
    }
  }

  fun getVisibility(isLoading: Boolean): Int {
    return (if (isLoading) View.VISIBLE else View.GONE)
  }

  fun setAppTheme(isDarkModeActive: Boolean, switchTheme: SwitchMaterial? = null) {
    if (isDarkModeActive) {
      AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
      switchTheme?.isChecked = true
    } else {
      AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
      switchTheme?.isChecked = false
    }
  }
}
