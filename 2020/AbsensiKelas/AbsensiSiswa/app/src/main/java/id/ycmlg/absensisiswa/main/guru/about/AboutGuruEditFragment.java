package id.ycmlg.absensisiswa.main.guru.about;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.AppCompatSpinner;
import androidx.fragment.app.Fragment;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;

import java.util.Objects;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.databinding.FragmentAboutGuruEditBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link AboutGuruEditFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class AboutGuruEditFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "nis";
    private static final String ARG_PARAM2 = "email";

    // TODO: Rename and change types of parameters
    private String nis;
    private String email;

    public AboutGuruEditFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param nis Parameter 1.
     * @param email Parameter 2.
     * @return A new instance of fragment AboutGuruEditFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static AboutGuruEditFragment newInstance(String nis, String email) {
        AboutGuruEditFragment fragment = new AboutGuruEditFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, nis);
        args.putString(ARG_PARAM2, email);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            nis = getArguments().getString(ARG_PARAM1);
            email = getArguments().getString(ARG_PARAM2);
            firebaseAuth = FirebaseAuth.getInstance();
            database = FirebaseDatabase.getInstance();
            userRef = database.getReference(userPath);
        }
    }

    private FragmentAboutGuruEditBinding editGuruBind;
    private View root;
    private EditText ed_nama_lengkap_about_edit_guru;
    private EditText ed_kota_lahir_about_edit_guru;
    private EditText ed_tanggal_lahir_about_edit_guru;
    private AppCompatSpinner spinner_agama_edit_guru_about_edit_guru;
    private RadioGroup rg_jenis_kelamin_about_edit_guru;
    private EditText ed_nomor_telepon_about_edit_guru;
    private ImageButton bt_about_save_guru_about_edit_guru;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private String userPath = "u", agama, jeniskelamin, kotalahir, namalengkap, nomortelepon, tanggallahir;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        editGuruBind = FragmentAboutGuruEditBinding.inflate(inflater, container, false);
        root = editGuruBind.getRoot();
        bt_about_save_guru_about_edit_guru = editGuruBind.btAboutSaveAboutEditGuru;
        ed_kota_lahir_about_edit_guru = editGuruBind.edKotaLahirAboutEditGuru;
        ed_nama_lengkap_about_edit_guru = editGuruBind.edNamaLengkapAboutEditGuru;
        ed_nomor_telepon_about_edit_guru = editGuruBind.edNomorTeleponAboutEditGuru;
        ed_tanggal_lahir_about_edit_guru = editGuruBind.edTanggalLahirAboutEditGuru;
        rg_jenis_kelamin_about_edit_guru = editGuruBind.rgJenisKelaminAboutEditGuru;
        spinner_agama_edit_guru_about_edit_guru = editGuruBind.spinnerAgamaAboutEditGuru;

        bt_about_save_guru_about_edit_guru.setOnClickListener(view -> {
            boolean formOk = false;
            if(ed_kota_lahir_about_edit_guru.getText().toString().length() > 0) {
                kotalahir = ed_kota_lahir_about_edit_guru.getText().toString();
                formOk = true;
            } else {
                formOk = false;
                ed_kota_lahir_about_edit_guru.setError("Kosong!");
            }
            if(ed_nama_lengkap_about_edit_guru.getText().toString().length() > 0 && formOk == true) {
                namalengkap = ed_nama_lengkap_about_edit_guru.getText().toString();
                formOk = true;
            } else {
                formOk = false;
                ed_nama_lengkap_about_edit_guru.setError("Kosong!");
            }
            if(ed_nomor_telepon_about_edit_guru.getText().toString().length() > 0 && formOk == true) {
                nomortelepon = ed_nomor_telepon_about_edit_guru.getText().toString();
                formOk = true;
            } else {
                formOk = false;
                ed_nomor_telepon_about_edit_guru.setError("Kosong!");
            }
            if(ed_tanggal_lahir_about_edit_guru.getText().toString().length() > 0 && formOk == true) {
                tanggallahir = ed_tanggal_lahir_about_edit_guru.getText().toString();
                formOk = true;
            } else {
                formOk = false;
                ed_tanggal_lahir_about_edit_guru.setError("Kosong!");
            }

            if(rg_jenis_kelamin_about_edit_guru.getCheckedRadioButtonId() == -1){
                formOk = false;
            } else {
                RadioButton jk = root.findViewById(rg_jenis_kelamin_about_edit_guru.getCheckedRadioButtonId());
                jeniskelamin = jk.getText().toString();
                formOk = true;
            }
            if(spinner_agama_edit_guru_about_edit_guru.getSelectedItem() != null ) {
                agama = spinner_agama_edit_guru_about_edit_guru.getSelectedItem().toString();
                formOk = true;
            } else  {
                formOk = false;
            }

            if(formOk){
                DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
                uuid.child("a").setValue(Objects.requireNonNull(agama));
                uuid.child("jk").setValue(Objects.requireNonNull(jeniskelamin));
                uuid.child("kl").setValue(Objects.requireNonNull(kotalahir));
                uuid.child("nl").setValue(Objects.requireNonNull(namalengkap));
                uuid.child("nt").setValue(Objects.requireNonNull(nomortelepon));
                uuid.child("tl").setValue(Objects.requireNonNull(tanggallahir));
                Fragment fragment = new AboutGuruFragment();
                requireActivity().getSupportFragmentManager()
                        .beginTransaction()
                        .replace(R.id.fragment_container_guru, fragment)
                        .commit();
                ((AppCompatActivity)requireActivity()).getSupportActionBar().setTitle("About");
            } else {
                Toast.makeText(requireContext(), "Form tidak lengkap!", Toast.LENGTH_LONG).show();
            }

        });

        return root;
    }
}