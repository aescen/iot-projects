package id.ycmlg.absensisiswa.login;

import android.app.ProgressDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.User;
import id.ycmlg.absensisiswa.databinding.FragmentLoginGuruBinding;
import id.ycmlg.absensisiswa.main.MainGuruActivity;
import id.ycmlg.absensisiswa.main.chat.chatmodels.StaticInfo;
import id.ycmlg.absensisiswa.main.chat.chatservices.Tools;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LoginGuruFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LoginGuruFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    public LoginGuruFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment LoginGuruFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static LoginGuruFragment newInstance(String param1, String param2) {
        LoginGuruFragment fragment = new LoginGuruFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam1 = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
        }

        firebaseAuth = FirebaseAuth.getInstance();
        database = FirebaseDatabase.getInstance();
        userRef = database.getReference(userPath);
        userListRef = database.getReference(userListPath);
//        GLOBAL_VARIABLE = database.getReference(globalVariablePath);
//        loginData = LoginData.getInstance();
//        loginData.initSharedPref(requireContext());
//        DEFAULT_SHARED_PREF_PASSWORD = loginData.getDefaultSharedPrefPassword(GLOBAL_VARIABLE);

        if(firebaseAuth.getCurrentUser() != null){
            Intent intent = new Intent(requireActivity(), MainGuruActivity.class);
            startActivity(intent);
            requireActivity().finish();
        }
    }

   /*
    * if using view binding enable this override
    *
    @Override
    public void onDestroyView() {
        super.onDestroyView();
        loginGuruBinding = null;
    }
    */


    private EditText ed_nip;
    private EditText ed_pw_guru;
    private Button bt_login_guru;
    private View root;
    //private LoginData loginData;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference GLOBAL_VARIABLE;
    private String globalVariablePath = "gv";
    private String sharedPrefPasswordPath = "dpw";
    private DatabaseReference userRef;
    private DatabaseReference userListRef;
    private String username;
    private String email;
    private String password;
    private String modeLabel = "m";
    private String emailLabel = "e";
    private String mode = "g";
    private String userListPath = "ul";
    private String userPath = "u";
    private ProgressDialog progressDialog;
    private User user;
    private String DEFAULT_SHARED_PREF_PASSWORD;
    private FragmentLoginGuruBinding loginGuruBinding;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_login_guru, container, false);
        // if using view binding (enable @Override onDestroyView)
        //loginGuruBinding = FragmentLoginGuruBinding.inflate(inflater, container, false);
        //root = loginGuruBinding.getRoot();
        //loginGuruBinding.nip.setText("View Binding!");
        //loginGuruBinding.btLoginGuru.setOnClickListener(view -> {
            //
        //});

        ed_nip = root.findViewById(R.id.nip);
        ed_pw_guru = root.findViewById(R.id.password_guru);
        bt_login_guru = root.findViewById(R.id.bt_login_guru);
        progressDialog = new ProgressDialog(requireContext());

        ed_nip.setOnEditorActionListener((textView, actionId, keyEvent) -> {
            boolean handled = false;
            if (actionId == EditorInfo.IME_ACTION_NEXT) {
                ed_pw_guru.requestFocus();
                handled = true;
            }
            return handled;
        });

        ed_pw_guru.setOnEditorActionListener((textView, actionId, keyEvent) -> {
            boolean handled = false;
            if (actionId == EditorInfo.IME_ACTION_DONE) {
                bt_login_guru.performClick();
                handled = true;
            }
            return handled;
        });

        bt_login_guru.setOnClickListener(view -> {
            progressDialog.setMessage("Please Wait...");
            progressDialog.show();
            final String nip = ed_nip.getText().toString().trim();
            final String pw = ed_pw_guru.getText().toString().trim();
            if (isUserNameValid(nip) && isPasswordValid(pw)){
                userListRef.addValueEventListener(new ValueEventListener() {
                    @Override
                    public void onDataChange(@NonNull DataSnapshot snapshot) {
                        boolean userExist = false;
                        for(DataSnapshot aUser : snapshot.getChildren() ){
                            if(aUser.getKey().contentEquals(nip)){
                                if (aUser.child(modeLabel).getValue().toString().contentEquals(mode)){ //mode guru
                                    userExist = true;
                                    username = nip;
                                    email = aUser.child(emailLabel).getValue().toString(); //email
                                    password = pw;
                                }
                            }
                        }
                        if (userExist) {
                            user = new User(username, email, mode);
                            userLogin();
                        } else {
                            progressDialog.dismiss();
                            Toast.makeText(requireContext(), "User not found!", Toast.LENGTH_LONG).show();
                        }
                    }

                    @Override
                    public void onCancelled(@NonNull DatabaseError error) {

                    }
                });
            } else {
                    ed_nip.setError("Invalid! must > 5");
                    ed_pw_guru.setError("Invalid! must > 5");
                    Toast.makeText(requireContext(), "Login data error!", Toast.LENGTH_LONG).show();
            }
        });

        return root;
    }

    private void userLogin(){
        firebaseAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(requireActivity(), task -> {
//                        Log.i(TAG, "onComplete: " + firebaseAuth.getCurrentUser().getUid() + ":" +
//                                firebaseAuth.getUid());
//                        String gson = new Gson().toJson(user, User.class);
//                        userRef.child(firebaseAuth.getCurrentUser().getUid()).setValue(gson);
                    //if the task is successfull
                    if(task.isSuccessful()){
                        //LoginData.getInstance().Login(user);
                        DatabaseReference firebase = database.getReferenceFromUrl(StaticInfo.UsersURL);
                        final String emailPath = Tools.encodeString(email);
                        firebase.child(emailPath).addListenerForSingleValueEvent(new ValueEventListener() {
                            @Override
                            public void onDataChange(@NonNull DataSnapshot snapshot) {
                                SharedPreferences pref = requireActivity()
                                        .getApplicationContext()
                                        .getSharedPreferences("LocalUser", 0);
                                SharedPreferences.Editor editor = pref.edit();
                                //Log.d("SIGN-IN", "snapshot:" + snapshot.getValue().toString());
                                editor.putString("uid", firebaseAuth.getCurrentUser().getUid());
                                editor.putString("id", snapshot.child("id").getValue(String.class));
                                editor.putString("Email", snapshot.child("Email").getValue(String.class));
                                editor.putString("FirstName", snapshot.child("FirstName").getValue(String.class));
                                editor.putString("LastName", snapshot.child("LastName").getValue(String.class));
                                editor.apply();
                                Intent intent = new Intent(requireActivity(), MainGuruActivity.class);
                                startActivity(intent);
                                progressDialog.dismiss();
                                requireActivity().finish();
                            }

                            @Override public void onCancelled(@NonNull DatabaseError error) {
                                //Log.w("SIGN-IN", "signInWithEmail:cancelled", task.getException());
                                Toast.makeText(requireContext(), "Authentication cancelled.",
                                        Toast.LENGTH_SHORT).show();
                                progressDialog.dismiss();
                            }
                        });
                    } else {
                        Toast.makeText(requireContext(), "Login auth error!", Toast.LENGTH_LONG).show();
                        progressDialog.dismiss();
                    }
                });
    }

    // A placeholder username validation check
    private boolean isUserNameValid(String username) {
        return username != null && username.trim().length() >= 4;
    }

    // A placeholder password validation check
    private boolean isPasswordValid(String password) {
        return password != null && password.length() > 5;
    }

    @Override
    public void onStop() {
        super.onStop();
//        try {
//            getActivity().finish();
//        } catch (NullPointerException e) {
//            requireActivity().finish();
//        }
    }
}

//try {
//        loginData.prefRemove("param1");
//        loginData.prefRemove("param2");
//        loginData.prefRemove("param3");
//        loginData.prefCommit();
//        loginData.prefPutString("param1", AesGcmCryptor.encrypt(username, DEFAULT_SHARED_PREF_PASSWORD));//username
//        loginData.prefPutString("param2", AesGcmCryptor.encrypt(email, DEFAULT_SHARED_PREF_PASSWORD));//email
//        loginData.prefPutString("param3", AesGcmCryptor.encrypt(mode, DEFAULT_SHARED_PREF_PASSWORD));//mode
//        loginData.prefPutBoolean("firstRun", false);
//        loginData.prefCommit();
//
//        //Encryption encryption = Encryption.getDefault("Key", "Salt", new byte[16]);
//        //String encrypted = encryption.encryptOrNull("top secret string");
//        //String decrypted = encryption.decryptOrNull(encrypted);
//        } catch (Exception e) {
//        e.printStackTrace();
//        }
//        break;