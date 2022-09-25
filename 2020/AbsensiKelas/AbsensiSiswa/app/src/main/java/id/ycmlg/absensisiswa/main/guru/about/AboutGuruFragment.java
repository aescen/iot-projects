package id.ycmlg.absensisiswa.main.guru.about;

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

public class AboutGuruFragment extends Fragment {

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        firebaseAuth = FirebaseAuth.getInstance();
        database = FirebaseDatabase.getInstance();
        userRef = database.getReference(userPath);
        if(firebaseAuth.getCurrentUser() == null){
            requireActivity().finish();
            Intent intent = new Intent(requireActivity(), LoginActivity.class);
            startActivity(intent);
        }
    }

    private static final int ABOUT_GURU_EDIT_REQ_CODE = 10101;
    private View root = null;
    private ImageButton bt_about_edit_guru = null;
    private TextView tv_nama_lengkap = null;
    private TextView tv_kota_lahir = null;
    private TextView tv_tanggal_lahir = null;
    private TextView tv_agama = null;
    private TextView tv_jenis_kelamin = null;
    private TextView tv_nomor_telepon = null;
    private TextView tv_email = null;
    private TextView tv_logout_about_guru;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private String userPath = "u";
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        root = inflater.inflate(R.layout.fragment_about_guru, container, false);
        tv_nama_lengkap = root.findViewById(R.id.tv_nama_lengkap);
        tv_kota_lahir = root.findViewById(R.id.tv_kota_lahir);
        tv_tanggal_lahir = root.findViewById(R.id.tv_tanggal_lahir);
        tv_agama = root.findViewById(R.id.tv_agama);
        tv_jenis_kelamin = root.findViewById(R.id.tv_jenis_kelamin);
        tv_nomor_telepon = root.findViewById(R.id.tv_nomor_telepon);
        tv_email = root.findViewById(R.id.tv_email);
        bt_about_edit_guru = root.findViewById(R.id.bt_edit_about_guru);
        tv_logout_about_guru = root.findViewById(R.id.tv_logout_about_guru);

        DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
        uuid.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot snapshot) {
                final String nl = snapshot.child("nl").getValue().toString() == null ?
                        "No data." : snapshot.child("nl").getValue().toString();
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
                tv_nama_lengkap.setText(nl);//nama lengkap
                tv_kota_lahir.setText(kl);//kota lahir
                tv_tanggal_lahir.setText(tl);//tanggal lahir
                tv_agama.setText(a);//agama
                tv_jenis_kelamin.setText(jk);//jenis kelamin
                tv_nomor_telepon.setText(nt);//nomor telepon
                tv_email.setText(e);//email

                if(un != null){
                    bt_about_edit_guru.setOnClickListener(view -> {
                        Fragment fragment = AboutGuruEditFragment.newInstance(un, e);
                        requireActivity().getSupportFragmentManager().
                                beginTransaction()
                                .replace(R.id.fragment_container_guru, fragment)
                                .addToBackStack(null)
                                .commit();
                    });
                } else {
                    Toast.makeText(requireContext(), "Username data is null!", Toast.LENGTH_SHORT).show();
                }
            }
            @Override public void onCancelled(@NonNull DatabaseError error) {}
        });

        tv_logout_about_guru.setOnClickListener(view -> {
            firebaseAuth.signOut();
            //LoginData.getInstance().Logout();
            Intent intent = new Intent(requireContext(), LoginActivity.class);
            startActivity(intent);
            requireActivity().finish();
        });

        return root;
    }
}