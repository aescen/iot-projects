package id.ycmlg.absensisiswa.main.guru.home.menukelas.raport;

import android.app.DatePickerDialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
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
import id.ycmlg.absensisiswa.data.DaftarSiswaLaporanRaportData;
import id.ycmlg.absensisiswa.data.Filter;
import id.ycmlg.absensisiswa.main.ortu.raport.RaporPDFViewFragment;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LaporanGuruRaportFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LaporanGuruRaportFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String mParam2;

    public LaporanGuruRaportFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param param2 Parameter 2.
     * @return A new instance of fragment LaporanRaportFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static LaporanGuruRaportFragment newInstance(String param1, String param2) {
        LaporanGuruRaportFragment fragment = new LaporanGuruRaportFragment();
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
            kelasRef = database.getReference("laporanrapor").child(namaKelas.toLowerCase().replaceAll("\\s+",""));
        }
    }

    private View root;
    private TableLayout tl_daftar_siswa_laporan_raport_guru;
    private FirebaseDatabase database;
    private DatabaseReference kelasRef;
    private List<DaftarSiswaLaporanRaportData> daftarSiswaLaporanRaportData;
    private LinearLayout pb_ll_laporan_raport;
    private DatePickerDialog datePickerDialog;
    private EditText ed_raport;
    private EditText ed_laporan_raport_tanggal_dari;
    private EditText ed_laporan_raport_tanggal_ke;
    private ImageButton ib_laporan_raport_date_start;
    private ImageButton ib_laporan_raport_date_end;
    private ImageButton ib_search_laporan_raport;
    private int dayD;
    private int monthD;
    private int yearD;
    private Long epochDari;
    private Long epochKe;
    private List<Filter> toFilter= new ArrayList<>();

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_laporan_raport, container, false);
        tl_daftar_siswa_laporan_raport_guru = root.findViewById(R.id.tl_daftar_siswa_laporan_raport_guru);
        pb_ll_laporan_raport = root.findViewById(R.id.pb_ll_laporan_raport);
        pb_ll_laporan_raport.setVisibility(View.VISIBLE);

        ed_raport = root.findViewById(R.id.ed_raport);
        ed_laporan_raport_tanggal_dari = root.findViewById(R.id.ed_laporan_raport_tanggal_dari);
        ed_laporan_raport_tanggal_ke = root.findViewById(R.id.ed_laporan_raport_tanggal_ke);
        ib_laporan_raport_date_start = root.findViewById(R.id.ib_laporan_raport_date_start);
        ib_laporan_raport_date_end = root.findViewById(R.id.ib_laporan_raport_date_end);
        ib_search_laporan_raport = root.findViewById(R.id.ib_search_laporan_raport);

        ed_raport.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}
            @Override
            public void afterTextChanged(Editable s) {
                String nisSer = "";
                if(s != null) nisSer = s.toString().trim();
                if(nisSer.length() > 0){
                    toFilter = new ArrayList<>();
                    Filter aFilter = new Filter();
                    aFilter.filterSet = nisSer;
                    aFilter.toFilter = "nis";
                    toFilter.add(aFilter);
                } else{
                    toFilter = new ArrayList<>();
                }

                loadFilteredData();
            }
        });

        ib_laporan_raport_date_start.setOnClickListener(view -> {
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
                        ed_laporan_raport_tanggal_dari.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_laporan_raport_date_end.setOnClickListener(view -> {
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
                        ed_laporan_raport_tanggal_ke.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_search_laporan_raport.setOnClickListener(view -> {
            //final String nisEd = ed_laporan_nilai_akademik.getText().toString().trim();
            final String tglDari = ed_laporan_raport_tanggal_dari.getText().toString().trim();
            final String tglKe = ed_laporan_raport_tanggal_ke.getText().toString().trim();
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
                        //Log.i("CAT-DATA", snapshot.toString());
                        daftarSiswaLaporanRaportData = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot arrChild : snapshot.getChildren()){
                            DaftarSiswaLaporanRaportData row = new DaftarSiswaLaporanRaportData();
                            row.no = (i + 1);
                            row.ket = arrChild.child("ket").getValue().toString();
                            row.nf = arrChild.child("nf").getValue().toString();
                            row.nis = arrChild.child("nis").getValue().toString();
                            row.nm = arrChild.child("nm").getValue().toString();
                            row.tgl = arrChild.child("tgl").getValue().toString();
                            row.wkt = arrChild.child("wkt").getValue().toString();
                            daftarSiswaLaporanRaportData.add(row);
                            i++;
                        }
                        loadTableData(false);
                        pb_ll_laporan_raport.setVisibility(View.GONE);
                    } else {
                        pb_ll_laporan_raport.setVisibility(View.GONE);
                        //Log.i("CAT-DATA", "No data for " + namaKelas);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_raport.setVisibility(View.GONE);
                }
            });
        }*/

        loadFilteredData();

        return root;
    }

    private void loadFilteredData(){
        if(kelasRef != null) {
            pb_ll_laporan_raport.setVisibility(View.VISIBLE);
            kelasRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    boolean isFilter = false;
                    if (snapshot.getValue() != null) {
                        //Log.i("CAT-DATA", snapshot.toString());
                        List<DaftarSiswaLaporanRaportData> newDsl = new ArrayList<>();
                        daftarSiswaLaporanRaportData = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot arrChild : snapshot.getChildren()){
                            DaftarSiswaLaporanRaportData row = new DaftarSiswaLaporanRaportData();
                            row.no = (i + 1);
                            row.ket = arrChild.child("ket").getValue().toString();
                            row.nf = arrChild.child("nf").getValue().toString();
                            row.nis = arrChild.child("nis").getValue().toString();
                            row.nm = arrChild.child("nm").getValue().toString();
                            row.tgl = arrChild.child("tgl").getValue().toString();
                            row.wkt = arrChild.child("wkt").getValue().toString();
                            long epochNow = 0;
                            try { epochNow = new SimpleDateFormat("dd-MM-yyyy").parse(row.tgl).getTime();
                            } catch (ParseException e) { e.printStackTrace(); }
                            if(epochDari != null && epochKe != null){
                                isFilter = true;
                                if(epochNow >= epochDari && epochNow <= epochKe){
                                    newDsl.add(row);
                                    i++;
                                }
                            } else {
                                newDsl.add(row);
                                i++;
                            }
                        }

                        if(toFilter.size() > 0){
                            for (int x = 0; x < toFilter.size() ; x++){
                                Filter aFilter = toFilter.get(x);
                                for (int y = 0; y < newDsl.size(); y++){
                                    for (Field f : newDsl.get(y).getClass().getDeclaredFields()) {
                                        try {
                                            if(f.getName().contentEquals(aFilter.toFilter)){
                                                isFilter = true;
                                                final JsonObject jo = (JsonObject) new Gson().toJsonTree(newDsl.get(y));
                                                if(jo.get(f.getName()).getAsString().contains(aFilter.filterSet)){
                                                    daftarSiswaLaporanRaportData.add(newDsl.get(y));
                                                }
                                            }
                                        } catch (Exception e) { e.printStackTrace(); }
                                    }
                                }
                            }
                        } else {
                            daftarSiswaLaporanRaportData = newDsl;
                        }

                        loadTableData(true);
                        pb_ll_laporan_raport.setVisibility(View.GONE);
                    } else {
                        pb_ll_laporan_raport.setVisibility(View.GONE);
                        //Log.i("CAT-DATA", "No data for " + namaKelas);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_raport.setVisibility(View.GONE);
                }
            });
        }
    }

    private void loadTableData(boolean isFilter){
        Context context = requireContext();
        int rows = daftarSiswaLaporanRaportData.size();
        LoadTableHeader header = new LoadTableHeader(context);
        if (daftarSiswaLaporanRaportData != null && daftarSiswaLaporanRaportData.size() > 0){
            if(isFilter){
                tl_daftar_siswa_laporan_raport_guru.removeAllViews();
                tl_daftar_siswa_laporan_raport_guru.addView(header.tableHeader, header.tableParam);
            }
            DaftarSiswaLaporanRaportData row;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = daftarSiswaLaporanRaportData.get(i);
                final int COLUMN_COUNT = 7;
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
                                .replace(R.id.nav_kelas_host_fragment, fragment)
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
                trAbsen.addView(tvNis);
                trAbsen.addView(tvNm);
                trAbsen.addView(tvKet);
                trAbsen.addView(tvVF);

                tl_daftar_siswa_laporan_raport_guru.addView(trAbsen, trParams);
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
                tl_daftar_siswa_laporan_raport_guru.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa_laporan_raport_guru.setVisibility(View.VISIBLE);
        } else {
            //Log.i("CAT-table", "No data");
            tl_daftar_siswa_laporan_raport_guru.removeAllViews();
            tl_daftar_siswa_laporan_raport_guru.addView(header.tableHeader, header.tableParam);
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

            final TextView tvVFHeader = new TextView(context);
            tvVFHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvVFHeader.setGravity(Gravity.CENTER);
            tvVFHeader.setPadding(5, 15, 0, 15);
            tvVFHeader.setText("View File");
            tvVFHeader.setBackgroundResource(R.color.bg_header_col);
            tvVFHeader.setTextAppearance(context, R.style.header_col);

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
            tableHeader.addView(tvVFHeader);
        }
    }
}