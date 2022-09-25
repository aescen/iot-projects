package id.ycmlg.absensisiswa.main.guru.home.menukelas;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.DaftarSiswaData;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link DaftarSiswaFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class DaftarSiswaFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String mParam2;

    public DaftarSiswaFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment DaftarSiswaFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static DaftarSiswaFragment newInstance(String param1, String param2) {
        DaftarSiswaFragment fragment = new DaftarSiswaFragment();
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
            namaKelas = getArguments().getString(ARG_PARAM1);
            mParam2 = getArguments().getString(ARG_PARAM2);
            database = FirebaseDatabase.getInstance();
            kelasRef = database.getReference("ds").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private TableLayout tl_daftar_siswa = null;
    private View root = null;
    private FirebaseDatabase database = null;
    private DatabaseReference kelasRef = null;
    private List<DaftarSiswaData> daftarSiswa = null;
    private LinearLayout pb_ll_daftar_siswa;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_daftar_siswa, container, false);
        tl_daftar_siswa = root.findViewById(R.id.tl_daftar_siswa);
        tl_daftar_siswa.setStretchAllColumns(true);
        pb_ll_daftar_siswa = root.findViewById(R.id.pb_ll_daftar_siswa);
        pb_ll_daftar_siswa.setVisibility(View.VISIBLE);

        if(kelasRef != null) {
            kelasRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    if (snapshot.getValue() != null) {
                        //Log.("DS", snapshot.toString());
                        int cnt = (int) snapshot.getChildrenCount();
                        int i = 0;
                        daftarSiswa = new ArrayList<>();
                        for (DataSnapshot child : snapshot.getChildren()) {
                            DaftarSiswaData row = new DaftarSiswaData();
                            row.no = (i + 1);
                            row.nis = Integer.parseInt(child.getKey());
                            row.nisn = Long.parseLong(child.child("nisn").getValue().toString());
                            row.nama = child.child("nama").getValue().toString();
                            row.lp = child.child("lp").getValue().toString();
                            daftarSiswa.add(row);
                            i++;
                        }
                        loadTableData();
                        pb_ll_daftar_siswa.setVisibility(View.GONE);
                    } else {
                        //Log.("DS", "No data for " + namaKelas);
                        pb_ll_daftar_siswa.setVisibility(View.GONE);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_daftar_siswa.setVisibility(View.GONE);
                }
            });
        }
        return root;
    }

    private void loadTableData(){
        Context context = requireContext();
        int rows = daftarSiswa.size();
        if (daftarSiswa != null && daftarSiswa.size() > 0){
            DaftarSiswaData row;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = daftarSiswa.get(i);
                final TextView tvNo = new TextView(context);
                tvNo.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNo.setBackgroundColor(Color.parseColor(textColor));
                tvNo.setGravity(Gravity.CENTER);
                tvNo.setPadding(5, 15, 0, 15);
                tvNo.setText(String.valueOf(row.no));

                final TextView tvNis = new TextView(context);
                tvNis.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNis.setGravity(Gravity.CENTER);
                tvNis.setPadding(5, 15, 0, 15);
                tvNis.setBackgroundColor(Color.parseColor(textColor));
                tvNis.setText(String.valueOf(row.nis));

                final TextView tvNisn = new TextView(context);
                tvNisn.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNisn.setGravity(Gravity.CENTER);
                tvNisn.setBackgroundColor(Color.parseColor(textColor));
                tvNisn.setPadding(5, 15, 0, 15);
                tvNisn.setText(String.valueOf(row.nisn));

                final TextView tvNama = new TextView(context);
                tvNama.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNama.setGravity(Gravity.CENTER);
                tvNama.setPadding(5, 15, 0, 15);
                tvNama.setBackgroundColor(Color.parseColor(textColor));
                tvNama.setText(String.valueOf(row.nama));

                final TextView tvLp = new TextView(context);
                tvLp.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvLp.setGravity(Gravity.CENTER);
                tvLp.setBackgroundColor(Color.parseColor(textColor));
                tvLp.setPadding(5, 15, 0, 15);
                tvLp.setText(String.valueOf(row.lp));

                final TableRow trSiswa = new TableRow(context);
                trSiswa.setId(i + 1);
                TableLayout.LayoutParams trParams = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParams.setMargins(0, 0, 0, 0);
                trSiswa.setPadding(0,0,0,0);
                trSiswa.setLayoutParams(trParams);
                trSiswa.addView(tvNo);
                trSiswa.addView(tvNis);
                trSiswa.addView(tvNisn);
                trSiswa.addView(tvNama);
                trSiswa.addView(tvLp);

                tl_daftar_siswa.addView(trSiswa, trParams);
                final TableRow trSep = new TableRow(context);
                TableLayout.LayoutParams trParamsSep = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParamsSep.setMargins(0, 0, 0, 0);
                trSep.setLayoutParams(trParamsSep);
                TextView tvSep = new TextView(requireContext());
                TableRow.LayoutParams tvSepLay = new TableRow.LayoutParams(TableRow
                        .LayoutParams.MATCH_PARENT, TableRow
                        .LayoutParams.WRAP_CONTENT);
                tvSepLay.span = 5;
                tvSep.setLayoutParams(tvSepLay);
                tvSep.setBackgroundColor(Color.parseColor("#d9d9d9"));
                tvSep.setHeight(1);
                trSep.addView(tvSep);
                tl_daftar_siswa.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa.setVisibility(View.VISIBLE);
        } else {
            //Log.("DS-table", "No data");
        }
    }
}