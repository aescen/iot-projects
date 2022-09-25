package id.ac.plnm.smartcart.data.model

import android.os.Parcelable
import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import kotlinx.parcelize.Parcelize

@Parcelize
@JsonIgnoreProperties(ignoreUnknown = true)
data class Keranjang (
  @field:JsonProperty("keranjang") val ids: List<IdKeranjang?>? = null
) : Parcelable

@Parcelize
@JsonIgnoreProperties(ignoreUnknown = true)
data class IdKeranjang(
  @field:JsonProperty("id") val id: String? = null,
) : Parcelable
