package id.ycmlg.absensisiswa.main.ortu.laporan;

import android.app.DatePickerDialog;
import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ImageView;
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
import id.ycmlg.absensisiswa.data.DaftarSiswaNilaiEditData;
import id.ycmlg.absensisiswa.data.Filter;
import id.ycmlg.absensisiswa.databinding.FragmentLaporanNilaiAkademikBinding;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LaporanNilaiAkademikOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LaporanNilaiAkademikOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "namaKelas";
    private static final String ARG_PARAM2 = "nis";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;

    public LaporanNilaiAkademikOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param namaKelas Parameter 1.
     * @param nis Parameter 2.
     * @return A new instance of fragment LaporanNilaiAkademikFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static LaporanNilaiAkademikOrtuFragment newInstance(String namaKelas, String nis) {
        LaporanNilaiAkademikOrtuFragment fragment = new LaporanNilaiAkademikOrtuFragment();
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
            nilaiRef = database.getReference("nilaiakademik");
        }
    }

    private View root;
    private FirebaseDatabase database;
    private DatabaseReference nilaiRef;
    private List<DaftarSiswaNilaiEditData> dsNilaIAkademikData;
    private FragmentLaporanNilaiAkademikBinding lnaBinded;
    private EditText ed_laporan_nilai_akademik;
    private EditText ed_laporan_nilai_akademik_tanggal_dari;
    private EditText ed_laporan_nilai_akademik_tanggal_ke;
    private ImageButton ib_start_date_laporan_nilai_akademik;
    private ImageButton ib_end_date_laporan_nilai_akademik;
    private ImageView ib_search_laporan_nilai_akademik;
    private TableLayout tl_daftar_siswa_laporan_nilai_akademik;
    private LinearLayout pb_ll_laporan_nilai_akademik;
    private DatePickerDialog datePickerDialog;
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
        lnaBinded = FragmentLaporanNilaiAkademikBinding.inflate(inflater, container, false);
        root = lnaBinded.getRoot();
        ed_laporan_nilai_akademik = lnaBinded.edLaporanNilaiAkademik;
        ed_laporan_nilai_akademik_tanggal_dari = lnaBinded.edLaporanNilaiAkademikTanggalDari;
        ed_laporan_nilai_akademik_tanggal_ke = lnaBinded.edLaporanNilaiAkademikTanggalKe;
        ib_start_date_laporan_nilai_akademik = lnaBinded.ibStartDateLaporanNilaiAkademik;
        ib_end_date_laporan_nilai_akademik = lnaBinded.ibStartDateLaporanNilaiAkademik;
        ib_search_laporan_nilai_akademik = lnaBinded.ibSearchLaporanNilaiAkademik;
        tl_daftar_siswa_laporan_nilai_akademik = lnaBinded.tlDaftarSiswaLaporanNilaiAkademik;
        pb_ll_laporan_nilai_akademik = root.findViewById(R.id.pb_ll_laporan_nilai_akademik);

        ed_laporan_nilai_akademik.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {}
            @Override
            public void afterTextChanged(Editable s) {
                String nisSer = "";
                if(s != null) nisSer = s.toString().trim();
                if(nisSer.length() > 0){
                    toFilter = new ArrayList<>();
                    Filter aFilter = new Filter();
                    aFilter.filterSet = s.toString();
                    aFilter.toFilter = "mapel";
                    toFilter.add(aFilter);
                } else{
                    toFilter = new ArrayList<>();
                }

                loadFilteredData();
            }
        });

        ib_start_date_laporan_nilai_akademik.setOnClickListener(view -> {
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
                        ed_laporan_nilai_akademik_tanggal_dari.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_end_date_laporan_nilai_akademik.setOnClickListener(view -> {
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
                        ed_laporan_nilai_akademik_tanggal_ke.setText(dayOfMonth + "-"+ (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_search_laporan_nilai_akademik.setOnClickListener(view -> {
            //final String nisEd = ed_laporan_nilai_akademik.getText().toString().trim();
            final String tglDari = ed_laporan_nilai_akademik_tanggal_dari.getText().toString().trim();
            final String tglKe = ed_laporan_nilai_akademik_tanggal_ke.getText().toString().trim();
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

        /*if(nilaiRef != null) {
            nilaiRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    int cnt = (int) snapshot.getChildrenCount();
                    dsNilaIAkademikData = new ArrayList<>();
                    int i = 0;
                    for (DataSnapshot childAka : snapshot.getChildren()) {
                        for (DataSnapshot childKls : childAka.getChildren()) {
                            for (DataSnapshot childSubject : childKls.getChildren()) {
                                for (DataSnapshot childArr : childSubject.getChildren()) {
                                    DaftarSiswaNilaiEditData row = new DaftarSiswaNilaiEditData();
                                    row.no = (i + 1);
                                    row.created = childArr.child("created").getValue().toString();
                                    row.mapel = childArr.child("mapel").getValue().toString();
                                    row.jn = childArr.child("jn").getValue().toString();
                                    row.klssmt = childArr.child("klssmt").getValue().toString();
                                    row.n = childArr.child("n").getValue().toString();
                                    row.nis = childArr.child("nis").getValue().toString();
                                    row.nm = childArr.child("nm").getValue().toString();
                                    row.pmb = childArr.child("pmb").getValue().toString();
                                    row.st = childArr.child("st").getValue().toString();
                                    row.sub = childArr.child("sub").getValue().toString();
                                    row.t = childArr.child("t").getValue().toString();
                                    row.ta = childArr.child("ta").getValue().toString();
                                    if(row.nis.contentEquals(nis)){
                                        dsNilaIAkademikData.add(row);
                                        i++;
                                    }
                                }
                            }
                        }
                    }

                    loadTableData(false);
                    pb_ll_laporan_nilai_akademik.setVisibility(View.GONE);
                }


                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_nilai_akademik.setVisibility(View.GONE);
                }
            });
        }*/

        loadFilteredData();

        return root;
    }

    private void loadFilteredData(){
        if(nilaiRef != null) {
            pb_ll_laporan_nilai_akademik.setVisibility(View.VISIBLE);
            nilaiRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    boolean isFilter = false;
                    int cnt = (int) snapshot.getChildrenCount();
                    List<DaftarSiswaNilaiEditData> newDsn = new ArrayList<>();
                    dsNilaIAkademikData = new ArrayList<>();
                    int i = 0;
                    for (DataSnapshot childAka : snapshot.getChildren()) {
                        for (DataSnapshot childKls : childAka.getChildren()) {
                            for (DataSnapshot childSubject : childKls.getChildren()) {
                                for (DataSnapshot childArr : childSubject.getChildren()) {
                                    DaftarSiswaNilaiEditData row = new DaftarSiswaNilaiEditData();
                                    row.no = (i + 1);
                                    row.created = childArr.child("created").getValue().toString();
                                    row.mapel = childArr.child("mapel").getValue().toString();
                                    row.jn = childArr.child("jn").getValue().toString();
                                    row.klssmt = childArr.child("klssmt").getValue().toString();
                                    row.n = childArr.child("n").getValue().toString();
                                    row.nis = childArr.child("nis").getValue().toString();
                                    row.nm = childArr.child("nm").getValue().toString();
                                    row.pmb = childArr.child("pmb").getValue().toString();
                                    row.st = childArr.child("st").getValue().toString();
                                    row.sub = childArr.child("sub").getValue().toString();
                                    row.t = childArr.child("t").getValue().toString();
                                    row.ta = childArr.child("ta").getValue().toString();
                                    long epochNow = 0;
                                    try { epochNow = new SimpleDateFormat("dd-MM-yyyy").parse(row.created).getTime();
                                    } catch (ParseException e) { e.printStackTrace(); }
                                    if(epochDari != null && epochKe != null){
                                        isFilter = true;
                                        if(row.nis.contentEquals(nis) && epochNow >= epochDari && epochNow <= epochKe){
                                            newDsn.add(row);
                                            i++;
                                        }
                                    } else if(row.nis.contentEquals(nis)){
                                        newDsn.add(row);
                                        i++;
                                    }
                                }
                            }
                        }
                    }

                    if(toFilter.size() > 0){
                        for (int x = 0; x < toFilter.size() ; x++){
                            Filter aFilter = toFilter.get(x);
                            for (int y = 0; y < newDsn.size(); y++){
                                for (Field f : newDsn.get(y).getClass().getDeclaredFields()) {
                                    try {
                                        if(f.getName().contentEquals(aFilter.toFilter)){
                                            isFilter = true;
                                            final JsonObject jo = (JsonObject) new Gson().toJsonTree(newDsn.get(y));
                                            if(jo.get(f.getName()).getAsString().toLowerCase().contains(aFilter.filterSet.toLowerCase())){
                                                dsNilaIAkademikData.add(newDsn.get(y));
                                            }
                                        }
                                    } catch (Exception e) { e.printStackTrace(); }
                                }
                            }
                        }
                    } else {
                        dsNilaIAkademikData = newDsn;
                    }

                    loadTableData(true);
                    pb_ll_laporan_nilai_akademik.setVisibility(View.GONE);
                }


                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_nilai_akademik.setVisibility(View.GONE);
                }
            });
        }
    }

    private void loadTableData(boolean isFilter){
        Context context = requireContext();
        int rows = dsNilaIAkademikData.size();
        LoadTableHeader header = new LoadTableHeader(context);
        if (dsNilaIAkademikData != null && dsNilaIAkademikData.size() > 0){
            if(isFilter){
                tl_daftar_siswa_laporan_nilai_akademik.removeAllViews();
                tl_daftar_siswa_laporan_nilai_akademik.addView(header.tableHeader, header.tableParam);
            }
            DaftarSiswaNilaiEditData row = null;
            final int COLUMN_COUNT = 12;

            for (int i=0;i<rows;i++){
                row = dsNilaIAkademikData.get(i);
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }

                final TextView tvNo = new TextView(context);
                tvNo.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNo.setGravity(Gravity.CENTER);
                tvNo.setPadding(5, 15, 0, 15);

                final TextView tvTgl = new TextView(context);
                tvTgl.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTgl.setGravity(Gravity.CENTER);
                tvTgl.setPadding(5, 15, 0, 15);

                final TextView tvMapel = new TextView(context);
                tvMapel.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvMapel.setGravity(Gravity.CENTER);
                tvMapel.setPadding(5, 15, 0, 15);

                final TextView tvNis = new TextView(context);
                tvNis.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNis.setGravity(Gravity.CENTER);
                tvNis.setPadding(5, 15, 0, 15);

                final TextView tvNama = new TextView(context);
                tvNama.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvNama.setGravity(Gravity.CENTER);
                tvNama.setPadding(5, 15, 0, 15);

                final TextView tvTa = new TextView(context);
                tvTa.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTa.setGravity(Gravity.CENTER);
                tvTa.setPadding(5, 15, 0, 15);

                final TextView tvKs = new TextView(context);
                tvKs.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvKs.setGravity(Gravity.CENTER);
                tvKs.setPadding(5, 15, 0, 15);

                final TextView tvTm = new TextView(context);
                tvTm.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvTm.setGravity(Gravity.CENTER);
                tvTm.setPadding(5, 15, 0, 15);

                final TextView tvSt = new TextView(context);
                tvSt.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvSt.setGravity(Gravity.CENTER);
                tvSt.setPadding(5, 15, 0, 15);

                final TextView tvPmb = new TextView(context);
                tvPmb.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvPmb.setGravity(Gravity.CENTER);
                tvPmb.setPadding(5, 15, 0, 15);

                final TextView tvJn = new TextView(context);
                tvJn.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.WRAP_CONTENT));
                tvJn.setGravity(Gravity.CENTER);
                tvJn.setPadding(5, 15, 0, 15);

                final TextView tvNl = new TextView(context);
                tvNl.setLayoutParams(new TableRow.LayoutParams(TableRow
                        .LayoutParams.WRAP_CONTENT, TableRow
                        .LayoutParams.MATCH_PARENT));
                tvNl.setGravity(Gravity.CENTER);
                tvNl.setPadding(5, 15, 0, 15);

                tvNo.setBackgroundColor(Color.parseColor(textColor));
                tvTgl.setBackgroundColor(Color.parseColor(textColor));
                tvMapel.setBackgroundColor(Color.parseColor(textColor));
                tvNis.setBackgroundColor(Color.parseColor(textColor));
                tvNama.setBackgroundColor(Color.parseColor(textColor));
                tvTa.setBackgroundColor(Color.parseColor(textColor));
                tvKs.setBackgroundColor(Color.parseColor(textColor));
                tvTm.setBackgroundColor(Color.parseColor(textColor));
                tvSt.setBackgroundColor(Color.parseColor(textColor));
                tvPmb.setBackgroundColor(Color.parseColor(textColor));
                tvJn.setBackgroundColor(Color.parseColor(textColor));
                tvNl.setBackgroundColor(Color.parseColor(textColor));

                tvNo.setText(String.valueOf(row.no));
                tvTgl.setText(row.created);
                tvMapel.setText(row.mapel);
                tvNis.setText(row.nis);
                tvNama.setText(row.nm);
                tvTa.setText(row.ta);
                tvKs.setText(row.klssmt);
                tvTm.setText(row.t);
                tvSt.setText(row.st);
                tvPmb.setText(row.pmb);
                tvJn.setText(row.jn);
                tvNl.setText(row.n);

                final TableRow trNilaiEdit = new TableRow(context);
                trNilaiEdit.setId(i + 1);
                TableLayout.LayoutParams trParams = new TableLayout.LayoutParams(TableLayout
                        .LayoutParams.MATCH_PARENT, TableLayout
                        .LayoutParams.WRAP_CONTENT);
                trParams.setMargins(0, 0, 0, 0);
                trNilaiEdit.setPadding(0,0,0,0);
                trNilaiEdit.setLayoutParams(trParams);
                trNilaiEdit.addView(tvNo);
                trNilaiEdit.addView(tvTgl);
                trNilaiEdit.addView(tvMapel);
                trNilaiEdit.addView(tvNis);
                trNilaiEdit.addView(tvNama);
                trNilaiEdit.addView(tvTa);
                trNilaiEdit.addView(tvKs);
                trNilaiEdit.addView(tvTm);
                trNilaiEdit.addView(tvSt);
                trNilaiEdit.addView(tvPmb);
                trNilaiEdit.addView(tvJn);
                trNilaiEdit.addView(tvNl);

                tl_daftar_siswa_laporan_nilai_akademik.addView(trNilaiEdit, trParams);
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
                tl_daftar_siswa_laporan_nilai_akademik.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa_laporan_nilai_akademik.setVisibility(View.VISIBLE);
        } else {
            //Log.i("ABS-table", "No data");
            tl_daftar_siswa_laporan_nilai_akademik.removeAllViews();
            tl_daftar_siswa_laporan_nilai_akademik.addView(header.tableHeader, header.tableParam);
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

            final TextView tvMapelHeader = new TextView(context);
            tvMapelHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvMapelHeader.setGravity(Gravity.CENTER);
            tvMapelHeader.setPadding(5, 15, 0, 15);
            tvMapelHeader.setText("Mata Pelajaran");
            tvMapelHeader.setBackgroundResource(R.color.bg_header_col);
            tvMapelHeader.setTextAppearance(context, R.style.header_col);

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

            final TextView tvTaHeader = new TextView(context);
            tvTaHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvTaHeader.setGravity(Gravity.CENTER);
            tvTaHeader.setPadding(5, 15, 0, 15);
            tvTaHeader.setText("Tahun Ajaran");
            tvTaHeader.setBackgroundResource(R.color.bg_header_col);
            tvTaHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvKsHeader = new TextView(context);
            tvKsHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.WRAP_CONTENT));
            tvKsHeader.setGravity(Gravity.CENTER);
            tvKsHeader.setPadding(5, 15, 0, 15);
            tvKsHeader.setText("Kelas/Semester");
            tvKsHeader.setBackgroundResource(R.color.bg_header_col);
            tvKsHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvTmHeader = new TextView(context);
            tvTmHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvTmHeader.setGravity(Gravity.CENTER);
            tvTmHeader.setPadding(5, 15, 0, 15);
            tvTmHeader.setText("Tema");
            tvTmHeader.setBackgroundResource(R.color.bg_header_col);
            tvTmHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvStHeader = new TextView(context);
            tvStHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.WRAP_CONTENT));
            tvStHeader.setGravity(Gravity.CENTER);
            tvStHeader.setPadding(5, 15, 0, 15);
            tvStHeader.setText("Sub Tema");
            tvStHeader.setBackgroundResource(R.color.bg_header_col);
            tvStHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvPmbHeader = new TextView(context);
            tvPmbHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvPmbHeader.setGravity(Gravity.CENTER);
            tvPmbHeader.setPadding(5, 15, 0, 15);
            tvPmbHeader.setText("Pembelajaran");
            tvPmbHeader.setBackgroundResource(R.color.bg_header_col);
            tvPmbHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvJnHeader = new TextView(context);
            tvJnHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.WRAP_CONTENT));
            tvJnHeader.setGravity(Gravity.CENTER);
            tvJnHeader.setPadding(5, 15, 0, 15);
            tvJnHeader.setText("Jenis Nilai");
            tvJnHeader.setBackgroundResource(R.color.bg_header_col);
            tvJnHeader.setTextAppearance(context, R.style.header_col);

            final TextView tvNlHeader = new TextView(context);
            tvNlHeader.setLayoutParams(new TableRow.LayoutParams(TableRow
                    .LayoutParams.WRAP_CONTENT, TableRow
                    .LayoutParams.MATCH_PARENT));
            tvNlHeader.setGravity(Gravity.CENTER);
            tvNlHeader.setPadding(5, 15, 0, 15);
            tvNlHeader.setText("Nilai");
            tvNlHeader.setBackgroundResource(R.color.bg_header_col);
            tvNlHeader.setTextAppearance(context, R.style.header_col);

            tableParam = new TableLayout.LayoutParams(TableLayout
                    .LayoutParams.MATCH_PARENT, TableLayout
                    .LayoutParams.WRAP_CONTENT);
            tableParam.setMargins(0, 0, 0, 0);

            tableHeader = new TableRow(context);
            tableHeader.setPadding(0,0,0,0);
            tableHeader.setLayoutParams(tableParam);
            tableHeader.addView(tvNoHeader);
            tableHeader.addView(tvTglHeader);
            tableHeader.addView(tvMapelHeader);
            tableHeader.addView(tvNisHeader);
            tableHeader.addView(tvNamaHeader);
            tableHeader.addView(tvTaHeader);
            tableHeader.addView(tvKsHeader);
            tableHeader.addView(tvTmHeader);
            tableHeader.addView(tvStHeader);
            tableHeader.addView(tvPmbHeader);
            tableHeader.addView(tvJnHeader);
            tableHeader.addView(tvNlHeader);
        }
    }
}