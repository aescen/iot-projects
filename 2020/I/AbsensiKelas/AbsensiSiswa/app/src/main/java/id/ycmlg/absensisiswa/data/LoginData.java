package id.ycmlg.absensisiswa.data;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.ValueEventListener;

public class LoginData {
    //Singleton pattern
    private static volatile LoginData instance = null;
    private static User user = null;
    private static String DEFAULT_SHARED_PREF_PASSWORD = null;
    private static final String sharedPrefPasswordPath = "dpw";
    private SharedPreferences settings;
    private SharedPreferences.Editor editor;

    public static User getUser() {
        return user;
    }

    private LoginData() {}

    public void Login(User user) {
        this.user = user;
    }

    public void Logout(){
        String p1 = settings.getString("param1", null);
        String p2 = settings.getString("param2", null);
        String p3 = settings.getString("param2", null);
        if(p1 != null) editor.remove("param1");
        if(p2 != null) editor.remove("param2");
        if(p3 != null) editor.remove("param3");
        editor.commit();
        instance = null;
        user = null;
    }

    public String getDefaultSharedPrefPassword(DatabaseReference databaseReference){
        databaseReference.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot snapshot) {
                DEFAULT_SHARED_PREF_PASSWORD = snapshot.child(sharedPrefPasswordPath).getValue().toString();
                //Log.i("dpw", "pass: " + DEFAULT_SHARED_PREF_PASSWORD);
            }

            @Override
            public void onCancelled(@NonNull DatabaseError error) {

            }
        });

        return DEFAULT_SHARED_PREF_PASSWORD;
    }

    public synchronized static LoginData getInstance() {
        if (instance == null) {
            instance = new LoginData();
        }
        return instance;
    }

    public void initSharedPref(Context context){
        settings = PreferenceManager.getDefaultSharedPreferences(context);
        editor = settings.edit();
    }

    public void prefPutString(String key, String value){
        editor.putString(key, value);
    }

    public void prefPutBoolean(String key, boolean value){
        editor.putBoolean(key, value);
    }

    public String prefGetString(String key, @Nullable String defaultValue){
        return settings.getString(key, defaultValue);
    }

    public Boolean prefGetBoolean(String key, @Nullable Boolean defaultValue){
        return settings.getBoolean(key, defaultValue);
    }

    public void prefRemove(String key){
        editor.remove(key);
    }

    public void prefCommit(){
        editor.commit();
    }

    public void prefApply(){
        editor.apply();
    }

    public void resetInstance(){
        instance = null;
        instance = new LoginData();
    }
}

