package id.ycmlg.absensisiswa.main.chat;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.chatadapter.FriendListAdapter;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.chat.chatservices.DataContext;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class ChatAddContactActivity extends AppCompatActivity {
    ListView lv_SerachList;
    EditText searchKey;
    ProgressDialog pd;
    private static FirebaseDatabase database;
    private DataContext db;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat_add_contact);
        getSupportActionBar().setTitle("Add Contacts");
        database = FirebaseDatabase.getInstance();
        db = new DataContext(this, null, null, 1);
        pd = new ProgressDialog(this);
        pd.setMessage("Searching...");
        lv_SerachList = findViewById(R.id.lv_AddContactList);
        searchKey = findViewById(R.id.et_SearchKey);
        // listener for item click
        lv_SerachList.setOnItemClickListener(
                (parent, view, position, id) -> {
                    TextView email = view.findViewById(R.id.tv_HiddenEmail);
                    // start FriendProfileFull
                    Intent intent = new Intent(ChatAddContactActivity.this, ChatFriendProfileActivity.class);
                    intent.putExtra("Email", email.getText().toString());
                    startActivity(intent);
                }
        );
    }

    @Override
    protected void onStart() {
        super.onStart();
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
    }

    public void btn_SearchClick(View view) {
        if (!searchKey.getText().toString().trim().equals("") && searchKey.getText().toString().length() > 2) {

            if (Tools.isNetworkAvailable(this)){
                FindFriendsTask t = new FindFriendsTask();
                t.execute();
            }else {
                Toast.makeText(this, "Please check your internet connection.", Toast.LENGTH_SHORT).show();
            }

        } else {
            searchKey.setText("");
            Toast.makeText(this, "Input at least 3 characters", Toast.LENGTH_SHORT).show();
        }
    }

    public class FindFriendsTask extends AsyncTask<Void, Void, String> {

        @Override
        protected void onPreExecute() {
            runOnUiThread(() -> pd.show());
        }

        @Override
        protected String doInBackground(Void... params) {
            User user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
            List<User> friendList = new ArrayList<>();
            DatabaseReference usersRef = database.getReferenceFromUrl(StaticInfo.UsersURL + "/");
            usersRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    for (DataSnapshot aUser: snapshot.getChildren()) {
                        User f = new User();
                        //f.uid = aUser.child("uid").getValue(String.class);
                        f.id = aUser.child("id").getValue(String.class);
                        f.Email = Tools.decodeString(aUser.child("Email").getValue(String.class));
                        f.FirstName = aUser.child("FirstName").getValue(String.class);
                        f.LastName = aUser.child("LastName").getValue(String.class);
                        String serKey = searchKey.getText().toString().toLowerCase().trim();
                        String fullName = f.FirstName.toLowerCase() + " " + f.LastName.toLowerCase();
                        if (f.Email.toLowerCase().contains(serKey) || fullName.contains(serKey) || f.id.contains(serKey)) {
                            if (!f.Email.equals(user.Email)) {
                                friendList.add(f);
                            }
                        }
                    }

                    ListAdapter adp = new FriendListAdapter(ChatAddContactActivity.this, friendList);
                    lv_SerachList.setAdapter(adp);
                    runOnUiThread(() -> pd.hide());
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    runOnUiThread(() -> {
                        pd.hide();
                        Toast.makeText(ChatAddContactActivity.this, "Please check your internet connection.", Toast.LENGTH_SHORT).show();
                    });
                }
            });
            return null;
        }

        @Override protected void onPostExecute(String jsonListString) {}
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
    }
}
