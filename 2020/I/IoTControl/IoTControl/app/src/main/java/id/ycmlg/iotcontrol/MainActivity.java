package id.ycmlg.iotcontrol;

import android.annotation.SuppressLint;
import android.annotation.TargetApi;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.InstanceIdResult;
import com.google.firebase.messaging.FirebaseMessaging;
import com.squareup.okhttp.MediaType;
import com.squareup.okhttp.OkHttpClient;
import com.squareup.okhttp.Request;
import com.squareup.okhttp.RequestBody;
import com.squareup.okhttp.Response;

import org.json.JSONObject;

import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {
    private static final String ROOT_PATH = "iotcontrol";
    private static final String RELAY_PATH = "relay";

    @TargetApi(Build.VERSION_CODES.LOLLIPOP)
    @RequiresApi(api = Build.VERSION_CODES.JELLY_BEAN)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        getSupportActionBar().hide();

        FirebaseDatabase database = FirebaseDatabase.getInstance();
        DatabaseReference iotControl = database.getReference(ROOT_PATH);
        FirebaseMessaging.getInstance();

        SwitchCompat switchCompat = findViewById(R.id.switchCompat);
        TextView tvOn = findViewById(R.id.tvOn);
        TextView tvOff = findViewById(R.id.tvOff);
        View screen = findViewById(R.id.screen);
        Button btFcm = findViewById(R.id.btFcm);
        Button btCrud = findViewById(R.id.btCrud);

        switchCompat.setOnCheckedChangeListener((buttonView, isChecked) -> {
            //Log.i("iotControl", "Relay: " + isChecked);
            if(isChecked){
                //write data
                iotControl.child(RELAY_PATH).setValue(true);
                tvOn.setVisibility(View.VISIBLE);
                tvOff.setVisibility(View.INVISIBLE);
            } else{
                //write data
                iotControl.child(RELAY_PATH).setValue(false);
                tvOn.setVisibility(View.INVISIBLE);
                tvOff.setVisibility(View.VISIBLE);
            }
        });

        //Read data
        iotControl.child(RELAY_PATH).addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot dataSnapshot) {
                Boolean value = dataSnapshot.getValue(Boolean.class);
                //Log.i("iotControl", "Relay: " + value);
                if(value){
                    tvOn.setVisibility(View.VISIBLE);
                    tvOff.setVisibility(View.INVISIBLE);
                } else{
                    tvOn.setVisibility(View.INVISIBLE);
                    tvOff.setVisibility(View.VISIBLE);
                }
                if (screen.getVisibility() == View.VISIBLE) {
                    screen.setVisibility(View.GONE);
                }
                if (btFcm.getVisibility() == View.INVISIBLE) {
                    btFcm.setVisibility(View.VISIBLE);
                }
                if (btCrud.getVisibility() == View.INVISIBLE) {
                    btCrud.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {
                Log.w("iotControl", "Failed to read value.", error.toException());
            }
        });

        btFcm.setOnClickListener(v -> testFCM());

        btCrud.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, CRUDActivity.class);
            startActivity(intent);
        });
    }

    @SuppressLint("StaticFieldLeak")
    private void testFCM(){
        MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        final String SERVER_KEY = "AAAAt___-W4:APA91bH7rMNaUUWg_s6V7T1ZbubDQKKjdNycS_m_gLUUrl3AeNczGFlnKohXP6jGptLLK-qBq8YYnFwKrfMTjFjqP2gyvH6yI-6wTL4s3db3gU-NAiAyTO89jPb9ZMEePNrmyttLQMZP";

        Task<String> task = FirebaseMessaging.getInstance().getToken();
        task.addOnSuccessListener(token -> {
            new AsyncTask<Void,Void,Void>(){
                @Override
                protected Void doInBackground(Void... params) {
                    try {
                        OkHttpClient client = new OkHttpClient();
                        JSONObject json=new JSONObject();
                        JSONObject dataJson=new JSONObject();
                        dataJson.put("body","Hi this is sent from device...");
                        dataJson.put("title","FCM test");
                        json.put("notification", dataJson);
                        json.put("to", token);
                        RequestBody body = RequestBody.create(JSON, json.toString());
                        Request request = new Request.Builder()
                                .header("Authorization","key="+ SERVER_KEY)
                                .url("https://fcm.googleapis.com/fcm/send")
                                .post(body)
                                .build();
                        Response response = client.newCall(request).execute();
                        String finalResponse = response.body().string();
                    }catch (Exception e){
                        //Log.d(TAG,e+"");
                    }
                    return null;
                }
            }.execute();
        });
    }
}