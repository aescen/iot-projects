package id.ac.plnm.smartcart.ui.common

import android.app.Application
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import id.ac.plnm.smartcart.ui.setting.preference.SettingPreferences
import id.ac.plnm.smartcart.ui.setting.viewmodel.SettingViewModel

class ViewModelFactory(
  private val mApplication: Application,
  private val pref: SettingPreferences? = null
) :
  ViewModelProvider.NewInstanceFactory() {

  companion object {
    @Volatile
    private var INSTANCE: ViewModelFactory? = null

    @JvmStatic
    fun getInstance(application: Application): ViewModelFactory {
      if (INSTANCE == null) {
        synchronized(ViewModelFactory::class.java) {
          INSTANCE = ViewModelFactory(application, null)
        }
      }
      return INSTANCE as ViewModelFactory
    }

  }

  @Suppress("UNCHECKED_CAST")
  override fun <T : ViewModel> create(modelClass: Class<T>): T {
    when {
      modelClass.isAssignableFrom(SettingViewModel::class.java) -> {
        pref?.let { it: SettingPreferences ->
          return SettingViewModel(it) as T
        }
        throw NullPointerException("Setting Preference is null")
      }
      else -> throw IllegalArgumentException("Unknown ViewModel class: " + modelClass.name)
    }
  }
}
