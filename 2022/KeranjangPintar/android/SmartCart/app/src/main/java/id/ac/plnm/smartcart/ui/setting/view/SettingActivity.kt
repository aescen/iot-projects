package id.ac.plnm.smartcart.ui.setting.view

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.view.MenuItem
import androidx.lifecycle.ViewModelProvider
import id.ac.plnm.smartcart.ui.setting.preference.SettingPreferences
import id.ac.plnm.smartcart.ui.setting.preference.dataStore
import id.ac.plnm.smartcart.ui.setting.viewmodel.SettingViewModel
import id.ac.plnm.smartcart.R
import id.ac.plnm.smartcart.databinding.ActivitySettingBinding
import id.ac.plnm.smartcart.ui.common.UiUtil.setAppTheme
import id.ac.plnm.smartcart.ui.common.ViewModelFactory

class SettingActivity : AppCompatActivity() {
  private lateinit var binding: ActivitySettingBinding
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ActivitySettingBinding.inflate(layoutInflater)
    setContentView(binding.root)
    supportActionBar?.title =
      resources.getString(R.string.setting_title)
    supportActionBar?.setHomeButtonEnabled(true)
    supportActionBar?.setDisplayHomeAsUpEnabled(true)

    val pref = SettingPreferences.getInstance(dataStore)
    val settingViewModel = ViewModelProvider(
      this,
      ViewModelFactory(application, pref)
    )[SettingViewModel::class.java]

    with(binding) {

      settingViewModel.getThemeSettings()
        .observe(this@SettingActivity) { isDarkModeActive: Boolean ->
          setAppTheme(isDarkModeActive, switchTheme)
        }

      settingViewModel.getBaseApiSettings().observe(this@SettingActivity) { baseApi ->
        Log.d(TAG, baseApi)
      }

      switchTheme.setOnCheckedChangeListener { _, isChecked ->
        settingViewModel.saveThemeSetting(isChecked)
      }
    }
  }

  override fun onOptionsItemSelected(item: MenuItem): Boolean {
    return when (item.itemId) {
      android.R.id.home -> {
        onBackPressed()
        true
      }
      else -> super.onOptionsItemSelected(item)
    }
  }

  companion object {
    private const val TAG = "SettingActivity"
  }
}