package id.ycmlg.absensisiswa.main.guru.home.menukelas.nilaiakademik;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.DividerItemDecoration;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.HashMap;

import id.ycmlg.absensisiswa.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link NilaiListFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class NilaiListFragment extends Fragment {

    // TODO: Rename parameter arguments, choose names that match
    // the fragment initialization parameters, e.g. ARG_ITEM_NUMBER
    private static final String ARG_PARAM1 = "tipeKelas";
    private static final String ARG_PARAM2 = "namaKelas";
    private static final String ARG_PARAM3 = "mapelPath";
    private static final String ARG_PARAM4 = "mapel";
    private static final String ARG_PARAM5 = "isDelete";

    // TODO: Rename and change types of parameters
    private String tipeKelas;
    private String namaKelas;
    private String mapelPath;
    private String mapel;
    private Boolean isDelete;

    public NilaiListFragment() {
        // Required empty public constructor
    }

    /**
     * Use this factory method to create a new instance of
     * this fragment using the provided parameters.
     *
     * @param tipeKelas Parameter 1.
     * @param namaKelas Parameter 2.
     * @param mapelPath Parameter 3.
     * @param mapel Parameter 4.
     * @param isDelete Parameter 5.
     * @return A new instance of fragment NilaiListFragment.
     */
    // TODO: Rename and change types and number of parameters
    public static NilaiListFragment newInstance(String tipeKelas, String namaKelas, String mapelPath, String mapel, Boolean isDelete) {
        NilaiListFragment fragment = new NilaiListFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, tipeKelas);
        args.putString(ARG_PARAM2, namaKelas);
        args.putString(ARG_PARAM3, mapelPath);
        args.putString(ARG_PARAM4, mapel);
        if(isDelete != null){
            args.putBoolean(ARG_PARAM5, isDelete);
        }
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            tipeKelas = getArguments().getString(ARG_PARAM1);
            namaKelas = getArguments().getString(ARG_PARAM2);
            mapelPath = getArguments().getString(ARG_PARAM3);
            mapel = getArguments().getString(ARG_PARAM4);
            isDelete = getArguments().getBoolean(ARG_PARAM5);
            database = FirebaseDatabase.getInstance();
            mapelRef = database.getReference("nilaiakademik").child(mapelPath)
                    .child(namaKelas
                            .replaceAll("\\s+","")
                            .trim()
                            .toLowerCase());

            /*Log.i("NA-ARGS", tipeKelas + ":"
                    + namaKelas + ":"
                    + mapelPath + ":"
                    + mapel + ":"
                    + namaKelas.replaceAll("\\s+","").trim().toLowerCase()
                    + "\nrefs:" + database.toString() + ":" + mapelRef.toString());*/
        }
    }

    private View root = null;
    private FirebaseDatabase database;
    private DatabaseReference mapelRef;
    private TextView tv_label_mapel = null;
    private ImageButton bt_nilai_add = null;
    private ImageButton bt_nilai_del = null;
    private static RecyclerView recycler_view_nilai_list;
    private static RecyclerView.Adapter rcvAdapter;
    private static RecyclerView.LayoutManager rcvlayoutManager;
    private static final String SUBJECT_TITLE = "Subject";
    private static final String SUBJECT_TAHUN = "SubjectTahun";
    private static final String SUBJECT_PATH = "SubjectPath";
    private static HashMap<String, String[]> datasetSubject = new HashMap<>();
    private LinearLayout pb_ll_nilai_list;
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        root = inflater.inflate(R.layout.fragment_nilai_list, container, false);
        tv_label_mapel = root.findViewById(R.id.tv_title_mata_pelajaran);
        bt_nilai_add = root.findViewById(R.id.bt_nilai_add);
        bt_nilai_del = root.findViewById(R.id.bt_nilai_delete);
        pb_ll_nilai_list = root.findViewById(R.id.pb_ll_nilai_list);
        recycler_view_nilai_list = root.findViewById(R.id.recycler_view_nilai_list);
        rcvlayoutManager = new LinearLayoutManager(requireContext());
        recycler_view_nilai_list.setLayoutManager(rcvlayoutManager);

        if(mapelRef != null) {
            mapelRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot snapshot) {
                    if (snapshot.getValue() != null) {
                        //Log.i("NA-DATA", snapshot.toString());
                        String[] subArr = new String[(int) snapshot.getChildrenCount()];
                        String[] yearArr = new String[(int) snapshot.getChildrenCount()];
                        String[] subjectArr = new String[(int) snapshot.getChildrenCount()];
                        int i = 0;
                        for (DataSnapshot childAkad : snapshot.getChildren()) {
                            //Log.i("NA-ST", childAkad.getKey());
                            String nStr = childAkad.getKey().replaceAll("ss", "/");
                            nStr = nStr.replaceAll("t", ".");
                            final String subject = nStr.substring(nStr.indexOf("_") + 1, nStr.length());
                            final String year = nStr.substring(0, nStr.indexOf("_"));
                            subArr[i] = subject;
                            yearArr[i] = year;
                            subjectArr[i] = childAkad.getKey() + "&" + nStr;
                            i++;
                        }
                        datasetSubject.put(SUBJECT_TITLE, subArr);
                        datasetSubject.put(SUBJECT_TAHUN, yearArr);
                        datasetSubject.put(SUBJECT_PATH, subjectArr);
                        rcvAdapter = new RcvNilaiListAdapter(datasetSubject, isDelete);
                        recycler_view_nilai_list.addItemDecoration(new DividerItemDecoration(requireContext(), LinearLayoutManager.VERTICAL));
                        //recycler_view_nilai_list.addItemDecoration(new LineDividerItemDecoration(requireContext(), R.drawable.line_divider));
                        recycler_view_nilai_list.setAdapter(rcvAdapter);
                    } else {
                        //Log.i("NA-DATA", "No data for " + namaKelas);
                    }
                    pb_ll_nilai_list.setVisibility(View.GONE);
                }


                @Override
                public void onCancelled(@NonNull DatabaseError error) {
                    pb_ll_nilai_list.setVisibility(View.GONE);
                }
            });
        }

        tv_label_mapel.setText(mapel);

        bt_nilai_add.setOnClickListener(view -> {
            Fragment fragment = AddNilaiAkademikFragment.newInstance(namaKelas, mapel, mapelPath, null);
            requireActivity().getSupportFragmentManager().
                    beginTransaction()
                    .replace(R.id.nav_kelas_host_fragment, fragment)
                    .addToBackStack(null)
                    .commit();
        });

        bt_nilai_del.setOnClickListener(view -> {
            if(datasetSubject != null){
                isDelete = (isDelete == null) ? false : !isDelete;
                Fragment fragment = NilaiListFragment.newInstance(tipeKelas, namaKelas, mapelPath, mapel, isDelete);
                fragment.setRetainInstance(true);
                requireActivity().getSupportFragmentManager()
                        .beginTransaction()
                        .replace(R.id.nav_kelas_host_fragment, fragment)
                        .commit();
                ((AppCompatActivity)requireActivity()).getSupportActionBar().setTitle("Nilai Akademik");

                /*pb_ll_nilai_list.setVisibility(View.VISIBLE);
                isDelete = !isDelete;
                rcvAdapter = new RcvNilaiListAdapter(datasetSubject, isDelete);
                recycler_view_nilai_list.addItemDecoration(new DividerItemDecoration(requireContext(), LinearLayoutManager.VERTICAL));
                //recycler_view_nilai_list.addItemDecoration(new LineDividerItemDecoration(requireContext(), R.drawable.line_divider));
                recycler_view_nilai_list.setAdapter(rcvAdapter);
                pb_ll_nilai_list.setVisibility(View.GONE);*/
            }
        });

        return root;
    }

    private class RcvNilaiListAdapter extends RecyclerView.Adapter<RcvNilaiListAdapter.NilaiViewHolder> {
        private HashMap<String, String[]> subjectData;
        private boolean isDelete = false;

        public RcvNilaiListAdapter(HashMap<String, String[]> dataset, boolean isDelete) {
            this.subjectData = dataset;
            this.isDelete = isDelete;
        }

        public class NilaiViewHolder extends RecyclerView.ViewHolder {
            public ImageButton bt_nilai_component_delete;
            public TextView nilai_subject;
            public TextView nilai_subject_tahun;
            public String subjectPath;
            public int position;

            public NilaiViewHolder(LinearLayout itemView) {
                super(itemView);
                bt_nilai_component_delete = itemView.findViewById(R.id.bt_nilai_component_delete);
                nilai_subject = itemView.findViewById(R.id.nilai_subject);
                nilai_subject_tahun = itemView.findViewById(R.id.nilai_subject_tahun);
                if(isDelete){
                    bt_nilai_component_delete.setVisibility(View.VISIBLE);
                    View.OnClickListener onClick = view -> {
                        //pb_ll_nilai_list.setVisibility(View.VISIBLE);
                        final String nSubjectPath = subjectPath.substring(0, subjectPath.indexOf("&"));
                        mapelRef.child(nSubjectPath).setValue(null);

                        Fragment fragment = NilaiListFragment.newInstance(tipeKelas, namaKelas, mapelPath, mapel, false);
                        requireActivity().getSupportFragmentManager()
                                .beginTransaction()
                                .replace(R.id.nav_kelas_host_fragment, fragment)
                                .commit();
                        ((AppCompatActivity)requireActivity()).getSupportActionBar().setTitle("Nilai Akademik");

                        /*HashMap<String, String[]> nSubjectData = new HashMap<>();
                        final int len = subjectData.get(SUBJECT_PATH).length;
                        String[] subArr = new String[len];
                        String[] yearArr = new String[len];
                        String[] subjectArr = new String[len];
                        int l = 0;
                        for (int i = 0; i < len ; i++) {
                            if(i != position) {
                                subArr[l] = subjectData.get(SUBJECT_TITLE)[i];
                                yearArr[l] = subjectData.get(SUBJECT_TAHUN)[i];
                                subjectArr[l] = subjectData.get(SUBJECT_PATH)[i];
                                l++;
                            }
                        }
                        nSubjectData.put(SUBJECT_TITLE, subArr);
                        nSubjectData.put(SUBJECT_TAHUN, yearArr);
                        nSubjectData.put(SUBJECT_PATH, subjectArr);
                        datasetSubject = nSubjectData;
                        subjectData = nSubjectData;
                        isDelete = false;*/
                        //pb_ll_nilai_list.setVisibility(View.GONE);
                    };
                    bt_nilai_component_delete.setOnClickListener(onClick);
                    itemView.setOnClickListener(onClick);
                    itemView.setOnTouchListener(new View.OnTouchListener() {
                        float _xSwipe1;
                        float _xSwipe2;
                        @Override
                        public boolean onTouch(View v, MotionEvent event) {
                            switch (event.getAction()) {
                                case MotionEvent.ACTION_DOWN:
                                    _xSwipe1 = event.getX();
                                    break;
                                case MotionEvent.ACTION_UP:
                                    _xSwipe2 = event.getX();
                                    float deltaX = _xSwipe2 - _xSwipe1;
                                    /*if (deltaX < 0) {
                                        Log.e("SWIPE", "Right to Left swipe");
                                    }
                                    else */
                                    if (deltaX >0) {
                                        //Log.e("SWIPE", "Left to right swipe");
                                    }
                                    break;
                            }
                            return false;
                        }
                    });
                } else {
                    itemView.setOnClickListener(view -> {
                        Fragment fragment = NilaiDetailsFragment.newInstance(subjectPath, mapel, mapelPath, namaKelas);
                        requireActivity().getSupportFragmentManager()
                                .beginTransaction()
                                .replace(R.id.nav_kelas_host_fragment, fragment)
                                .addToBackStack(null)
                                .commit();
                    });
                }
            }
        }

        @NonNull
        @Override
        public RcvNilaiListAdapter.NilaiViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            LinearLayout linearLayout = (LinearLayout) LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.nilai_component, parent, false);
            return new NilaiViewHolder(linearLayout);
        }

        @Override
        public void onBindViewHolder(@NonNull RcvNilaiListAdapter.NilaiViewHolder holder, int position) {
            holder.subjectPath = subjectData.get(SUBJECT_PATH)[position];
            holder.nilai_subject.setText(subjectData.get(SUBJECT_TITLE)[position]);
            holder.nilai_subject_tahun.setText(subjectData.get(SUBJECT_TAHUN)[position]);
            holder.position = position;
        }

        @Override
        public int getItemCount() {
            final int cnt1 = subjectData.get(SUBJECT_TITLE).length;
            final int cnt2 = subjectData.get(SUBJECT_TAHUN).length;
            if(cnt1 == cnt2) {
                return cnt1;
            } else {
                return 0;
            }
        }
    }

    private class LineDividerItemDecoration extends RecyclerView.ItemDecoration {
        private Drawable mDivider;

        public LineDividerItemDecoration(Context context, int dividerDrawable) {
            mDivider = ContextCompat.getDrawable(context, dividerDrawable);
        }

        @Override
        public void onDrawOver(Canvas c, RecyclerView parent, RecyclerView.State state) {
            int left = parent.getPaddingLeft();
            int right = parent.getWidth() - parent.getPaddingRight();
            int childCount = parent.getChildCount();
            for (int i = 0; i < childCount; i++) {
                View child = parent.getChildAt(i);
                RecyclerView.LayoutParams params = (RecyclerView.LayoutParams) child.getLayoutParams();
                int top = child.getBottom() + params.bottomMargin;
                int bottom = top + mDivider.getIntrinsicHeight();
                mDivider.setBounds(left, top, right, bottom);
                mDivider.draw(c);
            }
        }
    }
}