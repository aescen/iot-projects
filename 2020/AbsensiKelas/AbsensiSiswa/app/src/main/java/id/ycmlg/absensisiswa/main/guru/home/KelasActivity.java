package id.ycmlg.absensisiswa.main.guru.home;

import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.ExpandableListView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.navigation.ui.AppBarConfiguration;

import com.google.android.material.navigation.NavigationView;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.login.LoginActivity;
import id.ycmlg.absensisiswa.main.chat.ChatMainActivity;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.AbsensiFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.DaftarSiswaFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.JadwalPelajaranFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.LaporanCatatanGuruFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.PelanggaranFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.SikapFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.ijin.PermintaanIjinFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.nfcread.ReadNFCFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.nilaiakademik.NilaiListFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.raport.GuruRaportFragment;
import id.ycmlg.absensisiswa.main.guru.home.menukelas.raport.LaporanGuruRaportFragment;
import id.ycmlg.absensisiswa.main.util.ExpandableListAdapter;
import id.ycmlg.absensisiswa.main.util.MenuModel;

public class KelasActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener, FragmentManager.OnBackStackChangedListener {
    private AppBarConfiguration mAppBarConfiguration;

    private ExpandableListAdapter expandableListAdapter;
    private ExpandableListView expandableListView;
    private List<MenuModel> headerList = new ArrayList<>();
    private HashMap<MenuModel, List<MenuModel>> childList = new HashMap<>();

    final String chat = "Chat"; final String pChat = "chat";
    final String pJadwalPelajaran = "JadwalPelajaran"; final String pDaftarSiswa = "DaftarSiswa";
    final String pAbsensi = "Absensi"; final String pBacaNFC = "BacaNFC"; final String pMintaIjin = "Permintaan Ijin";
    final String pSikap = "Sikap"; final String pPelanggaran = "Pelanggaran"; final String pLaporanCatatan = "LaporanCatatan";
    final String pPAgama = "PAgama"; final String pPPKn = "PPKn"; final String pPBI = "PBI";final String pPMTK = "PMTK";
    final String pPIPA = "PIPA";final String pPIPS = "PIPS";
    final String pPSBP = "PSBP"; final String pPJDK = "PJDK"; final String pPTIK = "PTIK"; final String pPBING = "PBING"; final String pPBJ = "PBJ";
    final String pRaport = "Raport"; final String pLaporanRaport = "LaporanRaport";
    final String jadwalPelajaran = "Jadwal Pelajaran"; final String daftarSiswa = "Daftar Siswa";
    final String absensi = "Absensi"; final String bacaNFC = "Baca kartu NFC"; final String mintaIjin = "Permintaan Ijin";
    final String catatan = "Catatan"; final String sikap = "Sikap"; final String pelanggaran = "Pelanggaran"; final String laporanCatatan = "Laporan Catatan";
    final String nilaiAkademik = "Nilai Akademik"; final String agama = "Pendidikan Agama"; final String ppkn = "Pend. Pancasila & Kewarganegaraan"; final String bi = "Bahasa Indonesia"; final String mtk = "Matematika";
    final String ipa = "IPA"; final String ips = "IPS";
    final String sbp = "Seni Budaya & Prakarya"; final String pjdk = "PJDK"; final String tik = "TIK"; final String bing = "Bahasa Inggris"; final String bj = "Bahasa Jawa";
    final String raport = "Raport"; final String laporanRaport = "Laporan Raport";
    private String tipeKelas;
    private String namaKelas;
    private DrawerLayout drawer;
    private ActionBarDrawerToggle toggle;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private String userPath = "u";
    private TextView tv_nav_header_kelas_nama_guru;
    private TextView tv_nav_header_kelas_nama;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_kelas);
        Toolbar toolbar = findViewById(R.id.toolbar_kelas);
        setSupportActionBar(toolbar);

        Intent intent = getIntent();
        tipeKelas = intent.getStringExtra(getString(R.string.var_tipe_kelas));
        namaKelas = intent.getStringExtra(getString(R.string.var_nama_kelas));

        //FirebaseDatabase.getInstance().setPersistenceEnabled(true);
        firebaseAuth = FirebaseAuth.getInstance();
        database = FirebaseDatabase.getInstance();
        userRef = database.getReference(userPath);
        if(firebaseAuth.getCurrentUser() == null){
            intent = new Intent(this, LoginActivity.class);
            finish();
            startActivity(intent);
        }

        expandableListView = findViewById(R.id.expandable_list_view_kelas);
        prepareMenuData(tipeKelas, namaKelas);
        populateExpandableList();

        drawer = findViewById(R.id.drawer_layout_kelas);
        toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.setDrawerIndicatorEnabled(true);
        toggle.syncState();

        NavigationView navigationView = findViewById(R.id.nav_view_kelas);
        navigationView.setNavigationItemSelectedListener(this);

        //default first page to show
        Fragment fragment = JadwalPelajaranFragment.newInstance(namaKelas.replaceAll("\\s+","").trim().toLowerCase());
        loadFragment(fragment, jadwalPelajaran);

        //Listen for changes in the back stack
        getSupportFragmentManager().addOnBackStackChangedListener(this);
        //Handle when activity is recreated like on orientation Change
        shouldDisplayHomeUp();

        View headerView = navigationView.getHeaderView(0);
        tv_nav_header_kelas_nama_guru = headerView.findViewById(R.id.tv_nav_header_kelas_nama_guru);
        tv_nav_header_kelas_nama = headerView.findViewById(R.id.tv_nav_header_kelas_nama);

        tv_nav_header_kelas_nama.setText(namaKelas);

        DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
        uuid.addListenerForSingleValueEvent(new ValueEventListener() {
            @Override public void onDataChange(@NonNull DataSnapshot snapshot) {
                String nl = snapshot.child("nl").getValue().toString();
                if(nl != null) tv_nav_header_kelas_nama_guru.setText(nl);
            }
            @Override public void onCancelled(@NonNull DatabaseError error) {}
        });

    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout_kelas);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.kelas, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        } else if (item.getItemId()==android.R.id.home) {
            super.onBackPressed();
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.nav_home_kelas) {
        } else if (id == R.id.nav_gallery_kelas) {

        } else if (id == R.id.nav_slideshow_kelas) {

        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout_kelas);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @Override
    public boolean onSupportNavigateUp() {
        getSupportFragmentManager().popBackStack();
//        NavController navController = Navigation.findNavController(this, R.id.nav_kelas_host_fragment);
//        return NavigationUI.navigateUp(navController, mAppBarConfiguration)
//                || super.onSupportNavigateUp();
        return true;
    }

    @Override
    public void onBackStackChanged() {
        shouldDisplayHomeUp();
    }

    public void shouldDisplayHomeUp(){
        //Enable Up button only  if there are entries in the back stack
        boolean canGoBack = getSupportFragmentManager().getBackStackEntryCount()>0;
        getSupportActionBar().setDisplayHomeAsUpEnabled(canGoBack);
        //getSupportActionBar().setDisplayShowHomeEnabled(canGoBack);
        toggle.setDrawerIndicatorEnabled(!canGoBack);
    }

    private void prepareMenuData(String tipeKelas, String namaKelas) {
        //Nosub
        MenuModel menuModel = new MenuModel(chat, true, false, pChat);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }
        menuModel = new MenuModel(jadwalPelajaran, true, false, pJadwalPelajaran);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }
        menuModel = new MenuModel(daftarSiswa, true, false, pDaftarSiswa);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }

        //Withsub
        List<MenuModel> childModelsList = new ArrayList<>();
        menuModel = new MenuModel(absensi, true, true, "");
        headerList.add(menuModel);
        MenuModel childModel = new MenuModel(absensi, false, false, pAbsensi);
        childModelsList.add(childModel);
        childModel = new MenuModel(bacaNFC, false, false, pBacaNFC);
        childModelsList.add(childModel);
        childModel = new MenuModel(mintaIjin, false, false, pMintaIjin);
        childModelsList.add(childModel);
        if (menuModel.hasChildren) { childList.put(menuModel, childModelsList); }

        childModelsList = new ArrayList<>();
        menuModel = new MenuModel(catatan, true, true, ""); //Menu of Python Tutorials
        headerList.add(menuModel);
        childModel = new MenuModel(sikap, false, false, pSikap);
        childModelsList.add(childModel);
        childModel = new MenuModel(pelanggaran, false, false, pPelanggaran);
        childModelsList.add(childModel);
        childModel = new MenuModel(laporanCatatan, false, false, pLaporanCatatan);
        childModelsList.add(childModel);
        if (menuModel.hasChildren) { childList.put(menuModel, childModelsList); }

        childModelsList = new ArrayList<>();
        menuModel = new MenuModel(nilaiAkademik, true, true, ""); //Menu of Python Tutorials
        headerList.add(menuModel);
        childModel = new MenuModel(agama, false, false, pPAgama);
        childModelsList.add(childModel);
        childModel = new MenuModel(ppkn, false, false, pPPKn);
        childModelsList.add(childModel);
        childModel = new MenuModel(bi, false, false, pPBI);
        childModelsList.add(childModel);
        childModel = new MenuModel(mtk, false, false, pPMTK);
        childModelsList.add(childModel);

        //if(tipeKelas !=null &&
        //    tipeKelas.contentEquals(getString(R.string.const_kelas_rendah))){
        //}else
        if(tipeKelas != null &&
            tipeKelas.contentEquals(getString(R.string.const_kelas_tinggi))){
            childModel = new MenuModel(ipa, false, false, pPIPA);
            childModelsList.add(childModel);
            childModel = new MenuModel(ips, false, false, pPIPS);
            childModelsList.add(childModel);
        }

        //else{
        //    Log.e("MenuData", "prepareMenuData: Error tipeKelas = " + tipeKelas);
        //}
        childModel = new MenuModel(sbp, false, false, pPSBP);
        childModelsList.add(childModel);
        childModel = new MenuModel(pjdk, false, false, pPJDK);
        childModelsList.add(childModel);
        childModel = new MenuModel(tik, false, false, pPTIK);
        childModelsList.add(childModel);
        childModel = new MenuModel(bing, false, false, pPBING);
        childModelsList.add(childModel);
        childModel = new MenuModel(bj, false, false, pPBJ);
        childModelsList.add(childModel);
        if (menuModel.hasChildren) { childList.put(menuModel, childModelsList); }

        childModelsList = new ArrayList<>();
        menuModel = new MenuModel(raport, true, true, ""); //Menu of Python Tutorials
        headerList.add(menuModel);
        childModel = new MenuModel(raport, false, false, pRaport);
        childModelsList.add(childModel);
        childModel = new MenuModel(laporanRaport, false, false, pLaporanRaport);
        childModelsList.add(childModel);
        if (menuModel.hasChildren) { childList.put(menuModel, childModelsList); }
    }

    private void populateExpandableList() {
        expandableListAdapter = new ExpandableListAdapter(this, headerList, childList);
        expandableListView.setAdapter(expandableListAdapter);

        //expand all group
        for(int i = 0; i < expandableListAdapter.getGroupCount(); i++) {
            expandableListView.expandGroup(i);
        }

        expandableListView.setOnGroupClickListener((parent, v, groupPosition, id) -> {
            if (headerList.get(groupPosition).isGroup) {
                if (!headerList.get(groupPosition).hasChildren) {
                    //load view when group clicked
                    Fragment fragment1;
                    //final String pJadwalPelajaran = "JadwalPelajaran"; final String pDaftarSiswa = "DaftarSiswa";
                    if (headerList.get(groupPosition).path.hashCode() == pChat.hashCode()){
                        Intent startChat = new Intent(KelasActivity.this, ChatMainActivity.class);
                        startActivity(startChat);
                    } else if (headerList.get(groupPosition).path.hashCode() == pJadwalPelajaran.hashCode()){
                        fragment1 = JadwalPelajaranFragment.newInstance(namaKelas.replaceAll("\\s+","").trim().toLowerCase());
                        loadFragment(fragment1, jadwalPelajaran);
                    } else if (headerList.get(groupPosition).path.hashCode() == pDaftarSiswa.hashCode()){
                        fragment1 = DaftarSiswaFragment.newInstance(namaKelas, null);
                        loadFragment(fragment1, daftarSiswa);
                    }
                }
            }

            return false;
        });

        expandableListView.setOnChildClickListener((parent, v, groupPosition, childPosition, id) -> {
            if (childList.get(headerList.get(groupPosition)) != null) {
                MenuModel model = childList.get(headerList.get(groupPosition)).get(childPosition);
                if (model.path.length() > 0) {
                    //load view when child clicked
                    Fragment fragment12;

                    //final String pAbsensi = "Absensi"; final String pBacaNFC = "BacaNFC"; final String pMintaIjin = "Permintaan Ijin";
                    if (model.path.hashCode() == pAbsensi.hashCode()) {
                        fragment12 = AbsensiFragment.newInstance(namaKelas, null);
                        loadFragment(fragment12, absensi);
                    } else if (model.path.contentEquals(pBacaNFC)){
                        fragment12 = ReadNFCFragment.newInstance(namaKelas, null);
                        loadFragment(fragment12, bacaNFC);
                    } else if (model.path.contentEquals(pMintaIjin)){
                        fragment12 = PermintaanIjinFragment.newInstance(namaKelas, null);
                        loadFragment(fragment12, mintaIjin);
                    }
                    //final String pSikap = "Sikap"; final String pPelanggaran = "Pelanggaran"; final String pLaporanCatatan = "LaporanCatatan";
                    else if (model.path.contentEquals(pSikap)){
                        fragment12 = SikapFragment.newInstance(namaKelas, null, null, null);
                        loadFragment(fragment12, sikap);
                    } else if (model.path.contentEquals(pPelanggaran)){
                        fragment12 = PelanggaranFragment.newInstance(namaKelas, null, null, null);
                        loadFragment(fragment12, pelanggaran);
                    } else if (model.path.contentEquals(pLaporanCatatan)){
                        fragment12 = LaporanCatatanGuruFragment.newInstance(namaKelas, null);
                        loadFragment(fragment12, laporanCatatan);
                    }
                    //final String pPAgama = "PAgama"; final String pPPKn = "PPKn"; final String pPBI = "PBI";final String pPMTK = "PMTK";
                    //String agama = "Pendidikan Agama"; String ppkn = "Pend. Pancasila & Kewarganegaraan"; String bi = "Bahasa Indonesia"; String mtk = "Matematika";
                    else if (model.path.contentEquals(pPAgama)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPAgama, agama, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPPKn)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPPKn, ppkn, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPBI)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPBI, bi, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPMTK)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPMTK, mtk, null);
                        loadFragment(fragment12, nilaiAkademik);
                    }
                    //final String pPIPA = "PIPA";final String pPIPS = "PIPS";
                    //String ipa = "IPA"; String ips = "IPS";
                    else if (model.path.contentEquals(pPIPA)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPIPA, ipa, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPIPS)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPIPS, ips, null);
                        loadFragment(fragment12, nilaiAkademik);
                    }
                    //final String pPSBP = "PSBP"; final String pPJDK = "PJDK"; final String pPTIK = "PTIK"; final String pPBING = "PBING"; final String pPJ = "PJ";
                    //String sbp = "Seni Budaya & Prakarya"; String pjdk = "PJDK"; String tik = "TIK"; String bing = "Bahasa Inggris";String bj = "Bahasa Jawa";
                    else if (model.path.contentEquals(pPSBP)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPSBP, sbp, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPJDK)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPJDK, pjdk, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPTIK)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPTIK, tik, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPBING)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPBING, bing, null);
                        loadFragment(fragment12, nilaiAkademik);
                    } else if (model.path.contentEquals(pPBJ)){
                        fragment12 = NilaiListFragment.newInstance(tipeKelas, namaKelas, pPBJ, bj, null);
                        loadFragment(fragment12, nilaiAkademik);
                    }
                    //final String pRaport = "Raport"; final String pLaporanRaport = "LaporanRaport";
                    else if (model.path.contentEquals(pRaport)){
                        fragment12 = GuruRaportFragment.newInstance(namaKelas, null);
                        fragment12.setRetainInstance(true);
                        loadFragment(fragment12, raport);
                    } else if (model.path.contentEquals(pLaporanRaport)){
                        fragment12 = LaporanGuruRaportFragment.newInstance(namaKelas, null);
                        loadFragment(fragment12, laporanRaport);
                    }

                    //onBackPressed();
                }
            }

            return false;
        });
    }

    private boolean loadFragment(Fragment fragment, String title) {
        //switching fragment
        if (title == null) title = "";
        if (fragment != null) {
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.nav_kelas_host_fragment, fragment)
                    .commit();
            this.getSupportActionBar().setTitle(title);
            if (drawer.isOpen()) drawer.close();
            return true;
        }
        return false;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
    }

    @Override
    protected void onStart() {
        super.onStart();
        if (!LocalUserService.isAppServiceRunning(this)) {
            try {
                if(LocalUserService.isAppVisible()) startService(new Intent(this, AppService.class));
            } catch (Exception e) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    //startForegroundService(new Intent(this, AppService.class));
                }
                e.printStackTrace();
            }
            //Toast.makeText(this, "Running service ...", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        LocalUserService.appResumed();
    }

    @Override
    protected void onPause() {
        super.onPause();
        LocalUserService.appPaused();
    }
}