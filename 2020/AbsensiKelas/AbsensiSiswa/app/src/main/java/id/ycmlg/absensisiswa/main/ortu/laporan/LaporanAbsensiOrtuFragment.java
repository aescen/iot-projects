package id.ycmlg.absensisiswa.main.ortu.laporan;

import android.app.DatePickerDialog;
import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageButton;
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
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.lang.reflect.Field;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.DaftarAbsensiSiswaData;
import id.ycmlg.absensisiswa.data.Filter;
import id.ycmlg.absensisiswa.databinding.FragmentLaporanAbsensiOrtuBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LaporanAbsensiOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LaporanAbsensiOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "nis";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;

    public LaporanAbsensiOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param nis Parameter 2.
     * @return A new instance of fragment LaporanAbsensiFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static LaporanAbsensiOrtuFragment newInstance(String namaKelas, String nis) {
        LaporanAbsensiOrtuFragment fragment = new LaporanAbsensiOrtuFragment();
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
            kelasRef = database.getReference("abs").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private TableLayout tl_daftar_siswa_laporan_absensi_ortu;
    private View root;
    private FirebaseDatabase database;
    private DatabaseReference kelasRef;
    private List<DaftarAbsensiSiswaData> dabsSiswaOrtu;
    private DatePickerDialog datePickerDialog;
    private LinearLayout pb_ll_laporan_absensi_ortu;
    private EditText ed_laporan_absensi_ortu;
    private EditText ed_laporan_absensi_tanggal_dari_ortu;
    private EditText ed_laporan_absensi_tanggal_ke_ortu;
    private ImageButton ib_laporan_start_date_absensi_ortu;
    private ImageButton ib_laporan_end_date_absensi_ortu;
    private ImageButton ib_search_laporan_absensi;
    private CheckBox cb_sakit;
    private CheckBox cb_ijin;
    private CheckBox cb_tanpa_ket;
    private final String strsakit = "Sakit";
    private final String strijin = "Ijin";
    private final String strmasuk = "Masuk";
    private final String stralpha = "Tanpa Ket.";
    private int dayD;
    private int monthD;
    private int yearD;
    private Long epochDari;
    private Long epochKe;
    private FragmentLaporanAbsensiOrtuBinding absOrtuBinded;
    private List<Filter> toFilter= new ArrayList<>();

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        absOrtuBinded = FragmentLaporanAbsensiOrtuBinding.inflate(inflater, container,false);
        root = absOrtuBinded.getRoot();
        cb_ijin = absOrtuBinded.cbIjin;
        cb_sakit = absOrtuBinded.cbSakit;
        cb_tanpa_ket = absOrtuBinded.cbTanpaKet;
        tl_daftar_siswa_laporan_absensi_ortu = absOrtuBinded.tlDaftarSiswaLaporanAbsensiOrtu;
        ed_laporan_absensi_tanggal_dari_ortu = absOrtuBinded.edLaporanAbsensiTanggalDariOrtu;
        ed_laporan_absensi_tanggal_ke_ortu = absOrtuBinded.edLaporanAbsensiTanggalKeOrtu;
        ib_laporan_start_date_absensi_ortu = absOrtuBinded.ibLaporanStartDateAbsensiOrtu;
        ib_laporan_end_date_absensi_ortu = absOrtuBinded.ibLaporanEndDateAbsensiOrtu;
        ib_search_laporan_absensi = absOrtuBinded.ibSearchLaporanAbsensi;
        pb_ll_laporan_absensi_ortu = root.findViewById(R.id.pb_ll_laporan_absensi_ortu);
        pb_ll_laporan_absensi_ortu.setVisibility(View.VISIBLE);

        cb_ijin.setOnCheckedChangeListener((buttonView, isChecked) -> {
            boolean filterPresent = false;
            for (Filter aFilter:toFilter) {
                if(aFilter.filterSet.contentEquals(strijin)){
                    filterPresent = true;
                }
            }
            if(isChecked && !filterPresent){
                Filter aFilter = new Filter();
                aFilter.filterSet = strijin;
                aFilter.toFilter = "ket";
                toFilter.add(aFilter);
            }else if(!isChecked){
                for (int i = 0; i < toFilter.size(); i++) {
                    if(toFilter.get(i).filterSet.contentEquals(strijin)){
                        toFilter.remove(i);
                    }
                }
            }

            loadFilteredData();
        });

        cb_sakit.setOnCheckedChangeListener((buttonView, isChecked) -> {
            boolean filterPresent = false;
            for (Filter aFilter:toFilter) {
                if(aFilter.filterSet.contentEquals(strsakit)){
                    filterPresent = true;
                }
            }
            if(isChecked && !filterPresent){
                Filter aFilter = new Filter();
                aFilter.filterSet = strsakit;
                aFilter.toFilter = "ket";
                toFilter.add(aFilter);
            }else if(!isChecked){
                for (int i = 0; i < toFilter.size(); i++) {
                    if(toFilter.get(i).filterSet.contentEquals(strsakit)){
                        toFilter.remove(i);
                    }
                }
            }

            loadFilteredData();
        });

        cb_tanpa_ket.setOnCheckedChangeListener((buttonView, isChecked) -> {
            boolean filterPresent = false;
            for (Filter aFilter:toFilter) {
                if(aFilter.filterSet.contentEquals(stralpha)){
                    filterPresent = true;
                }
            }
            if(isChecked && !filterPresent){
                Filter aFilter = new Filter();
                aFilter.filterSet = stralpha;
                aFilter.toFilter = "ket";
                toFilter.add(aFilter);
            }else if(!isChecked){
                for (int i = 0; i < toFilter.size(); i++) {
                    if(toFilter.get(i).filterSet.contentEquals(stralpha)){
                        toFilter.remove(i);
                    }
                }
            }

            loadFilteredData();
        });

        ib_laporan_start_date_absensi_ortu.setOnClickListener(view -> {
            final Calendar c = Calendar.getInstance();
            int mYear = c.get(Calendar.YEAR); // current year
            int mMonth = c.get(Calendar.MONTH); // current month
            int mDay = c.get(Calendar.DAY_OF_MONTH); // current day
            // date picker dialog
            datePickerDialog = new DatePickerDialog(requireContext(),
                    (view1, year, monthOfYear, dayOfMonth) -> {
                        // set day of month , month and year value in the edit text
                        dayD = dayOfMonth;
                        monthD = monthOfYear;
                        yearD = monthOfYear;
                        ed_laporan_absensi_tanggal_dari_ortu.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_laporan_end_date_absensi_ortu.setOnClickListener(view -> {
            final Calendar c = Calendar.getInstance();
            int mYear = c.get(Calendar.YEAR); // current year
            int mMonth = c.get(Calendar.MONTH); // current month
            int mDay = c.get(Calendar.DAY_OF_MONTH); // current day
            // date picker dialog
            datePickerDialog = new DatePickerDialog(requireContext(),
                    (view1, year, monthOfYear, dayOfMonth) -> {
                        // set day of month , month and year value in the edit text
                        dayD = dayOfMonth;
                        monthD = monthOfYear;
                        yearD = monthOfYear;
                        ed_laporan_absensi_tanggal_ke_ortu.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_search_laporan_absensi.setOnClickListener(view -> {
            //final String nisEd = ed_laporan_nilai_akademik.getText().toString().trim();
            final String tglDari = ed_laporan_absensi_tanggal_dari_ortu.getText().toString().trim();
            final String tglKe = ed_laporan_absensi_tanggal_ke_ortu.getText().toString().trim();
            if(tglDari.length() > 0 && tglKe.length() > 0){
                try {
                    epochDari = new SimpleDateFormat("dd-MM-yyyy")
                            .parse(tglDari)
                            .getTime();
                    epochKe = new SimpleDateFormat("dd-MM-yyyy")
                            .parse(tglKe)
                            .getTime();
                    loadFilteredData();
                } catch (ParseException e) {
                    e.printStackTrace();
                }
            }
        });

        /*if(kelasRef != null) {
            kelasRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    if (snapshot.getValue() != null) {
                        //Log.i("ABS-DATA", snapshot.toString());
                        dabsSiswaOrtu = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childTgl : snapshot.getChildren()) {
                            for (DataSnapshot arrChild : childTgl.getChildren()){
                                DaftarAbsensiSiswaData row = new DaftarAbsensiSiswaData();
                                row.no = (i + 1);
                                row.ket = checkKet(arrChild.child("ket").getValue().toString());
                                row.nis = arrChild.child("nis").getValue().toString();
                                row.nm = arrChild.child("nm").getValue().toString();
                                row.tgl = arrChild.child("tgl").getValue().toString();
                                row.wkt = arrChild.child("wkt").getValue().toString();
                                if(row.nis.contentEquals(nis)){
                                    dabsSiswaOrtu.add(row);
                                    i++;
                                }
                            }
                        }
                        loadTableData(false);
                        pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                    } else {
                        //Log.i("ABS-DATA", "No data for " + namaKelas);
                        pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                    }
                }

                private String checkKet(String ket) {
                    if (ket != null){
                        if(ket.contentEquals("s")) return "Sakit";
                        else if(ket.contentEquals("i")) return "Ijin";
                        else if(ket.contentEquals("m")) return "Masuk";
                        else return "Tanpa Ket.";
                    } else return "n/a";
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                }
            });
        }*/

        loadFilteredData();

        return root;
    }

    private void loadFilteredData(){
        if(kelasRef != null) {
            pb_ll_laporan_absensi_ortu.setVisibility(View.VISIBLE);
            kelasRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    boolean isFilter = false;
                    if (snapshot.getValue() != null) {
                        //Log.i("ABS-DATA", snapshot.toString());
                        List<DaftarAbsensiSiswaData> newDabs = new ArrayList<>();
                        dabsSiswaOrtu = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childTgl : snapshot.getChildren()) {
                            for (DataSnapshot arrChild : childTgl.getChildren()){
                                DaftarAbsensiSiswaData row = new DaftarAbsensiSiswaData();
                                row.no = (i + 1);
                                row.ket = checkKet(arrChild.child("ket").getValue().toString());
                                row.nis = arrChild.child("nis").getValue().toString();
                                row.nm = arrChild.child("nm").getValue().toString();
                                row.tgl = arrChild.child("tgl").getValue().toString();
                                row.wkt = arrChild.child("wkt").getValue().toString();
                                long epochNow = 0L;
                                try { epochNow = new SimpleDateFormat("dd-MM-yyyy").parse(row.tgl).getTime();
                                } catch (ParseException e) { e.printStackTrace(); }
                                if(epochDari != null && epochKe != null){
                                    isFilter = true;
                                    if(row.nis.contentEquals(nis) && epochNow >= epochDari && epochNow <= epochKe){
                                        newDabs.add(row);
                                        i++;
                                    }
                                } else if (row.nis.contentEquals(nis)){
                                    newDabs.add(row);
                                    i++;
                                }
                            }
                        }

                        if(toFilter.size() > 0){
                            for (int x = 0; x < toFilter.size() ; x++){
                                Filter aFilter = toFilter.get(x);
                                for (int y = 0; y < newDabs.size(); y++){
                                    for (Field f : newDabs.get(y).getClass().getDeclaredFields()) {
                                        try {
                                            if(f.getName().contentEquals(aFilter.toFilter)){
                                                isFilter = true;
                                                final JsonObject jo = (JsonObject) new Gson().toJsonTree(newDabs.get(y));
                                                if(jo.get(f.getName()).getAsString().contentEquals(aFilter.filterSet)){
                                                    dabsSiswaOrtu.add(newDabs.get(y));
                                                }
                                            }
                                        } catch (Exception e) { e.printStackTrace(); }
                                    }
                                }
                            }
                        } else {
                            dabsSiswaOrtu = newDabs;
                        }

                        loadTableData(true);
                        pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                    } else {
                        //Log.i("ABS-DATA", "No data for " + namaKelas);
                        pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                    }
                }


                private String checkKet(String ket) {
                    if (ket != null){
                        if(ket.contentEquals("s")) { return strsakit;
                        } else if(ket.contentEquals("i")) { return strijin;
                        } else if(ket.contentEquals("m")) { return strmasuk;
                        } else { return stralpha;
                        }
                    } else return "n/a";
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_absensi_ortu.setVisibility(View.GONE);
                }
            });
        }
    }

    private void loadTableData(boolean isFilter){
        Context context = requireContext();
        int rows = dabsSiswaOrtu.size();
        LoadTableHeader header = new LoadTableHeader(context);
        if (dabsSiswaOrtu != null && dabsSiswaOrtu.size() > 0){
            if(isFilter){
                tl_daftar_siswa_laporan_absensi_ortu.removeAllViews();
                tl_daftar_siswa_laporan_absensi_ortu.addView(header.tableHeader, header.tableParam);
            }
            DaftarAbsensiSiswaData row;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = dabsSiswaOrtu.get(i);
                final int COLUMN_COUNT = 6;
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

                final TextView tvNis = new TextView(context);
                tvNis.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNis.setGravity(Gravity.CENTER);
                tvNis.setPadding(5, 15, 0, 15);
                tvNis.setBackgroundColor(Color.parseColor(textColor));
                tvNis.setText(String.valueOf(row.nis));

                final TextView tvNm = new TextView(context);
                tvNm.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNm.setGravity(Gravity.CENTER);
                tvNm.setBackgroundColor(Color.parseColor(textColor));
                tvNm.setPadding(5, 15, 0, 15);
                tvNm.setText(String.valueOf(row.nm));

                final TextView tvKet = new TextView(context);
                tvKet.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvKet.setGravity(Gravity.CENTER);
                tvKet.setPadding(5, 15, 0, 15);
                tvKet.setBackgroundColor(Color.parseColor(textColor));
                tvKet.setText(String.valueOf(row.ket));

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
                trAbsen.addView(tvNis);
                trAbsen.addView(tvNm);
                trAbsen.addView(tvKet);

                tl_daftar_siswa_laporan_absensi_ortu.addView(trAbsen, trParams);
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
                tl_daftar_siswa_laporan_absensi_ortu.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa_laporan_absensi_ortu.setVisibility(View.VISIBLE);
        } else {
            //Log.i("ABS-table", "No data");
            tl_daftar_siswa_laporan_absensi_ortu.removeAllViews();
            tl_daftar_siswa_laporan_absensi_ortu.addView(header.tableHeader, header.tableParam);
        }
    }

    private class LoadTableHeader{
        private TableRow tableHeader;
        private TableLayout.LayoutParams tableParam;

        private LoadTableHeader(Context context){
            final TextView tvNoHeader = new TextView(context);
            tvNoHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.WRAP_CONTENT));
            tvNoHeader.setGravity(Gravity.CENTER);
            tvNoHeader.setPadding(5, 15, 0, 15);
            tvNoHeader.setText("No");
            tvNoHeader.setBackgroundResource(R.color.bg_header_col);
            tvNoHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvTglHeader = new TextView(context);
            tvTglHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvTglHeader.setGravity(Gravity.CENTER);
            tvTglHeader.setPadding(5, 15, 0, 15);
            tvTglHeader.setText("Tanggal");
            tvTglHeader.setBackgroundResource(R.color.bg_header_col);
            tvTglHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvWaktuHeader = new TextView(context);
            tvWaktuHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvWaktuHeader.setGravity(Gravity.CENTER);
            tvWaktuHeader.setPadding(5, 15, 0, 15);
            tvWaktuHeader.setText("Waktu");
            tvWaktuHeader.setBackgroundResource(R.color.bg_header_col);
            tvWaktuHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvNisHeader = new TextView(context);
            tvNisHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvNisHeader.setGravity(Gravity.CENTER);
            tvNisHeader.setPadding(5, 15, 0, 15);
            tvNisHeader.setText("No Induk");
            tvNisHeader.setBackgroundResource(R.color.bg_header_col);
            tvNisHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvNamaHeader = new TextView(context);
            tvNamaHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.WRAP_CONTENT));
            tvNamaHeader.setGravity(Gravity.CENTER);
            tvNamaHeader.setPadding(5, 15, 0, 15);
            tvNamaHeader.setText("Nama");
            tvNamaHeader.setBackgroundResource(R.color.bg_header_col);
            tvNamaHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvKetHeader = new TextView(context);
            tvKetHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvKetHeader.setGravity(Gravity.CENTER);
            tvKetHeader.setPadding(5, 15, 0, 15);
            tvKetHeader.setText("Ket");
            tvKetHeader.setBackgroundResource(R.color.bg_header_col);
            tvKetHeader.setTextAppearance(context, R.style.header_col);

            tableParam = new TableLayout.LayoutParams(TableLayout
                    .LayoutParams.MATCH_PARENT, TableLayout
                    .LayoutParams.WRAP_CONTENT);
            tableParam.setMargins(0, 0, 0, 0);

            tableHeader = new TableRow(context);
            tableHeader.setPadding(0,0,0,0);
            tableHeader.setLayoutParams(tableParam);
            tableHeader.addView(tvNoHeader);
            tableHeader.addView(tvTglHeader);
            tableHeader.addView(tvWaktuHeader);
            tableHeader.addView(tvNisHeader);
            tableHeader.addView(tvNamaHeader);
            tableHeader.addView(tvKetHeader);
        }
    }
}