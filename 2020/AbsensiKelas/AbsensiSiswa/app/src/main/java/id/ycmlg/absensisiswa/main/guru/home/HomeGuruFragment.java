package id.ycmlg.absensisiswa.main.guru.home;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.main.chat.ChatMainActivity;

public class HomeGuruFragment extends Fragment {

    //private HomeGuruViewModel homeViewModel;
    private View root = null;
    private LinearLayout kelas1a = null;
    private LinearLayout kelas1b = null;
    private LinearLayout kelas2a = null;
    private LinearLayout kelas2b = null;
    private LinearLayout kelas2c = null;
    private LinearLayout kelas3a = null;
    private LinearLayout kelas3b = null;
    private LinearLayout kelas4a = null;
    private LinearLayout kelas4b = null;
    private LinearLayout kelas5a = null;
    private LinearLayout kelas5b = null;
    private LinearLayout kelas6a = null;
    private LinearLayout kelas6b = null;
    private FloatingActionButton fabHome = null;
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        root = inflater.inflate(R.layout.fragment_home, container, false);
        root.setVisibility(View.VISIBLE);
        kelas1a = root.findViewById(R.id.kelas_1A);
        kelas1b = root.findViewById(R.id.kelas_1B);
        kelas2a = root.findViewById(R.id.kelas_2A);
        kelas2b = root.findViewById(R.id.kelas_2B);
        kelas2c = root.findViewById(R.id.kelas_2C);
        kelas3a = root.findViewById(R.id.kelas_3A);
        kelas3b = root.findViewById(R.id.kelas_3B);
        kelas4a = root.findViewById(R.id.kelas_4A);
        kelas4b = root.findViewById(R.id.kelas_4B);
        kelas5a = root.findViewById(R.id.kelas_5A);
        kelas5b = root.findViewById(R.id.kelas_5B);
        kelas6a = root.findViewById(R.id.kelas_6A);
        kelas6b = root.findViewById(R.id.kelas_6B);
        fabHome = root.findViewById(R.id.fabHome);

        final String tkr = getString(R.string.const_kelas_rendah);
        kelas1a.setOnClickListener(view -> kelasActivity(tkr, "Kelas 1A"));
        kelas1b.setOnClickListener(view -> kelasActivity(tkr, "Kelas 1B"));
        kelas2a.setOnClickListener(view -> kelasActivity(tkr, "Kelas 2A"));
        kelas2b.setOnClickListener(view -> kelasActivity(tkr, "Kelas 2B"));
        kelas2c.setOnClickListener(view -> kelasActivity(tkr, "Kelas 2C"));
        kelas3a.setOnClickListener(view -> kelasActivity(tkr, "Kelas 3A"));
        kelas3b.setOnClickListener(view -> kelasActivity(tkr, "Kelas 3B"));
        final String tkh = getString(R.string.const_kelas_tinggi);
        kelas4a.setOnClickListener(view -> kelasActivity(tkh, "Kelas 4A"));
        kelas4b.setOnClickListener(view -> kelasActivity(tkh, "Kelas 4B"));
        kelas5a.setOnClickListener(view -> kelasActivity(tkh, "Kelas 5A"));
        kelas5b.setOnClickListener(view -> kelasActivity(tkh, "Kelas 5B"));
        kelas6a.setOnClickListener(view -> kelasActivity(tkh, "Kelas 6A"));
        kelas6b.setOnClickListener(view -> kelasActivity(tkh, "Kelas 6B"));

        fabHome.setOnClickListener(v ->{
            Intent startChat = new Intent(requireContext(), ChatMainActivity.class);
            startActivity(startChat);
        });

        return root;
    }

    private void kelasActivity(String tipe, String kelas){
        Intent i = new Intent(requireActivity(), KelasActivity.class);
        i.putExtra(getString(R.string.var_tipe_kelas), tipe);
        i.putExtra(getString(R.string.var_nama_kelas), kelas);
        i.addFlags(Intent.FLAG_ACTIVITY_BROUGHT_TO_FRONT);
        startActivity(i);
    }
}