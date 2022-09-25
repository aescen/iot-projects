package id.ac.plnm.smartcart.ui.setting.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.asLiveData
import androidx.lifecycle.viewModelScope
import id.ac.plnm.smartcart.ui.setting.preference.SettingPreferences
import kotlinx.coroutines.launch

class SettingViewModel(private val pref: SettingPreferences) : ViewModel() {
  fun getThemeSettings(): LiveData<Boolean> {
    return pref.getThemeSetting().asLiveData()
  }

  fun saveThemeSetting(isDarkModeActive: Boolean) {
    viewModelScope.launch {
      pref.saveThemeSetting(isDarkModeActive)
    }
  }

  fun getBaseApiSettings(): LiveData<String> {
    return pref.getBaseApiSetting().asLiveData()
  }

  fun saveBaseApiSetting(baseApi: String) {
    viewModelScope.launch {
      pref.saveBaseApiSetting(baseApi)
    }
  }

}