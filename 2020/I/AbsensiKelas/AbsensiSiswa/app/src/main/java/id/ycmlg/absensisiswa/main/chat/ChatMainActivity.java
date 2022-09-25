package id.ycmlg.absensisiswa.main.chat;

import android.app.Activity;
import android.app.NotificationManager;
import android.app.ProgressDialog;
import android.content.Intent;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentPagerAdapter;
import androidx.viewpager.widget.ViewPager;

import com.google.android.material.tabs.TabLayout;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.login.LoginActivity;
import id.ycmlg.absensisiswa.main.chat.chatadapter.AdapterLastChat;
import id.ycmlg.absensisiswa.main.chat.chatadapter.FriendListAdapter;
import id.ycmlg.absensisiswa.main.chat.chatmodels.Message;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatmodels.User;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.chat.chatservices.DataContext;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

public class
ChatMainActivity extends AppCompatActivity {
    private SectionsPagerAdapter mSectionsPagerAdapter;
    private ViewPager mViewPager;
    private User user;
    private static FirebaseDatabase database;
    private DatabaseReference refUser;
    private DataContext db;
    private ProgressDialog pd;
    private List<Message> userLastChatList;
    private List<User> userFriendList;
    private FriendListAdapter userFriendListAdp;
    private AdapterLastChat userLastChatAdp;
    private ListView lv_LastChatList;
    private ListView lv_FriendList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat_main);
        database = FirebaseDatabase.getInstance();
        db = new DataContext(this, null, null, 1);
        pd = new ProgressDialog(this);
        pd.setMessage("Refreshing...");
        Toolbar toolbar = findViewById(R.id.toolbarChatMain);
        setSupportActionBar(toolbar);
        getSupportActionBar().setTitle("My Chats");
        mSectionsPagerAdapter = new SectionsPagerAdapter(getSupportFragmentManager(),
                FragmentPagerAdapter.BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT);
        // Set up the ViewPager with the sections adapter.
        mViewPager = findViewById(R.id.containerChat);
        mViewPager.setAdapter(mSectionsPagerAdapter);
        TabLayout tabLayout = findViewById(R.id.tabsChat);
        tabLayout.setupWithViewPager(mViewPager);
    }

    @Override
    protected void onStart() {
        super.onStart();
        user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
        if (user.Email == null) {
            // send to activitylogin
            Intent intent = new Intent(this, LoginActivity.class);
            startActivity(intent);
            FirebaseAuth firebaseAuth = FirebaseAuth.getInstance();
            firebaseAuth.signOut();
            finish();
        } else {
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
        database = FirebaseDatabase.getInstance();
        refUser = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(user.Email));

        // refresh last chat
        refreshLastChat();

        // refresh contacts
        userFriendList = db.getUserFriendList();
        userFriendListAdp = new FriendListAdapter(this, userFriendList);
        lv_FriendList = findViewById(R.id.lv_FriendList);
        if (lv_FriendList != null) {
            lv_FriendList.setAdapter(userFriendListAdp);
            lv_FriendList.setOnItemLongClickListener((parent, view, position, id) -> {
                if (userFriendList.size() <= position) return false;
                final User selectedUser = userFriendList.get(position);
                final CharSequence[] options = new CharSequence[]{"Profile", "Delete Contact"};
                AlertDialog.Builder builder = new AlertDialog.Builder(ChatMainActivity.this);
                builder.setTitle(selectedUser.FirstName + " " + selectedUser.LastName);
                builder.setItems(options, (dialog, index) -> {
                    // the user clicked on list[index]
                    if (index == 0) {
                        // Profile
                        Intent intent = new Intent(ChatMainActivity.this, ChatFriendProfileActivity.class);
                        intent.putExtra("Email", selectedUser.Email);
                        startActivityForResult(intent, StaticInfo.ChatAciviityRequestCode);
                    } else {
                        // Delete Contact
                        new AlertDialog.Builder(ChatMainActivity.this)
                                .setTitle(selectedUser.FirstName + " " + selectedUser.LastName)
                                .setMessage("Are you sure to delete this contact?")
                                .setPositiveButton("Delete", (dialog12, which) -> {
                                    DatabaseReference ref = database.getReferenceFromUrl(StaticInfo.EndPoint + "/friends/" + Tools.encodeString(user.Email) + "/" + Tools.encodeString(selectedUser.Email));
                                    ref.removeValue();
                                    // delete from local database
                                    db.deleteFriendByEmailFromLocalDB(selectedUser.Email);
                                    Toast.makeText(ChatMainActivity.this, "Contact deleted successfully", Toast.LENGTH_SHORT).show();
                                    userFriendList = db.getUserFriendList();
                                    ListAdapter adp1 = new FriendListAdapter(ChatMainActivity.this, userFriendList);
                                    lv_FriendList.setAdapter(adp1);
                                })
                                .setNegativeButton(android.R.string.no, null)
                                .show();
                    }
                });

                builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());

                builder.show();

                return true;
            });
        }

        // set online status
        user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
        if (user.Email != null) {
            if (refUser == null) {
                refUser = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(user.Email));
            }
        } else {
            Toast.makeText(this, "Email is null.", Toast.LENGTH_SHORT).show();
        }
        if (refUser != null) refUser.child("Status").setValue("Online");

    }

    public void refreshLastChat() {
        runOnUiThread(()->{
            userLastChatList = db.getUserLastChatList(user.Email);
            userLastChatAdp = new AdapterLastChat(this, userLastChatList);
            lv_LastChatList = findViewById(R.id.lv_LastChatList);
            if (lv_LastChatList != null) {
                lv_LastChatList.setAdapter(userLastChatAdp);
                lv_LastChatList.setOnItemLongClickListener((parent, view, position, id) -> {
                    if (userLastChatList.size() <= position) return false;
                    final Message selectedMessageItem = userLastChatList.get(position);
                    final CharSequence[] options = new CharSequence[]{"Delete Chat"};
                    AlertDialog.Builder builder = new AlertDialog.Builder(ChatMainActivity.this);
                    builder.setTitle(selectedMessageItem.FriendFullName);
                    builder.setItems(options, (dialog, index) -> {
                        // the user clicked on list[index]
                        if (index == 0) {
                            // Delete Chat
                            new AlertDialog.Builder(ChatMainActivity.this)
                                    .setTitle(selectedMessageItem.FriendFullName)
                                    .setMessage("Are you sure to delete this chat?")
                                    .setPositiveButton("Delete", (dialog1, which) -> {
                                        db.deleteChat(user.Email, selectedMessageItem.FromMail);
                                        Toast.makeText(getApplicationContext(), "Chat deleted successfully", Toast.LENGTH_SHORT).show();
                                        userLastChatList = db.getUserLastChatList(user.Email);
                                        ListAdapter adp = new AdapterLastChat(getApplicationContext(), userLastChatList);
                                        lv_LastChatList.setAdapter(adp);
                                    })
                                    .setNegativeButton(android.R.string.no, null)
                                    .show();
                        }
                    });

                    builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());
                    builder.show();
                    return true;
                });
            } 
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // set last seen
        DateFormat dateFormat = new SimpleDateFormat("dd MM yy hh:mm a");
        Date date = new Date();
        refUser.child("Status").setValue(dateFormat.format(date));
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_chat_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.menu_logout) {
            new AlertDialog.Builder(this)
                    .setTitle("Logout?")
                    .setMessage("Are you sure to logout, you will no longer receive notifications.")
                    .setPositiveButton("Logout", (dialog, which) -> {
                        // set last seen
                        DateFormat dateFormat = new SimpleDateFormat("dd MM yy hh:mm a");
                        Date date = new Date();
                        refUser.child("Status").setValue(dateFormat.format(date));
                        NotificationManager not = (NotificationManager)getSystemService(NOTIFICATION_SERVICE);
                        not.cancelAll();
                        if (LocalUserService.deleteLocalUserFromPreferences(getApplicationContext())) {
                            db.deleteAllFriendsFromLocalDB();
                            //stopService(new Intent(getApplicationContext(), AppService.class));
                            //Toast.makeText(getApplicationContext(), "Logout Success", Toast.LENGTH_SHORT).show();
                            Intent intent = new Intent(getApplicationContext(), LoginActivity.class);
                            startActivity(intent);
                        } else {
                            //Toast.makeText(getApplicationContext(), "Logout Success", Toast.LENGTH_SHORT).show();
                            Intent intent = new Intent(getApplicationContext(), LoginActivity.class);
                            startActivity(intent);
                        }
                        finish();
                    })
                    .setNegativeButton(android.R.string.no, null)
                    .show();
            return true;
        }
        if (id == R.id.menu_profile) {
            startActivity(new Intent(this, ChatProfileActivity.class));

        }

        if (id == R.id.menu_addContacts) {
            startActivity(new Intent(this, ChatAddContactActivity.class));
            return true;
        }

        if (id == R.id.menu_notification) {
            startActivity(new Intent(this, ChatNotificationActivity.class));
            return true;
        }

        if (id == R.id.menu_refresh) {
            if (Tools.isNetworkAvailable(this)){
                RefreshChatListTask r = new RefreshChatListTask();
                FriendListTask t = new FriendListTask();
                r.execute();
                t.execute();
            }else {
                Toast.makeText(this, "Please check your internet connection.", Toast.LENGTH_SHORT).show();
            }

        }

        return super.onOptionsItemSelected(item);
    }

    private static class SectionsPagerAdapter extends FragmentPagerAdapter {
        public SectionsPagerAdapter(@NonNull FragmentManager fm, int behavior) {
            super(fm, behavior);
        }

        @NonNull
        @Override
        public Fragment getItem(int position) {
            return PlaceholderFragment.newInstance(position + 1);
        }

        @Override
        public int getCount() {
            return 2;
        }

        @Override
        public CharSequence getPageTitle(int position) {
            switch (position) {
                case 0:
                    return "CHATS";
                case 1:
                    return "CONTACTS";
            }
            return null;
        }
    }

    public static class PlaceholderFragment extends Fragment{
        private static final String ARG_SECTION_NUMBER = "section_number";
        private View rootView;
        private ListView lv_LastChatList;
        private DataContext db;
        User user;
        private List<User> userFriendList;
        private List<Message> userLastChatList;

        public PlaceholderFragment() {}

        public static PlaceholderFragment newInstance(int sectionNumber) {
            PlaceholderFragment fragment = new PlaceholderFragment();
            Bundle args = new Bundle();
            args.putInt(ARG_SECTION_NUMBER, sectionNumber);
            fragment.setArguments(args);
            return fragment;
        }

        @Override
        public View onCreateView(@NonNull LayoutInflater inflater, ViewGroup container,
                                 Bundle savedInstanceState) {
            if (user == null) {
                user = LocalUserService.getLocalUserFromPreferences(requireActivity());
            }
            db = new DataContext(requireActivity(), null, null, 1);
            // Chat tab
            if (getArguments().getInt(ARG_SECTION_NUMBER) == 1) {
                rootView = inflater.inflate(R.layout.fragment_chat, container, false);
                userLastChatList = db.getUserLastChatList(user.Email);
                ListAdapter adp = new AdapterLastChat(requireActivity(), userLastChatList);
                lv_LastChatList = rootView.findViewById(R.id.lv_LastChatList);
                lv_LastChatList.setAdapter(adp);
                lv_LastChatList.setOnItemClickListener(
                        (parent, view, position, id) -> {
                            TextView email = view.findViewById(R.id.tv_lastChat_HiddenEmail);
                            TextView tv_Name = view.findViewById(R.id.tv_lastChat_FriendFullName);
                            Intent intend = new Intent(requireActivity(), ChatActivity.class);
                            intend.putExtra("FriendEmail", email.getText().toString());
                            intend.putExtra("FriendFullName", tv_Name.getText().toString());
                            startActivity(intend);
                        }
                );

                lv_LastChatList.setOnItemLongClickListener((parent, view, position, id) -> {
                    if (userLastChatList.size() <= position) return false;
                    final Message selectedMessageItem = userLastChatList.get(position);
                    final CharSequence[] options = new CharSequence[]{"Delete Chat"};
                    AlertDialog.Builder builder = new AlertDialog.Builder(requireActivity());
                    builder.setTitle(selectedMessageItem.FriendFullName);
                    builder.setItems(options, (dialog, index) -> {
                        // the user clicked on list[index]
                        if (index == 0) {
                            // Delete Chat
                            new AlertDialog.Builder(requireActivity())
                                    .setTitle(selectedMessageItem.FriendFullName)
                                    .setMessage("Are you sure to delete this chat?")
                                    .setPositiveButton("Delete", (dialog1, which) -> {
                                        db.deleteChat(user.Email, selectedMessageItem.FromMail);
                                        Toast.makeText(requireActivity(), "Chat deleted successfully", Toast.LENGTH_SHORT).show();
                                        userLastChatList = db.getUserLastChatList(user.Email);
                                        ListAdapter adp1 = new AdapterLastChat(requireActivity(), userLastChatList);
                                        lv_LastChatList = rootView.findViewById(R.id.lv_LastChatList);
                                        lv_LastChatList.setAdapter(adp1);
                                    })
                                    .setNegativeButton(android.R.string.no, null)
                                    .show();
                        }
                    });

                    builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());

                    builder.show();

                    return true;
                });

                return rootView;
            }
            // Contacts tab
            else {
                rootView = inflater.inflate(R.layout.fragment_contact, container, false);
                userFriendList = db.getUserFriendList();
                ListAdapter adp = new FriendListAdapter(requireActivity(), userFriendList);
                ListView lv_FriendList = rootView.findViewById(R.id.lv_FriendList);
                lv_FriendList.setAdapter(adp);
                lv_FriendList.setOnItemClickListener(
                        (parent, view, position, id) -> {
                            TextView email = view.findViewById(R.id.tv_HiddenEmail);
                            TextView tv_Name = view.findViewById(R.id.tv_FriendFullName);
                            Intent intend = new Intent(requireActivity(), ChatActivity.class);
                            intend.putExtra("FriendEmail", email.getText().toString());
                            intend.putExtra("FriendFullName", tv_Name.getText().toString());
                            startActivity(intend);
                        }

                );

                lv_FriendList.setOnItemLongClickListener((parent, view, position, id) -> {
                    if (userFriendList.size() <= position) return false;
                    final User selectedUser = userFriendList.get(position);
                    final CharSequence[] options = new CharSequence[]{"Profile", "Delete Contact"};
                    AlertDialog.Builder builder = new AlertDialog.Builder(requireActivity());
                    builder.setTitle(selectedUser.FirstName + " " + selectedUser.LastName);
                    builder.setItems(options, (dialog, index) -> {
                        // the user clicked on list[index]
                        if (index == 0) {
                            // Profile
                            Intent intent = new Intent(requireActivity(), ChatFriendProfileActivity.class);
                            intent.putExtra("Email", selectedUser.Email);
                            startActivityForResult(intent, StaticInfo.ChatAciviityRequestCode);
                        } else {
                            // Delete Contact
                            new AlertDialog.Builder(requireActivity())
                                    .setTitle(selectedUser.FirstName + " " + selectedUser.LastName)
                                    .setMessage("Are you sure to delete this contact?")
                                    .setPositiveButton("Delete", (dialog12, which) -> {
                                        DatabaseReference ref = database.getReferenceFromUrl(StaticInfo.EndPoint + "/friends/" + Tools.encodeString(user.Email) + "/" + Tools.encodeString(selectedUser.Email));
                                        ref.removeValue();
                                        // delete from local database
                                        db.deleteFriendByEmailFromLocalDB(selectedUser.Email);
                                        Toast.makeText(requireActivity(), "Contact deleted successfully", Toast.LENGTH_SHORT).show();
                                        userFriendList = db.getUserFriendList();
                                        ListAdapter adp12 = new FriendListAdapter(requireActivity(), userFriendList);
                                        ListView lv_FriendList1 = rootView.findViewById(R.id.lv_FriendList);
                                        lv_FriendList1.setAdapter(adp12);
                                    })
                                    .setNegativeButton(android.R.string.no, null)
                                    .show();
                        }
                    });

                    builder.setNegativeButton("Cancel", (dialog, which) -> dialog.cancel());

                    builder.show();


                    return true;
                });
                return rootView;
            }

        }
    }

    public class RefreshChatListTask extends AsyncTask<Void, Void, String> {
        @Override protected void onPreExecute() {
            //runOnUiThread(() -> pd.show());
        }
        @Override
        protected String doInBackground(Void... params) {
            refreshLastChat();
            return null;
        }
        @Override protected void onPostExecute(String jsonListString) {
            //runOnUiThread(() -> pd.hide());
        }
    }

    public class FriendListTask extends AsyncTask<Void, Void, String> {

        @Override
        protected void onPreExecute() {
            runOnUiThread(() -> pd.show());
        }

        @Override
        protected String doInBackground(Void... params) {
            user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
            DatabaseReference friendRef = database.getReferenceFromUrl(StaticInfo.FriendsURL + "/" + Tools.encodeString(user.Email));
            friendRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    user = LocalUserService.getLocalUserFromPreferences(getApplicationContext());
                    List<User> friendList = new ArrayList<>();
                    for (DataSnapshot friendNode: snapshot.getChildren()) {
                        User friend = new User();
                        friend.id = friendNode.child("id").getValue(String.class);
                        friend.Email = Tools.encodeString(friendNode.child("Email").getValue(String.class));
                        friend.FirstName = friendNode.child("FirstName").getValue(String.class);
                        friend.LastName = friendNode.child("LastName").getValue(String.class);
                        friendList.add(friend);
                    }

                    // refresh local database
                    db = new DataContext(getApplicationContext(), null, null, 1);
                    db.refreshUserFriendList(friendList);

                    // set to adapter
                    ListAdapter adp = new FriendListAdapter(getApplicationContext(), db.getUserFriendList());
                    ListView lv_FriendList = findViewById(R.id.lv_FriendList);
                    lv_FriendList.setAdapter(adp);
                    runOnUiThread(() -> pd.hide());
                    //Toast.makeText(ChatMainActivity.this, "Contact list is updated", Toast.LENGTH_SHORT).show();
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    Toast.makeText(ChatMainActivity.this, "Contact list update cancelled", Toast.LENGTH_SHORT).show();
                    runOnUiThread(() -> pd.hide());
                }
            });
            return null;
        }

        @Override
        protected void onPostExecute(String jsonListString) {Toast.makeText(ChatMainActivity.this, "Updated", Toast.LENGTH_SHORT).show();}
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        user = LocalUserService.getLocalUserFromPreferences(this);
        if (requestCode == 100 && resultCode == Activity.RESULT_OK) {
            if (refUser == null) {
                refUser = database.getReferenceFromUrl(StaticInfo.UsersURL + "/" + Tools.encodeString(user.Email));
            }
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
            FriendListTask t = new FriendListTask();
            t.execute();
        }
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
