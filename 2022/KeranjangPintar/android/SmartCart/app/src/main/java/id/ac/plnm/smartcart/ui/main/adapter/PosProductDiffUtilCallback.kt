package id.ac.plnm.smartcart.ui.main.adapter

import androidx.recyclerview.widget.DiffUtil
import id.ac.plnm.smartcart.data.model.PosItem

class PosProductDiffUtilCallback(
  private val oldList: ArrayList<PosItem>,
  private val newList: ArrayList<PosItem>
) : DiffUtil.Callback() {

  override fun getOldListSize(): Int = oldList.size

  override fun getNewListSize(): Int = newList.size

  override fun areItemsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean =
    oldList[oldItemPosition].id.contentEquals(newList[newItemPosition].id)

  override fun areContentsTheSame(oldItemPosition: Int, newItemPosition: Int): Boolean {
    val id = oldList[oldItemPosition].id == newList[newItemPosition].id
    val namaProduk = oldList[oldItemPosition].namaProduk == newList[newItemPosition].namaProduk
    val deskripsi = oldList[oldItemPosition].deskripsi == newList[newItemPosition].deskripsi
    val harga = oldList[oldItemPosition].harga == newList[newItemPosition].harga
    val jumlah = oldList[oldItemPosition].jumlah == newList[newItemPosition].jumlah
    val sisa = oldList[oldItemPosition].sisa == newList[newItemPosition].sisa
    val imgUrl = oldList[oldItemPosition].imgUrl == newList[newItemPosition].imgUrl
    return id && (namaProduk || deskripsi || harga || jumlah || sisa || imgUrl)
  }
}
