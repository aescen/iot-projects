package id.ycmlg.absensisiswa;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.data.User;
import id.ycmlg.absensisiswa.databinding.ActivitySplashBinding;
import id.ycmlg.absensisiswa.login.LoginActivity;
import id.ycmlg.absensisiswa.main.MainGuruActivity;
import id.ycmlg.absensisiswa.main.MainOrtuActivity;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.nfc.utils.Utils;

public class SplashActivity extends AppCompatActivity {

    //private ProgressBar loadingProgressBar;
    //private LoginData loginData;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private DatabaseReference userListRef;
    private static final String userListPath = "ul";
    private static final String userPath = "u";
    private static final String modeGuru = "g";
    private static final String modeOrtu = "o";
    private String username = "";
    private String email = "";
    private String mode = "";
    private ActivitySplashBinding splashBinding;
//    private static final String globalVariablePath = "gv";
//    private static final String sharedPrefPasswordPath = "dpw";
//    private SharedPreferences settings;
//    private DatabaseReference GLOBAL_VARIABLE;
//    private String DEFAULT_SHARED_PREF_PASSWORD;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        setTheme(R.style.SplashTheme);
        super.onCreate(savedInstanceState);

        //setContentView(R.layout.activity_splash);

        // if using view binding
        //splashBinding = ActivitySplashBinding.inflate(getLayoutInflater());
        //View view = splashBinding.getRoot();
        //setContentView(view);
        //splashBinding.text.setText("Loading...");
        //TextView textView = splashBinding.text;


        if (Utils.isConnectedToInternet(SplashActivity.this)) {
            //loginData = LoginData.getInstance();
            //loginData.initSharedPref(this);
            firebaseAuth = FirebaseAuth.getInstance();
            //FirebaseDatabase.getInstance().setPersistenceEnabled(true);
            database = FirebaseDatabase.getInstance();
            //GLOBAL_VARIABLE = database.getReference().child(globalVariablePath);
            userRef = database.getReference(userPath);
            userListRef = database.getReference(userListPath);

            checkCred();

        } else {
            Toast.makeText(this, "Please check your Internet connection!", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    private void checkCred(){
        if(firebaseAuth.getCurrentUser() != null){
            DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
            uuid.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override public void onDataChange(@NonNull DataSnapshot snapshot) {
                    username = snapshot.child("un").getValue().toString();
                    email = snapshot.child("e").getValue().toString();
                    mode = snapshot.child("m").getValue().toString();
                    //Log.i("SplashScreen", "params: " + username + ":" + email + ":" + mode);
                    User user = new User(username, email, mode);
                    //LoginData.getInstance().Login(user);
                    loadLoginUi();
                    uuid.removeEventListener(this);
                }
                @Override public void onCancelled(@NonNull DatabaseError error) {}
            });

            //loadingProgressBar.setVisibility(View.GONE);
        } else { cleanPrefs(); }
    }

    private void loadLoginUi(){
        if (mode.contentEquals(modeGuru)) {
            Intent intent = new Intent(this, MainGuruActivity.class);
            if (!LocalUserService.isAppServiceRunning(this)) {
                try {
                    if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
                } catch (Exception e) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        //startForegroundService(new Intent(this, AppService.class));
                    }
                    e.printStackTrace();
                }
                //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
            }
            startActivity(intent);
            finish();
        } else if (mode.contentEquals(modeOrtu)){
            Intent intent = new Intent(this, MainOrtuActivity.class);
            if (!LocalUserService.isAppServiceRunning(this)) {
                try {
                    if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
                } catch (Exception e) {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        //startForegroundService(new Intent(this, AppService.class));
                    }
                    e.printStackTrace();
                }
                //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
            }
            startActivity(intent);
            finish();
        } else {
            cleanPrefs();
        }
    }

    private void cleanPrefs(){
        firebaseAuth.signOut();
        //LoginData.getInstance().Logout();
        Intent intent = new Intent(SplashActivity.this, LoginActivity.class);
        //loadingProgressBar.setVisibility(View.GONE);
        finish();
        startActivity(intent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        LocalUserService.appResumed();
    }

    @Override
    protected void onPause() {
        super.onPause();
        LocalUserService.appPaused();
        finish();
    }
}

//loadingProgressBar = findViewById(R.id.progressBarSplash);

//loadingProgressBar.setVisibility(View.VISIBLE);
        /*
        try {
            int TAG_LENGTH_BIT = 128; // must be one of {128, 120, 112, 104, 96}
            int IV_LENGTH_BYTE = 12;
            int SALT_LENGTH_BYTE = 16;
            Charset UTF_8 = StandardCharsets.UTF_8;
            String OUTPUT_FORMAT = "%-30s:%s";
            String PASSWORD = "this is a password";
            String pText = "AES-GSM Password-Bases encryption!";
            String encryptedTextBase64 = null;
            encryptedTextBase64 = AesGcmCryptor.encrypt(pText, PASSWORD);
            String decryptedText = AesGcmCryptor.decrypt(encryptedTextBase64, PASSWORD);
            Log.i("CryptTest", "onCreate: \n------ AES GCM Password-based Encryption ------");
            Log.i("CryptTest", "onCreate: " + String.format(OUTPUT_FORMAT, "Input (plain text)", pText));
            Log.i("CryptTest", "onCreate: " + String.format(OUTPUT_FORMAT, "Encrypted (base64) ", encryptedTextBase64));
            Log.i("CryptTest", "onCreate: \n------ AES GCM Password-based Decryption ------");
            Log.i("CryptTest", "onCreate: " + String.format(OUTPUT_FORMAT, "Input (base64)", encryptedTextBase64));
            Log.i("CryptTest", "onCreate: " + String.format(OUTPUT_FORMAT, "Decrypted (plain text)", decryptedText));
        } catch (Exception e) {
            e.printStackTrace();
        }
        */

//            String username = loginData.prefGetString("param1", null);
//            String email = loginData.prefGetString("param2", null);
//            String mode = loginData.prefGetString("param3", null);
//            settings = PreferenceManager.getDefaultSharedPreferences(getBaseContext());
//            boolean firstRun = settings.getBoolean("firstRun", true);

//            GLOBAL_VARIABLE.addListenerForSingleValueEvent(new ValueEventListener() {
//                @Override
//                public void onDataChange(@NonNull DataSnapshot snapshot) {
//                    DEFAULT_SHARED_PREF_PASSWORD = snapshot.child(sharedPrefPasswordPath).getValue().toString();
//                    if(DEFAULT_SHARED_PREF_PASSWORD != null) {
//                        checkCred();
//                        GLOBAL_VARIABLE.removeEventListener(this);
//                    }
//                }
//
//                @Override
//                public void onCancelled(@NonNull DatabaseError error) {
//
//                }
//            });

//            final Handler handler = new Handler();
//            handler.postDelayed(() -> checkCred(), 5000);

//        username = AesGcmCryptor.decrypt(username, DEFAULT_SHARED_PREF_PASSWORD);
//        email = AesGcmCryptor.decrypt(email, DEFAULT_SHARED_PREF_PASSWORD);
//        mode = AesGcmCryptor.decrypt(mode, DEFAULT_SHARED_PREF_PASSWORD);