package id.ac.plnm.smartcart.ui.qrscanner.view

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.budiyev.android.codescanner.*
import com.google.zxing.BarcodeFormat
import id.ac.plnm.smartcart.databinding.ActivityQrscannerBinding


class QRScannerActivity : AppCompatActivity() {
  private lateinit var codeScanner: CodeScanner
  private lateinit var binding: ActivityQrscannerBinding

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ActivityQrscannerBinding.inflate(layoutInflater)
    setContentView(binding.root)
    val scannerView = binding.scannerView

    codeScanner = CodeScanner(this@QRScannerActivity, scannerView)

    // Parameters (default values)
    codeScanner.camera = CodeScanner.CAMERA_BACK // or CAMERA_FRONT or specific camera id
    // codeScanner.formats = CodeScanner.TWO_DIMENSIONAL_FORMATS // list of type BarcodeFormat,
    codeScanner.formats = listOf(BarcodeFormat.QR_CODE) // list of type BarcodeFormat,
    // ex. listOf(BarcodeFormat.QR_CODE)
    codeScanner.autoFocusMode = AutoFocusMode.SAFE // or CONTINUOUS
    codeScanner.scanMode = ScanMode.SINGLE // or CONTINUOUS or PREVIEW
    codeScanner.isAutoFocusEnabled = true // Whether to enable auto focus or not
    codeScanner.isFlashEnabled = false // Whether to enable flash or not

    // Callbacks
    codeScanner.decodeCallback = DecodeCallback {
      // runOnUiThread {
      //   Toast.makeText(this@QRScannerActivity, "Scan result: ${it.text}", Toast.LENGTH_LONG).show()
      // }
      val pattern = Regex("""^[\d]*[.][\d]*[.][\d]*[.][\d]*[.][\d]*$""")
      if(pattern.containsMatchIn(it.text)) {
        val resultIntent = Intent()
        resultIntent.putExtra(EXTRA_QR_CODE, it.text)
        this@QRScannerActivity.setResult(Activity.RESULT_OK, resultIntent)
        finish()
      } else {
        runOnUiThread {
          Toast.makeText(
            this@QRScannerActivity, "QR Code is not recognized: ${it.text}",
            Toast.LENGTH_LONG
          ).show()
        }
        codeScanner.stopPreview()
        codeScanner.startPreview()
      }
    }
    codeScanner.errorCallback = ErrorCallback { // or ErrorCallback.SUPPRESS
      runOnUiThread {
        Toast.makeText(
          this@QRScannerActivity, "Camera initialization error: ${it.message}",
          Toast.LENGTH_LONG
        ).show()
        this@QRScannerActivity.setResult(Activity.RESULT_CANCELED)
        finish()
      }
    }

    scannerView.setOnClickListener {
      codeScanner.startPreview()
    }
  }

  override fun onResume() {
    super.onResume()
    codeScanner.startPreview()
  }

  override fun onPause() {
    codeScanner.releaseResources()
    super.onPause()
  }

  companion object {
    const val EXTRA_QR_CODE = "QR_CODE"
  }
}