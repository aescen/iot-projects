package id.ac.plnm.smartcart.ui.main.viewmodel

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import id.ac.plnm.smartcart.data.DataClient
import id.ac.plnm.smartcart.data.model.PosItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okio.IOException

class MainViewModel : ViewModel() {
  private val _qrKeranjang = MutableLiveData<String?>()
  val qrKeranjang: LiveData<String?> = _qrKeranjang

  private val _idKeranjang = MutableLiveData<String?>()
  val idKeranjang: LiveData<String?> = _idKeranjang

  private val _posProduct = MutableLiveData<ArrayList<PosItem>>()
  val posProduct: LiveData<ArrayList<PosItem>> = _posProduct

  private val _totalProduct = MutableLiveData<Int?>()
  val totalProduct: LiveData<Int?> = _totalProduct

  private val _totalPrice = MutableLiveData<Int?>()
  val totalPrice: LiveData<Int?> = _totalPrice

  private val _isLoading = MutableLiveData<Boolean>()
  val isLoading: LiveData<Boolean> = _isLoading

  private val _isError = MutableLiveData<Boolean>()
  val isError: LiveData<Boolean> = _isError

  init {
    _idKeranjang.value = null
    _posProduct.value = arrayListOf()
    _isError.value = false
    _isLoading.value = false
  }

  fun setQrKeranjang(qrKeranjang: String?) {
    _qrKeranjang.postValue(qrKeranjang)
  }

  fun updatePosProductList(qrKeranjang: String) {
    _isLoading.postValue(true)
    viewModelScope.launch(Dispatchers.IO) {
      try {
        val callGetIdKeranjang = DataClient.apiClient().getIdKeranjang(qrKeranjang)
        val resIdKeranjang = callGetIdKeranjang.execute()
        _isError.postValue(resIdKeranjang.isSuccessful.not())
        if (resIdKeranjang.isSuccessful) {
          resIdKeranjang.body()?.let { idKeranjang ->
            idKeranjang[0].id?.let { id ->
              _idKeranjang.postValue(id)
              getPosProduct(id)
            }
          }
        } else {
          Log.e(TAG, "onFailure: ${resIdKeranjang.message()}")
        }
      } catch (e: IOException) {
        Log.e(TAG, "netFailure: ${e.message.toString()}")
        _isError.postValue(true)
      }
    }
    _isLoading.postValue(false)
  }

  fun getPosProduct(idKeranjang: String) {
    _isLoading.postValue(true)
    viewModelScope.launch(Dispatchers.IO) {
      try {
        val callGetPosProduct = DataClient.apiClient().getPosProduct(idKeranjang)
        val resPosProduct = callGetPosProduct.execute()
        _isError.postValue(resPosProduct.isSuccessful.not())
        if (resPosProduct.isSuccessful) {
          resPosProduct.body()?.let { posProduct ->
            val products = posProduct as ArrayList<PosItem>?
            val items = products?.fold(0) { sum, item ->
              sum + (item.jumlah?.toInt() ?: 0)
            } ?: 0
            val prices = products?.fold(0) { sum, item ->
              sum + ((item.harga?.toInt() ?: 0) * (item.jumlah?.toInt() ?: 0))
            } ?: 0
            _posProduct.postValue(products)
            _totalProduct.postValue(items)
            _totalPrice.postValue(prices)
          }
        }
      } catch (e: IOException) {
        Log.e(TAG, "netFailure: ${e.message.toString()}")
        _isError.postValue(true)
      }
    }
    _isLoading.postValue(false)
  }

  companion object {
    private const val TAG = "MainViewModel"
    private const val CANCEL_MSG = "User request to cancel search"
  }
}
