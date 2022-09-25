package id.ycmlg.absensisiswa.main.ortu.about;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.login.LoginActivity;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link AboutOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class AboutOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";
    private static final int ABOUT_ORTU_EDIT_REQ_CODE = 12321;

    // TODO: Rename and change types of parameters
    private String mParam1;
    private String mParam2;

    public AboutOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment AboutOrtuFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static AboutOrtuFragment newInstance(String param1, String param2) {
        AboutOrtuFragment fragment = new AboutOrtuFragment();
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
        if(firebaseAuth.getCurrentUser() == null){
            requireActivity().finish();
            Intent intent = new Intent(requireActivity(), LoginActivity.class);
            startActivity(intent);
        }
    }

    private View root = null;
    private TextView tv_nama_lengkap_ortu = null;
    private TextView tv_nama_anak_ortu = null;
    private TextView tv_kota_lahir_ortu = null;
    private TextView tv_tanggal_lahir_ortu = null;
    private TextView tv_agama_ortu = null;
    private TextView tv_jenis_kelamin_ortu = null;
    private TextView tv_nomor_telepon_ortu = null;
    private TextView tv_email_ortu = null;
    private ImageButton ib_bt_edit_about_ortu = null;
    private TextView tv_logout_about_ortu;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private String userPath = "u";
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_about_ortu, container, false);
        tv_nama_lengkap_ortu = root.findViewById(R.id.tv_nama_lengkap_ortu);
        tv_nama_anak_ortu = root.findViewById(R.id.tv_nama_anak_ortu);
        tv_kota_lahir_ortu = root.findViewById(R.id.tv_kota_lahir_ortu);
        tv_tanggal_lahir_ortu = root.findViewById(R.id.tv_tanggal_lahir_ortu);
        tv_agama_ortu = root.findViewById(R.id.tv_agama_ortu);
        tv_jenis_kelamin_ortu = root.findViewById(R.id.tv_jenis_kelamin_ortu);
        tv_nomor_telepon_ortu = root.findViewById(R.id.tv_nomor_telepon_ortu);
        tv_email_ortu = root.findViewById(R.id.tv_email_ortu);
        ib_bt_edit_about_ortu = root.findViewById(R.id.bt_edit_about_ortu);
        tv_logout_about_ortu = root.findViewById(R.id.tv_logout_about_ortu);

        DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
        uuid.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot snapshot) {
                final String nl = snapshot.child("nl").getValue().toString() == null ?
                        "No data." : snapshot.child("nl").getValue().toString();
                final String na = snapshot.child("na").getValue().toString() == null ?
                        "No data." : snapshot.child("na").getValue().toString();
                final String kl = snapshot.child("kl").getValue().toString() == null ?
                        "No data." : snapshot.child("kl").getValue().toString();
                final String tl = snapshot.child("tl").getValue().toString() == null ?
                        "No data." : snapshot.child("tl").getValue().toString();
                final String a = snapshot.child("a").getValue().toString() == null ?
                        "No data." : snapshot.child("a").getValue().toString();
                final String jk = snapshot.child("jk").getValue().toString() == null ?
                        "No data." : snapshot.child("jk").getValue().toString();
                final String nt = snapshot.child("nt").getValue().toString() == null ?
                        "No data." : snapshot.child("nt").getValue().toString();
                final String e = snapshot.child("e").getValue().toString() == null ?
                        "No data." : snapshot.child("e").getValue().toString();
                final String un = snapshot.child("un").getValue().toString();
                tv_nama_lengkap_ortu.setText(nl);//nama lengkap
                tv_nama_anak_ortu.setText(na);//nama anak
                tv_kota_lahir_ortu.setText(kl);//kota lahir
                tv_tanggal_lahir_ortu.setText(tl);//tanggal lahir
                tv_agama_ortu.setText(a);//agama
                tv_jenis_kelamin_ortu.setText(jk);//jenis kelamin
                tv_nomor_telepon_ortu.setText(nt);//nomor telepon
                tv_email_ortu.setText(e);//email


                if(un != null){
                    ib_bt_edit_about_ortu.setOnClickListener(view -> {
                        Fragment fragment = AboutOrtuEditFragment.newInstance(un, e);
                        requireActivity().getSupportFragmentManager().
                                beginTransaction()
                                .replace(R.id.nav_main_ortu_host_fragment, fragment)
                                .addToBackStack(null)
                                .commit();
                    });
                } else {
                    Toast.makeText(requireContext(), "Username data is null!", Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onCancelled(@NonNull DatabaseError error) {}
        });

        tv_logout_about_ortu.setOnClickListener(view -> {
            firebaseAuth.signOut();
            //LoginData.getInstance().Logout();
            Intent intent = new Intent(requireContext(), LoginActivity.class);
            startActivity(intent);
            requireActivity().finish();
        });

        return root;
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if(requestCode == ABOUT_ORTU_EDIT_REQ_CODE) {
            if(resultCode == resultCode){

            }
        }
    }
}