package id.ac.plnm.smartcart.data.api

import id.ac.plnm.smartcart.data.model.IdKeranjang
import id.ac.plnm.smartcart.data.model.PosItem
import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Query

interface ApiService {
  @GET(ApiConstants.GET_KERANJANG)
  fun getIdKeranjang(@Query("keranjang") keranjang: String): Call<List<IdKeranjang>>

  @GET(ApiConstants.GET_POS)
  fun getPosProduct(@Query("idKeranjang") idKeranjang: String): Call<List<PosItem>>
}
