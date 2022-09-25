package id.ycmlg.absensisiswa.main.ortu;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;
import android.widget.TextView;

import androidx.fragment.app.Fragment;

import com.bumptech.glide.Glide;
import com.google.firebase.storage.FirebaseStorage;
import com.google.firebase.storage.StorageReference;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.databinding.FragmentJadwalPelajaranOrtuBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link JadwalPelajaranOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class JadwalPelajaranOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String mParam2;

    public JadwalPelajaranOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment JadwalPelajaranOrtuFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static JadwalPelajaranOrtuFragment newInstance(String namaKelas, String param2) {
        JadwalPelajaranOrtuFragment fragment = new JadwalPelajaranOrtuFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, namaKelas);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
            storage = FirebaseStorage.getInstance();
            storageRef = storage.getReference();
            jpRef = storageRef.child("jp");
            kelasRef = jpRef.child(namaKelas);
        }
    }

    private FirebaseStorage storage;
    private StorageReference storageRef;
    private StorageReference jpRef;
    private StorageReference kelasRef;
    private View root;
    private FragmentJadwalPelajaranOrtuBinding jpOrtuBinded;
    private ImageView iv_jadwal_pelajaran_ortu;
    private TextView tv_jadwal_pelajaran_ortu;
    private ProgressBar spinner;
    private RelativeLayout rl_gambar_jadwal_pelajaran_ortu;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        jpOrtuBinded = FragmentJadwalPelajaranOrtuBinding.inflate(inflater, container, false);
        root = jpOrtuBinded.getRoot();
        iv_jadwal_pelajaran_ortu = jpOrtuBinded.ivJadwalPelajaranOrtu;
        tv_jadwal_pelajaran_ortu = jpOrtuBinded.tvJadwalPelajaranOrtu;
        rl_gambar_jadwal_pelajaran_ortu = jpOrtuBinded.rlGambarJadwalPelajaranOrtu;
        spinner = jpOrtuBinded.pbJadwalPelajaranOrtu;
        spinner.getIndeterminateDrawable().setColorFilter(requireContext()
                .getResources()
                .getColor(R.color.colorPrimaryLight), android.graphics.PorterDuff.Mode.MULTIPLY);

        tv_jadwal_pelajaran_ortu.setVisibility(View.GONE);
        spinner.setVisibility(View.VISIBLE);

        if (namaKelas != null) {
            kelasRef.child("jp_" + namaKelas + ".png")
                    .getDownloadUrl()
                    .addOnSuccessListener(uri -> {
                        Glide.with(requireContext())
                                .load(uri)
                                .fitCenter()
                                .dontAnimate()
                                .into(iv_jadwal_pelajaran_ortu);
                        spinner.setVisibility(View.GONE);
                        rl_gambar_jadwal_pelajaran_ortu.setBackgroundColor(requireContext()
                                .getResources()
                                .getColor(R.color.transparent));
                        iv_jadwal_pelajaran_ortu.setVisibility(View.VISIBLE);
                    });
        }

        return root;
    }
}