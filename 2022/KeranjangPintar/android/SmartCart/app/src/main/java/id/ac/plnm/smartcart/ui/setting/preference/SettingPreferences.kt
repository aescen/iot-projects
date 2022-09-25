package id.ac.plnm.smartcart.ui.setting.preference

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

class SettingPreferences private constructor(private var dataStorePref: DataStore<Preferences>) {

  fun getThemeSetting(): Flow<Boolean> {
    return dataStorePref.data.map { preferences ->
      preferences[THEME_KEY] ?: false
    }
  }

  suspend fun saveThemeSetting(isDarkModeActive: Boolean) {
    dataStorePref.edit { preferences ->
      preferences[THEME_KEY] = isDarkModeActive
    }
  }

  fun getBaseApiSetting(): Flow<String> {
    return dataStorePref.data.map { preferences ->
      preferences[BASE_API_KEY] ?: "http://192.168.43.1"
    }
  }

  suspend fun saveBaseApiSetting(baseApi: String) {
    dataStorePref.edit { preferences ->
      preferences[BASE_API_KEY] = baseApi
    }
  }

  companion object {
    private val THEME_KEY = booleanPreferencesKey("dark_mode_setting")
    private val BASE_API_KEY = stringPreferencesKey("base_api_setting")
    @Volatile
    private var INSTANCE: SettingPreferences? = null

    fun getInstance(dataStore: DataStore<Preferences>): SettingPreferences {
      return INSTANCE ?: synchronized(this) {
        val instance = SettingPreferences(dataStore)
        INSTANCE = instance
        instance
      }
    }
  }
}