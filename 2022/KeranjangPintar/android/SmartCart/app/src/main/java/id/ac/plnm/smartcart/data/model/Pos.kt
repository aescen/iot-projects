package id.ac.plnm.smartcart.data.model

import android.os.Parcelable
import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import kotlinx.parcelize.Parcelize

@Parcelize
@JsonIgnoreProperties(ignoreUnknown = true)
data class Pos (
  @field:JsonProperty("pos") val items: List<PosItem?>? = null
) : Parcelable

@Parcelize
@JsonIgnoreProperties(ignoreUnknown = true)
data class PosItem(
  @field:JsonProperty("id") val id: String? = null,
  @field:JsonProperty("id_keranjang") val idKeranjang: String? = null,
  @field:JsonProperty("id_user") val idUser: String? = null,
  @field:JsonProperty("id_produk") val idProduk: String? = null,
  @field:JsonProperty("nama_user") val namaUser: String? = null,
  @field:JsonProperty("nama_produk") val namaProduk: String? = null,
  @field:JsonProperty("deskripsi") val deskripsi: String? = null,
  @field:JsonProperty("harga") val harga: String? = null,
  @field:JsonProperty("jumlah") val jumlah: String? = null,
  @field:JsonProperty("sisa") val sisa: String? = null,
  @field:JsonProperty("img_url") val imgUrl: String? = null,
) : Parcelable