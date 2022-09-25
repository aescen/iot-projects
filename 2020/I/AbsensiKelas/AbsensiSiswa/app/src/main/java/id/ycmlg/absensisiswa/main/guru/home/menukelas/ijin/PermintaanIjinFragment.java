package id.ycmlg.absensisiswa.main.guru.home.menukelas.ijin;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.widget.EditText;
import android.widget.ImageButton;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import id.ycmlg.absensisiswa.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link PermintaanIjinFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class PermintaanIjinFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "nis";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;


    public PermintaanIjinFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param nis Parameter 2.
     * @return A new instance of fragment PermintaanIjinFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static PermintaanIjinFragment newInstance(String namaKelas, String nis) {
        PermintaanIjinFragment fragment = new PermintaanIjinFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, nis);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            nis = getArguments().getString(ARG_PARAM2);
            database = FirebaseDatabase.getInstance();
            dsRef = database.getReference("ds").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
            absRef = database.getReference("abs").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private View root = null;
    private FirebaseDatabase database = null;
    private DatabaseReference dsRef = null;
    private DatabaseReference absRef = null;
    private ImageButton ib_search_button_minta_ijin = null;
    private EditText ed_minta_ijin = null;
    private String namaLengkap;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_permintaan_ijin, container, false);
        ib_search_button_minta_ijin = root.findViewById(R.id.ib_search_button_minta_ijin);
        ed_minta_ijin = root.findViewById(R.id.ed_minta_ijin);

        ed_minta_ijin.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {}
            @Override public void onTextChanged(CharSequence charSequence, int i, int i1, int i2) {}
            @Override
            public void afterTextChanged(Editable editable) {
                nis = ed_minta_ijin.getText().toString().trim();
                if(nis.length() > 3 && TextUtils.isDigitsOnly(nis)){
                    dsRef.addListenerForSingleValueEvent(new ValueEventListener() {
                        @Override
                        public void onDataChange(@NonNull DataSnapshot snapshot) {
                            boolean userFound = false;
                            for (DataSnapshot userChild: snapshot.getChildren()) {
                                if(nis.contentEquals(userChild.getKey())){
                                    userFound = true;
                                    namaLengkap = userChild.child("nama").getValue().toString();
                                }
                            }
                            if(userFound){
                                ed_minta_ijin.setOnEditorActionListener((v, actionId, event) -> {
                                    boolean handled = false;
                                    if (actionId == EditorInfo.IME_ACTION_DONE) {
                                        Fragment fragment = IjinFragment.newInstance(namaKelas, nis, namaLengkap);
                                        requireActivity().getSupportFragmentManager().
                                                beginTransaction()
                                                .replace(R.id.nav_kelas_host_fragment, fragment)
                                                .addToBackStack(null)
                                                .commit();
                                        ed_minta_ijin.setText("");
                                        handled = true;
                                    }
                                    return handled;
                                });
                            } else{
                                ed_minta_ijin.setError("NIS tidak ada!");
                            }
                        }

                        @Override
                        public void onCancelled(@NonNull DatabaseError error) {

                        }
                    });
                } else if(nis.trim().length() > 0 && nis.trim().length() <= 3) {
                    ed_minta_ijin.setError("NIS tidak ada!");
                }
            }
        });

        return root;
    }
}