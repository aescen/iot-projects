package id.ac.plnm.smartcart.ui.main.view

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.res.Configuration
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.view.ViewTreeObserver
import android.widget.Toast
import androidx.activity.result.ActivityResult
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.WindowCompat
import androidx.lifecycle.ViewModelProvider
import com.karumi.dexter.Dexter
import com.karumi.dexter.listener.PermissionDeniedResponse
import com.karumi.dexter.listener.PermissionGrantedResponse
import com.karumi.dexter.listener.single.BasePermissionListener
import id.ac.plnm.smartcart.R
import id.ac.plnm.smartcart.data.model.PosItem
import id.ac.plnm.smartcart.databinding.ActivityMainBinding
import id.ac.plnm.smartcart.ui.common.UiUtil.setAppTheme
import id.ac.plnm.smartcart.ui.common.UiUtil.setRecyclerViewLayoutManager
import id.ac.plnm.smartcart.ui.common.ViewModelFactory
import id.ac.plnm.smartcart.ui.main.adapter.ListPosProductAdapter
import id.ac.plnm.smartcart.ui.main.adapter.ListPosProductAdapter.OnItemClickCallback
import id.ac.plnm.smartcart.ui.main.viewmodel.MainViewModel
import id.ac.plnm.smartcart.ui.qrscanner.view.QRScannerActivity
import id.ac.plnm.smartcart.ui.qrscanner.view.QRScannerActivity.Companion.EXTRA_QR_CODE
import id.ac.plnm.smartcart.ui.setting.preference.SettingPreferences
import id.ac.plnm.smartcart.ui.setting.preference.dataStore
import id.ac.plnm.smartcart.ui.setting.view.SettingActivity
import id.ac.plnm.smartcart.ui.setting.viewmodel.SettingViewModel
import java.util.*
import kotlin.concurrent.schedule

class MainActivity : AppCompatActivity() {

  //  private lateinit var appBarConfiguration: AppBarConfiguration
  private lateinit var binding: ActivityMainBinding
  private lateinit var resultLauncher: ActivityResultLauncher<Intent>
  private val mainViewModel by viewModels<MainViewModel>()
  private val listUserAdapter: ListPosProductAdapter = ListPosProductAdapter(arrayListOf())
  private var isReady = false

  override fun onCreate(savedInstanceState: Bundle?) {
    WindowCompat.setDecorFitsSystemWindows(window, false)
    super.onCreate(savedInstanceState)
    installSplashScreen()
    binding = ActivityMainBinding.inflate(layoutInflater)
    setContentView(binding.root)
    supportActionBar?.title = resources.getString(R.string.app_name)

//    setSupportActionBar(binding.toolbar)
//    val navController = findNavController(R.id.nav_host_fragment_content_main)
//    appBarConfiguration = AppBarConfiguration(navController.graph)
//    setupActionBarWithNavController(navController, appBarConfiguration)

    binding.root.viewTreeObserver.addOnPreDrawListener(object : ViewTreeObserver.OnPreDrawListener {
      override fun onPreDraw(): Boolean {
        return if (isReady) {
          binding.root.viewTreeObserver.removeOnPreDrawListener(this)
          true
        } else false
      }
    })

    requestForPermission(Manifest.permission.CAMERA)
    subscribeUi()
    setUpViews()

    Timer().schedule(1234) { isReady = true }
  }

  private fun setUpViews() {
    val startForResult =
      registerForActivityResult(StartActivityForResult()) { result: ActivityResult ->
        when (result.resultCode) {
          Activity.RESULT_OK -> {
            result.data?.getStringExtra(EXTRA_QR_CODE)?.let { qrCode ->
              Log.d(TAG, "Scan result: $qrCode")
              mainViewModel.setQrKeranjang(qrCode)
              runOnUiThread {
                Toast.makeText(this@MainActivity, "Scan result: $qrCode", Toast.LENGTH_LONG).show()
              }
            }
          }
          Activity.RESULT_CANCELED -> {
            Log.d(TAG, "Failed to start scanner.")
          }
        }
      }

    binding.fab.setOnClickListener {
      val newQRScannerActivity = Intent(this@MainActivity, QRScannerActivity::class.java)
      startForResult.launch(newQRScannerActivity)
    }

    binding.rvPosProducts.setHasFixedSize(true)
    showRecyclerList()
    setRecyclerViewLayoutManager(this, binding.rvPosProducts)
  }

  private fun showRecyclerList() {
    binding.rvPosProducts.apply {
      adapter = listUserAdapter
    }
    listUserAdapter.setOnItemClickCallback(object : OnItemClickCallback {
      override fun onItemClicked(data: PosItem) {
        runOnUiThread {
          Toast.makeText(this@MainActivity, "Pos Item: ${data.namaProduk}", Toast.LENGTH_SHORT)
            .show()
        }
//        showSelectedProduct(data)
      }
    })
  }

  private fun subscribeUi() {
    mainViewModel.totalProduct.observe((this@MainActivity)) { total ->
      total?.let { binding.tvTotalProduct.text = "Total produk: $total" }

    }

    mainViewModel.totalPrice.observe((this@MainActivity)) { total ->
      total?.let { binding.tvTotalPrice.text = "Total Harga: Rp. $total" }
    }

    mainViewModel.qrKeranjang.observe(this@MainActivity) { code ->
      code?.let {
        val qr = code.replace('.', '_')
        mainViewModel.updatePosProductList(qr)
        Log.d(TAG, "Set QR Code Keranjang: $qr")
      }
    }
    mainViewModel.posProduct.observe(this@MainActivity) { posProduct ->
      listUserAdapter.setListPosProduct(posProduct)
    }
    Timer().scheduleAtFixedRate(object : TimerTask() {
      override fun run() {
        mainViewModel.isLoading.value?.let {
          if (!it) {
            mainViewModel.idKeranjang.value?.let { id ->
              mainViewModel.getPosProduct(id)
            }
          }
        }
      }
    }, 0, 1500)

    val pref = SettingPreferences.getInstance(dataStore)
    val settingViewModel = ViewModelProvider(
      this@MainActivity,
      ViewModelFactory(application, pref)
    )[SettingViewModel::class.java]

    settingViewModel.getThemeSettings()
      .observe(this@MainActivity) { isDarkModeActive: Boolean ->
        setAppTheme(isDarkModeActive)
      }
  }

  override fun onCreateOptionsMenu(menu: Menu): Boolean {
    menuInflater.inflate(R.menu.menu_main, menu)
    return true
  }

  override fun onOptionsItemSelected(item: MenuItem): Boolean {
    return when (item.itemId) {
      R.id.settings -> {
        startActivity(Intent(this@MainActivity, SettingActivity::class.java))
        true
      }
      else -> super.onOptionsItemSelected(item)
    }
  }

  override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    setRecyclerViewLayoutManager(this@MainActivity, binding.rvPosProducts)
  }

//  override fun onSupportNavigateUp(): Boolean {
//    val navController = findNavController(R.id.nav_host_fragment_content_main)
//    return navController.navigateUp(appBarConfiguration)
//        || super.onSupportNavigateUp()
//  }

  private fun requestForPermission(permission: String) {
    Dexter.withContext(this@MainActivity)
      .withPermission(permission)
      .withListener(object : BasePermissionListener() {
        override fun onPermissionGranted(response: PermissionGrantedResponse) {
          Log.d(TAG, "Dexter: ${response.permissionName} granted!")
        }

        override fun onPermissionDenied(response: PermissionDeniedResponse) {
          Log.d(TAG, "Dexter: ${response.permissionName} denied!")
          runOnUiThread {
            Toast.makeText(
              this@MainActivity,
              "Dexter: ${response.permissionName} denied!",
              Toast.LENGTH_LONG
            ).show()
          }
        }
      })
      .withErrorListener { error -> Log.i(TAG, error.toString()) }
      .check()
  }

  companion object {
    private const val TAG = "MainActivity"
    const val SCAN_QR_CODE = 12345
  }
}