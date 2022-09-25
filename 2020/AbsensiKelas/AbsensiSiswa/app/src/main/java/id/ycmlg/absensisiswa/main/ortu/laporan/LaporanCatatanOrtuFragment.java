package id.ycmlg.absensisiswa.main.ortu.laporan;

import android.app.DatePickerDialog;
import android.content.Context;
import android.graphics.Color;
import android.graphics.Paint;
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
import androidx.fragment.app.FragmentTransaction;

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
import id.ycmlg.absensisiswa.data.DaftarSiswaLaporanCatatan;
import id.ycmlg.absensisiswa.data.Filter;
import id.ycmlg.absensisiswa.databinding.FragmentLaporanCatatanOrtuBinding;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.PelanggaranFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.SikapFragment;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link LaporanCatatanOrtuFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class LaporanCatatanOrtuFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "nis";

    // TODO: Rename and change types of parameters
    private String namaKelas;
    private String nis;

    public LaporanCatatanOrtuFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param param1 Parameter 1.
     * @param nis    Parameter 2.
     * @return A new instance of fragment LaporanCatatanFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static LaporanCatatanOrtuFragment newInstance(String param1, String nis) {
        LaporanCatatanOrtuFragment fragment = new LaporanCatatanOrtuFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
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
            catatanRef = database.getReference("catatan").child(namaKelas.toLowerCase().replaceAll("\\s+", ""));
        }
    }

    private View root;
    private FirebaseDatabase database;
    private DatabaseReference catatanRef;
    private List<DaftarSiswaLaporanCatatan> dsLaporanCatatanOrtu;
    private LinearLayout pb_ll_laporan_catatan_ortu;
    private DatePickerDialog datePickerDialog;
    private EditText ed_laporan_catatan_ortu;
    private EditText ed_laporan_catatan_ortu_tanggal_dari;
    private EditText ed_laporan_catatan_ortu_tanggal_ke;
    private ImageButton ib_laporan_catatan_ortu_start_date;
    private ImageButton ib_laporan_catatan_ortu_end_date;
    private ImageButton ib_search_laporan_catatan_ortu;
    private TableLayout tl_daftar_siswa_laporan_catatan_ortu;
    private FragmentLaporanCatatanOrtuBinding lapCatOrtuBinded;
    private int dayD;
    private int monthD;
    private int yearD;
    private Long epochDari;
    private Long epochKe;
    private List<Filter> toFilter= new ArrayList<>();
    private CheckBox cb_sikap;
    private CheckBox cb_pelanggaran;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        lapCatOrtuBinded = FragmentLaporanCatatanOrtuBinding.inflate(inflater, container, false);
        root = lapCatOrtuBinded.getRoot();
        tl_daftar_siswa_laporan_catatan_ortu = root.findViewById(R.id.tl_daftar_siswa_laporan_catatan_ortu);
        pb_ll_laporan_catatan_ortu = root.findViewById(R.id.pb_ll_laporan_catatan_ortu);
        pb_ll_laporan_catatan_ortu.setVisibility(View.VISIBLE);

        cb_pelanggaran = root.findViewById(R.id.cb_pelanggaran);
        cb_sikap = root.findViewById(R.id.cb_sikap);

        ed_laporan_catatan_ortu_tanggal_dari = root.findViewById(R.id.ed_laporan_catatan_ortu_tanggal_dari);
        ed_laporan_catatan_ortu_tanggal_ke = root.findViewById(R.id.ed_laporan_catatan_ortu_tanggal_ke);
        ib_laporan_catatan_ortu_start_date = root.findViewById(R.id.ib_laporan_catatan_ortu_start_date);
        ib_laporan_catatan_ortu_end_date = root.findViewById(R.id.ib_laporan_catatan_ortu_end_date);
        ib_search_laporan_catatan_ortu = root.findViewById(R.id.ib_search_laporan_catatan_ortu);

        cb_sikap.setOnCheckedChangeListener((buttonView, isChecked) -> {
            boolean filterPresent = false;
            for (Filter aFilter:toFilter) {
                if(aFilter.toFilter.contentEquals("skp")){
                    filterPresent = true;
                }
            }
            if(isChecked && !filterPresent){
                Filter aFilter = new Filter();
                aFilter.filterSet = "";
                aFilter.toFilter = "skp";
                toFilter.add(aFilter);
            }else if(!isChecked){
                for (int i = 0; i < toFilter.size(); i++) {
                    if(toFilter.get(i).toFilter.contentEquals("skp")){
                        toFilter.remove(i);
                    }
                }
            }

            loadFilteredData();
        });

        cb_pelanggaran.setOnCheckedChangeListener((buttonView, isChecked) -> {
            boolean filterPresent = false;
            for (Filter aFilter:toFilter) {
                if(aFilter.toFilter.contentEquals("plgrn")){
                    filterPresent = true;
                }
            }
            if(isChecked && !filterPresent){
                Filter aFilter = new Filter();
                aFilter.filterSet = "";
                aFilter.toFilter = "plgrn";
                toFilter.add(aFilter);
            }else if(!isChecked){
                for (int i = 0; i < toFilter.size(); i++) {
                    if(toFilter.get(i).toFilter.contentEquals("plgrn")){
                        toFilter.remove(i);
                        break;
                    }
                }
            }

            loadFilteredData();
        });

        ib_laporan_catatan_ortu_start_date.setOnClickListener(view -> {
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
                        ed_laporan_catatan_ortu_tanggal_dari.setText(dayOfMonth + "-" + (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_laporan_catatan_ortu_end_date.setOnClickListener(view -> {
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
                        ed_laporan_catatan_ortu_tanggal_ke.setText(dayOfMonth + "-" + (monthOfYear + 1) + "-" + year);
                    }, mYear, mMonth, mDay);
            datePickerDialog.show();
        });

        ib_search_laporan_catatan_ortu.setOnClickListener(view -> {
            //final String nisEd = ed_laporan_nilai_akademik.getText().toString().trim();
            final String tglDari = ed_laporan_catatan_ortu_tanggal_dari.getText().toString().trim();
            final String tglKe = ed_laporan_catatan_ortu_tanggal_ke.getText().toString().trim();
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

        /*if (catatanRef != null) {
            catatanRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    if (snapshot.getValue() != null) {
                        //Log.i("CAT-DATA", snapshot.toString());
                        dsLaporanCatatanOrtu = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childTgl : snapshot.getChildren()) {
                            for (DataSnapshot arrChild : childTgl.getChildren()) {
                                DaftarSiswaLaporanCatatan row = new DaftarSiswaLaporanCatatan();
                                row.no = (i + 1);
                                row.plgrn = arrChild.child("plgrn").getValue();
                                row.skp = arrChild.child("skp").getValue();
                                row.nis = arrChild.child("nis").getValue().toString();
                                row.tgl = arrChild.child("tgl").getValue().toString();
                                row.wkt = arrChild.child("wkt").getValue().toString();
                                row.nm = arrChild.child("nm").getValue().toString();
                                if (row.nis.contentEquals(nis)) {
                                    dsLaporanCatatanOrtu.add(row);
                                    i++;
                                }
                            }
                        }
                        loadTableData(false);
                        pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                    } else {
                        pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                        //Log.i("CAT-DATA", "No data for " + namaKelas);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                }
            });
        }*/

        loadFilteredData();

        return root;
    }

    private void loadFilteredData(){
        if (catatanRef != null) {
            pb_ll_laporan_catatan_ortu.setVisibility(View.VISIBLE);
            catatanRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    boolean isFilter = false;
                    if (snapshot.getValue() != null) {
                        //Log.i("CAT-DATA", snapshot.toString());
                        List<DaftarSiswaLaporanCatatan> newDs = new ArrayList<>();
                        dsLaporanCatatanOrtu = new ArrayList<>();
                        int i = 0;
                        for (DataSnapshot childTgl : snapshot.getChildren()) {
                            for (DataSnapshot arrChild : childTgl.getChildren()) {
                                DaftarSiswaLaporanCatatan row = new DaftarSiswaLaporanCatatan();
                                row.no = (i + 1);
                                row.plgrn = arrChild.child("plgrn").getValue();
                                row.skp = arrChild.child("skp").getValue();
                                row.nis = arrChild.child("nis").getValue().toString();
                                row.tgl = arrChild.child("tgl").getValue().toString();
                                row.wkt = arrChild.child("wkt").getValue().toString();
                                row.nm = arrChild.child("nm").getValue().toString();
                                long epochNow = 0;
                                try { epochNow = new SimpleDateFormat("dd-MM-yyyy").parse(row.tgl).getTime();
                                } catch (ParseException e) { e.printStackTrace(); }
                                if(epochDari != null && epochKe != null){
                                    isFilter = true;
                                    if (row.nis.contentEquals(nis) && epochNow >= epochDari && epochNow <= epochKe) {
                                        newDs.add(row);
                                        i++;
                                    }
                                } else if (row.nis.contentEquals(nis)){
                                    newDs.add(row);
                                    i++;
                                }
                            }
                        }

                        if(toFilter.size() > 0){
                            for (int x = 0; x < toFilter.size() ; x++){
                                Filter aFilter = toFilter.get(x);
                                for (int y = 0; y < newDs.size(); y++){
                                    for (Field f : newDs.get(y).getClass().getDeclaredFields()) {
                                        try {
                                            if(f.getName().contentEquals(aFilter.toFilter)){
                                                isFilter = true;
                                                final JsonObject jo = (JsonObject) new Gson().toJsonTree(newDs.get(y));
                                                if(jo.get(f.getName()) != null){
                                                    if(f.getName().contentEquals(aFilter.toFilter)){
                                                        dsLaporanCatatanOrtu.add(newDs.get(y));
                                                    }
                                                }
                                            }
                                        } catch (Exception e) { e.printStackTrace(); }
                                    }
                                }
                            }
                        } else {
                            dsLaporanCatatanOrtu = newDs;
                        }


                        loadTableData(true);
                        pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                    } else {
                        pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                        //Log.i("CAT-DATA", "No data for " + namaKelas);
                    }
                }

                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_laporan_catatan_ortu.setVisibility(View.GONE);
                }
            });
        }
    }

    private void loadTableData(boolean isFilter){
        Context context = requireContext();
        int rows = dsLaporanCatatanOrtu.size();
        LoadTableHeader header = new LoadTableHeader(context);
        if (dsLaporanCatatanOrtu != null && dsLaporanCatatanOrtu.size() > 0){
            if(isFilter){
                tl_daftar_siswa_laporan_catatan_ortu.removeAllViews();
                tl_daftar_siswa_laporan_catatan_ortu.addView(header.tableHeader, header.tableParam);
            }
            DaftarSiswaLaporanCatatan row;
            for (int i=0;i<rows;i++){
                String textColor = "#f8f8f8";
                if(i % 2 == 0){
                    textColor = "#ffffff";
                } else {
                    textColor = "#f8f8f8";
                }
                row = dsLaporanCatatanOrtu.get(i);
                final int COLUMN_COUNT = 4;
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
                //Log.i("CAT", row.skp + ":" + row.plgrn);
                if(row.skp != null){
                    final String nis = row.nis;
                    final String nama = row.nm;
                    final String sikap = row.skp.toString();
                    tvVF.setOnClickListener(view -> {
                        Fragment fragment = SikapFragment.newInstance(namaKelas, nis, nama, sikap);
                        loadFragment(fragment, "Sikap");

                    });
                } else if (row.plgrn != null) {
                    final String nis = row.nis;
                    final String nama = row.nm;
                    final String sikap = row.plgrn.toString();
                    tvVF.setOnClickListener(view -> {
                        Fragment fragment = PelanggaranFragment.newInstance(namaKelas, nis, nama, sikap);
                        loadFragment(fragment, "Pelanggaran");
                    });
                } else {
                    tvVF.setText("null");
                }

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

                tl_daftar_siswa_laporan_catatan_ortu.addView(trAbsen, trParams);
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
                tl_daftar_siswa_laporan_catatan_ortu.addView(trSep, trParamsSep);
            }
            tl_daftar_siswa_laporan_catatan_ortu.setVisibility(View.VISIBLE);
        } else {
            //Log.i("CAT-table", "No data");
            tl_daftar_siswa_laporan_catatan_ortu.removeAllViews();
            tl_daftar_siswa_laporan_catatan_ortu.addView(header.tableHeader, header.tableParam);
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
            tableHeader.addView(tvVFHeader);
        }
    }

    private boolean loadFragment(Fragment fragment, String title) {
        //switching fragment
        if (title == null) title = "";
        if (fragment != null) {
            requireActivity().getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.nav_main_ortu_host_fragment, fragment)
                    .setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN)
                    .addToBackStack(null)
                    .commit();
            //((AppCompatActivity)requireActivity()).getSupportActionBar().setTitle(title);
            return true;
        }
        return false;
    }
}