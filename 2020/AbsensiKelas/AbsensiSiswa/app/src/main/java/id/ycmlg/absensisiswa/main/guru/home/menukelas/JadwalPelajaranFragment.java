package id.ycmlg.absensisiswa.main.guru.home.menukelas;

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

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link JadwalPelajaranFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class JadwalPelajaranFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";

    // TODO: Rename and change types of parameters
    private String namaKelas;

    public JadwalPelajaranFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @return A new instance of fragment JadwalPelajaranFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static JadwalPelajaranFragment newInstance(String param1) {
        JadwalPelajaranFragment fragment = new JadwalPelajaranFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            namaKelas = getArguments().getString(ARG_PARAM1);
            //Log.i("param", "namakelas: " + namaKelas);

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
    private ImageView iv_jadwal_pelajaran;
    private TextView tv_jadwal_pelajaran;
    private ProgressBar spinner;
    private RelativeLayout rl_gambar_jadwal_pelajaran;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_jadwal_pelajaran, container, false);
        iv_jadwal_pelajaran = root.findViewById(R.id.iv_jadwal_pelajaran);
        tv_jadwal_pelajaran = root.findViewById(R.id.tv_jadwal_pelajaran);
        rl_gambar_jadwal_pelajaran = root.findViewById(R.id.rl_gambar_jadwal_pelajaran);
        spinner = root.findViewById(R.id.pb_jadwal_pelajaran);
        spinner.getIndeterminateDrawable().setColorFilter(requireContext()
                .getResources()
                .getColor(R.color.colorPrimaryLight), android.graphics.PorterDuff.Mode.MULTIPLY);

        tv_jadwal_pelajaran.setVisibility(View.GONE);
        spinner.setVisibility(View.VISIBLE);

        if (namaKelas != null) {
            kelasRef.child("jp_" + namaKelas + ".png")
                    .getDownloadUrl()
                    .addOnSuccessListener(uri -> {
                        Glide.with(requireContext())
                                .load(uri)
                                .fitCenter()
                                .dontAnimate()
                                .into(iv_jadwal_pelajaran);
                        spinner.setVisibility(View.GONE);
                        rl_gambar_jadwal_pelajaran.setBackgroundColor(requireContext()
                                .getResources()
                                .getColor(R.color.transparent));
                        iv_jadwal_pelajaran.setVisibility(View.VISIBLE);
                    });
        }
        return root;
    }
}