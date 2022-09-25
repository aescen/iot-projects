package id.ycmlg.absensisiswa.main.ortu.raport;

import android.content.Context;
import android.graphics.Color;
import android.graphics.Paint;
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
import id.ycmlg.absensisiswa.data.Raport;
import id.ycmlg.absensisiswa.databinding.FragmentRaportOrtuBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link RaportOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class RaportOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "nis";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;

    public RaportOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param nis Parameter 2.
     * @return A new instance of fragment RaportFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static RaportOrtuFragment newInstance(String namaKelas, String nis) {
        RaportOrtuFragment fragment = new RaportOrtuFragment();
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
            raporRef = database.getReference("laporanrapor").child(namaKelas.toLowerCase().replaceAll("\\s+",""));;
        }
    }

    private View root;
    private FragmentRaportOrtuBinding raporOrtuBinded;
    private TableLayout tl_daftar_raport_ortu;
    private LinearLayout pb_ll_raport_ortu;
    private FirebaseDatabase database;
    private DatabaseReference raporRef;
    private List<Raport> daftarRapor;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        raporOrtuBinded = FragmentRaportOrtuBinding.inflate(inflater, container, false);
        root = raporOrtuBinded.getRoot();
        tl_daftar_raport_ortu = raporOrtuBinded.tlDaftarRaportOrtu;
        pb_ll_raport_ortu = root.findViewById(R.id.pb_ll_raport_ortu);
        pb_ll_raport_ortu.setVisibility(View.VISIBLE);

        if(raporRef != null) {
            raporRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    if (snapshot.getValue() != null) {
                        daftarRapor = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childArr: snapshot.getChildren()) {
                            Raport row = new Raport();
                            row.no = (i + 1);
                            row.tgl = childArr.child("tgl").getValue().toString();
                            row.wkt = childArr.child("wkt").getValue().toString();
                            row.nf = childArr.child("nf").getValue().toString();
                            row.nis = childArr.child("nis").getValue().toString();
                            if(row.nis.contentEquals(nis)){
                                daftarRapor.add(row);
                                i++;
                            }
                        }
                        loadTableData();
                        pb_ll_raport_ortu.setVisibility(View.GONE);
                    } else {
                        //Log.i("ABS-DATA", "No data for " + namaKelas);
                        pb_ll_raport_ortu.setVisibility(View.GONE);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_raport_ortu.setVisibility(View.GONE);
                }
            });
        }

        return root;
    }

    private void loadTableData(){
        Context context = requireContext();
        int rows = daftarRapor.size();
        if (daftarRapor != null && daftarRapor.size() > 0){
            Raport row;
            final int COLUMN_COUNT = 4;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = daftarRapor.get(i);
                final TextView tvNo = new TextView(context);
                tvNo.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNo.setBackgroundColor(Color.parseColor(textColor));
                tvNo.setGravity(Gravity.CENTER);
                tvNo.setPadding(5, 15, 0, 15);
                tvNo.setText(String.valueOf(row.no));

                final TextView tvTgl = new TextView(context);
                tvTgl.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTgl.setGravity(Gravity.CENTER);
                tvTgl.setPadding(5, 15, 0, 15);
                tvTgl.setBackgroundColor(Color.parseColor(textColor));
                tvTgl.setText(String.valueOf(row.tgl));

                final TextView tvWkt = new TextView(context);
                tvWkt.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvWkt.setGravity(Gravity.CENTER);
                tvWkt.setBackgroundColor(Color.parseColor(textColor));
                tvWkt.setPadding(5, 15, 0, 15);
                tvWkt.setText(String.valueOf(row.wkt));

                final TextView tvVF = new TextView(context);
                tvVF.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvVF.setGravity(Gravity.CENTER);
                tvVF.setPadding(5, 15, 0, 15);
                tvVF.setBackgroundColor(Color.parseColor(textColor));
                tvVF.setText("View");
                tvVF.setTextColor(Color.parseColor("#2979FF"));
                tvVF.setPaintFlags(tvVF.getPaintFlags() | Paint.UNDERLINE_TEXT_FLAG);
                final String path = row.nf;
                tvVF.setOnClickListener(view -> {
                    //Toast.makeText(requireContext(), path, Toast.LENGTH_SHORT).show();
                    Fragment fragment = RaporPDFViewFragment.newInstance(namaKelas, path);
                    requireActivity().getSupportFragmentManager().
                            beginTransaction()
                            .replace(R.id.nav_main_ortu_host_fragment, fragment)
                            .addToBackStack(null)
                            .commit();
                });

                final TableRow trAbsen = new TableRow(context);
                trAbsen.setId(i + 1);
                TableLayout.LayoutParams trParams = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParams.setMargins(0, 0, 0, 0);
                trAbsen.setPadding(0,0,0,0);
                trAbsen.setLayoutParams(trParams);
                trAbsen.addView(tvNo);
                trAbsen.addView(tvTgl);
                trAbsen.addView(tvWkt);
                trAbsen.addView(tvVF);

                tl_daftar_raport_ortu.addView(trAbsen, trParams);
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
                tvSepLay.span = COLUMN_COUNT;
                tvSep.setLayoutParams(tvSepLay);
                tvSep.setBackgroundColor(Color.parseColor("#d9d9d9"));
                tvSep.setHeight(1);
                trSep.addView(tvSep);
                tl_daftar_raport_ortu.addView(trSep, trParamsSep);
            }
            tl_daftar_raport_ortu.setVisibility(View.VISIBLE);
        } else {
            //Log.i("ABS-table", "No data");
        }
    }
}