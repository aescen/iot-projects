package id.ac.plnm.smartcart.ui.main.adapter

import android.annotation.SuppressLint
import android.util.Log
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import id.ac.plnm.smartcart.R
import id.ac.plnm.smartcart.data.model.PosItem
import id.ac.plnm.smartcart.databinding.ItemRowProductBinding
import id.ac.plnm.smartcart.ui.main.adapter.ListPosProductAdapter.ListViewHolder

class ListPosProductAdapter(private var listPosProduct: ArrayList<PosItem> = arrayListOf()) :
  RecyclerView.Adapter<ListViewHolder>() {
  class ListViewHolder(var binding: ItemRowProductBinding) : RecyclerView.ViewHolder(binding.root)

  private lateinit var onItemClickCallback: OnItemClickCallback

  interface OnItemClickCallback {
    fun onItemClicked(data: PosItem)
  }

  fun setOnItemClickCallback(onItemClickCallback: OnItemClickCallback) {
    this.onItemClickCallback = onItemClickCallback
  }

  override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ListViewHolder {
    val binding: ItemRowProductBinding = ItemRowProductBinding.inflate(
      LayoutInflater.from(parent.context), parent, false
    )
    return ListViewHolder(binding)
  }

  override fun onBindViewHolder(holder: ListViewHolder, position: Int) {
    with(holder) {
      listPosProduct[position].let { product ->
        Glide.with(itemView)
          .load(product.imgUrl)
          .timeout(3700)
          .placeholder(R.drawable.ic_baseline_shopping_cart_24)
          .error(R.drawable.ic_no_image)
          .centerInside()
          .into(binding.imMainItemPhoto)
        with(binding) {
          tvMainProductName.text = product.namaProduk
          tvMainProductPrice.text = "Harga: ${product.harga}"
          tvMainProductQuantity.text = "Jumlah: ${product.jumlah}"
        }
        itemView.setOnClickListener { onItemClickCallback.onItemClicked(product) }
      }
    }
  }

  override fun getItemCount(): Int = listPosProduct.size

  @SuppressLint("NotifyDataSetChanged")
  fun setListPosProduct(newListPosProduct: ArrayList<PosItem>) {
    val diffResult =
      DiffUtil.calculateDiff(PosProductDiffUtilCallback(listPosProduct, newListPosProduct))
    listPosProduct = newListPosProduct
    try {
      diffResult.dispatchUpdatesTo(this)
    } catch (e: ArrayIndexOutOfBoundsException) {
      Log.e("MainActivity", "ListPosProductAdapter: $e")
      notifyDataSetChanged()
    }
  }
}