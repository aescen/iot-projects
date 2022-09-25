package id.ac.plnm.smartcart.data

import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import id.ac.plnm.smartcart.BuildConfig
import id.ac.plnm.smartcart.data.api.ApiConstants.API_BASE_URL
import id.ac.plnm.smartcart.data.api.ApiService
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.jackson.JacksonConverterFactory

object DataClient {
  fun apiClient(): ApiService {
    val loggingInterceptor = if (BuildConfig.DEBUG) {
      HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY)
    } else {
      HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.NONE)
    }
    val client = OkHttpClient.Builder()
      .addInterceptor(loggingInterceptor)
      .build()
    val retrofit = Retrofit.Builder()
      .baseUrl(API_BASE_URL)
      .addConverterFactory(JacksonConverterFactory.create(jacksonObjectMapper()))
      .client(client)
      .build()
    return retrofit.create(ApiService::class.java)
  }
}
