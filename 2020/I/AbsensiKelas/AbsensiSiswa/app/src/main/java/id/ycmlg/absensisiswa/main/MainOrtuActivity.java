package id.ycmlg.absensisiswa.main;

import android.Manifest;
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
import androidx.annotation.Nullable;
import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.navigation.ui.AppBarConfiguration;

import com.google.android.material.navigation.NavigationView;
import com.google.android.material.snackbar.Snackbar;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import com.karumi.dexter.Dexter;
import com.karumi.dexter.listener.multi.CompositeMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.DialogOnAnyDeniedMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.MultiplePermissionsListener;
import com.karumi.dexter.listener.multi.SnackbarOnAnyDeniedMultiplePermissionsListener;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.login.LoginActivity;
import id.ycmlg.absensisiswa.main.chat.ChatMainActivity;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.ortu.JadwalPelajaranOrtuFragment;
import id.ycmlg.absensisiswa.main.ortu.about.AboutOrtuFragment;
import id.ycmlg.absensisiswa.main.ortu.laporan.LaporanAbsensiOrtuFragment;
import id.ycmlg.absensisiswa.main.ortu.laporan.LaporanCatatanOrtuFragment;
import id.ycmlg.absensisiswa.main.ortu.laporan.LaporanNilaiAkademikOrtuFragment;
import id.ycmlg.absensisiswa.main.ortu.raport.RaportOrtuFragment;
import id.ycmlg.absensisiswa.main.util.ExpandableListAdapter;
import id.ycmlg.absensisiswa.main.util.MenuModel;

public class MainOrtuActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener, FragmentManager.OnBackStackChangedListener {
    private AppBarConfiguration mAppBarConfiguration;

    private ExpandableListAdapter expandableListAdapter;
    private ExpandableListView expandableListView;
    private List<MenuModel> headerList = new ArrayList<>();
    private HashMap<MenuModel, List<MenuModel>> childList = new HashMap<>();
    private String tipeKelas = null;
    private String namaKelas = null;
    private String nis = null;
    private String nm = null;
    final String chat = "Chat"; final String pChat = "chat";
    final String about = "About"; final String pAbout = "AboutOrtu";
    final String jadwalPelajaran = "Jadwal Pelajaran"; final String pJadwalPelajaran = "JadwalPelajaranOrtu";
    final String laporanAkademik = "Laporan Akademik";
    final String laporanAbsensi = "Laporan Absensi"; final String pLaporanAbsensi = "LaporanAbsensiOrtu";
    final String laporanCatatan = "Laporan Catatan"; final String pLaporanCatatan = "LaporanCatatanOrtu";
    final String laporanNilaiAkademik = "Laporan Nilai Akademik"; final String pLaporanNilaiAkademik= "LaporanNilaiAkademikOrtu";
    final String raport = "Raport"; final String pRaport = "RaportOrtu";
    //final String history = "History"; final String pHistory = "HistoryOrtu";
    private DrawerLayout drawer;
    private ActionBarDrawerToggle toggle;
    private TextView tv_nav_header_main_ortu_nama_siswa;
    private TextView tv_nav_header_main_ortu_nis;
    private FirebaseAuth firebaseAuth;
    private FirebaseDatabase database;
    private DatabaseReference userRef;
    private String userPath = "u";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_ortu);
        Toolbar toolbar = findViewById(R.id.toolbar_main_ortu);
        setSupportActionBar(toolbar);

        View parentLayout = findViewById(android.R.id.content);

        MultiplePermissionsListener dialogMultiplePermissionsListener =
                DialogOnAnyDeniedMultiplePermissionsListener.Builder
                        .withContext(this)
                        .withTitle("Storage permission")
                        .withMessage("Storage permission are needed to continue")
                        .withButtonText(android.R.string.ok)
                        .withIcon(R.mipmap.ic_launcher_foreground)
                        .build();

        MultiplePermissionsListener snackbarMultiplePermissionsListener =
                SnackbarOnAnyDeniedMultiplePermissionsListener.Builder
                        .with(parentLayout, "Storage permission are needed to continue")
                        .withOpenSettingsButton("Settings")
                        .withCallback(new Snackbar.Callback() {
                            @Override
                            public void onShown(Snackbar snackbar) {
                                // Event handler for when the given Snackbar is visible
                            }
                            @Override
                            public void onDismissed(Snackbar snackbar, int event) {
                                // Event handler for when the given Snackbar has been dismissed
                            }
                        })
                        .build();

        MultiplePermissionsListener compositePermissionsListener = new CompositeMultiplePermissionsListener(snackbarMultiplePermissionsListener, dialogMultiplePermissionsListener);

        Dexter.withContext(this)
                .withPermissions(
                        Manifest.permission.NFC,
                        Manifest.permission.INTERNET,
                        Manifest.permission.ACCESS_WIFI_STATE,
                        Manifest.permission.WRITE_EXTERNAL_STORAGE,
                        Manifest.permission.READ_EXTERNAL_STORAGE
                ).withListener(compositePermissionsListener).onSameThread().check();

        //FirebaseDatabase.getInstance().setPersistenceEnabled(true);
        firebaseAuth = FirebaseAuth.getInstance();
        database = FirebaseDatabase.getInstance();
        userRef = database.getReference(userPath);
        if(firebaseAuth.getCurrentUser() == null){
            Intent intent = new Intent(this, LoginActivity.class);
            finish();
            startActivity(intent);
        } else {
            DatabaseReference uuid = userRef.child(firebaseAuth.getCurrentUser().getUid());
            uuid.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override public void onDataChange(@NonNull DataSnapshot snapshot) {
                    nm = snapshot.child("na").getValue().toString();
                    nis = snapshot.child("un").getValue().toString();
                    namaKelas = snapshot.child("kls").getValue().toString();

                    expandableListView = findViewById(R.id.expandable_list_view_main_ortu);
                    prepareMenuData(tipeKelas, namaKelas, nis);
                    populateExpandableList();

                    drawer = findViewById(R.id.drawer_layout_main_ortu);
                    toggle = new ActionBarDrawerToggle(
                            MainOrtuActivity.this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
                    drawer.addDrawerListener(toggle);
                    toggle.syncState();

                    NavigationView navigationView = findViewById(R.id.nav_view_main_ortu);
                    navigationView.setNavigationItemSelectedListener(MainOrtuActivity.this);

                    //default first page to show
                    Fragment fragment = new AboutOrtuFragment();
                    loadFragment(fragment, about);

                    //Listen for changes in the back stack
                    getSupportFragmentManager().addOnBackStackChangedListener(MainOrtuActivity.this);
                    //Handle when activity is recreated like on orientation Change
                    shouldDisplayHomeUp();

                    View headerView = navigationView.getHeaderView(0);
                    tv_nav_header_main_ortu_nama_siswa = headerView.findViewById(R.id.tv_nav_header_main_ortu_nama_siswa);
                    tv_nav_header_main_ortu_nis = headerView.findViewById(R.id.tv_nav_header_main_ortu_nis);

                    if(nm != null) tv_nav_header_main_ortu_nama_siswa.setText(nm);//nama anak
                    if(nis != null) tv_nav_header_main_ortu_nis.setText(nis);
                }
                @Override public void onCancelled(@NonNull DatabaseError error) {}
            });
        }
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
    protected void onStop() {
        super.onStop();
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout_main_ortu);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main_ortu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.nav_home_main_ortu) {
        } else if (id == R.id.nav_gallery_main_ortu) {

        } else if (id == R.id.nav_slideshow_main_ortu) {

        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout_main_ortu);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    @Override
    public boolean onSupportNavigateUp() {
        getSupportFragmentManager().popBackStack();
//        NavController navController = Navigation.findNavController(this, R.id.nav_main_ortu_host_fragment);
//        return NavigationUI.navigateUp(navController, mAppBarConfiguration)
//                || super.onSupportNavigateUp();
        return true;
    }

    public void shouldDisplayHomeUp(){
        //Enable Up button only  if there are entries in the back stack
        boolean canGoBack = getSupportFragmentManager().getBackStackEntryCount()>0;
        getSupportActionBar().setDisplayHomeAsUpEnabled(canGoBack);
        //getSupportActionBar().setDisplayShowHomeEnabled(canGoBack);
        toggle.setDrawerIndicatorEnabled(!canGoBack);
    }

    private void prepareMenuData(String tipeKelas, String namaKelas, String nis) {
        //Nosub
        MenuModel menuModel = new MenuModel(chat, true, false, pChat);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }
        menuModel = new MenuModel(about, true, false, pAbout);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }
        menuModel = new MenuModel(jadwalPelajaran, true, false, pJadwalPelajaran);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }

        //Withsub
        List<MenuModel> childModelsList = new ArrayList<>();
        menuModel = new MenuModel(laporanAkademik, true, true, "");
        headerList.add(menuModel);
        MenuModel childModel = new MenuModel(laporanAbsensi, false, false, pLaporanAbsensi);
        childModelsList.add(childModel);
        childModel = new MenuModel(laporanCatatan, false, false, pLaporanCatatan);
        childModelsList.add(childModel);
        childModel = new MenuModel(laporanNilaiAkademik, false, false, pLaporanNilaiAkademik);
        childModelsList.add(childModel);
        if (menuModel.hasChildren) { childList.put(menuModel, childModelsList); }

        menuModel = new MenuModel(raport, true, false, pRaport);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }
        /*menuModel = new MenuModel(history, true, false, pHistory);
        headerList.add(menuModel);
        if (!menuModel.hasChildren) { childList.put(menuModel, null); }*/

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
                    Fragment fragment;
                    if (headerList.get(groupPosition).path.hashCode() == pChat.hashCode()){
                        Intent startChat = new Intent(MainOrtuActivity.this, ChatMainActivity.class);
                        startActivity(startChat);
                    } else if (headerList.get(groupPosition).path.contentEquals(pAbout)){
                        fragment = new AboutOrtuFragment();
                        loadFragment(fragment, about);
                    } else if (headerList.get(groupPosition).path.contentEquals(pJadwalPelajaran)){
                        fragment = JadwalPelajaranOrtuFragment.newInstance(namaKelas, null);
                        loadFragment(fragment, jadwalPelajaran);
                    } else if (headerList.get(groupPosition).path.contentEquals(pRaport)){
                        fragment = RaportOrtuFragment.newInstance(namaKelas, nis);
                        loadFragment(fragment, raport);
                    } /*else if (headerList.get(groupPosition).path.contentEquals(pHistory)){
                        fragment = new HistoryOrtuFragment();
                        loadFragment(fragment, history);
                    }*/
                    //onBackPressed();
                }
            }

            return false;
        });

        expandableListView.setOnChildClickListener((parent, v, groupPosition, childPosition, id) -> {
            if (childList.get(headerList.get(groupPosition)) != null) {
                MenuModel model = childList.get(headerList.get(groupPosition)).get(childPosition);
                if (model.path.length() > 0) {
                    //load view when child clicked
                    Fragment fragment;

                    if (model.path.contentEquals(pLaporanAbsensi)) {
                        fragment = LaporanAbsensiOrtuFragment.newInstance(namaKelas, nis);
                        loadFragment(fragment, laporanAbsensi);
                    } else if (model.path.contentEquals(pLaporanCatatan)){
                        fragment = LaporanCatatanOrtuFragment.newInstance(namaKelas, nis);
                        loadFragment(fragment, laporanCatatan);
                    } else if (model.path.contentEquals(pLaporanNilaiAkademik)){
                        fragment = LaporanNilaiAkademikOrtuFragment.newInstance(namaKelas, nis);
                        loadFragment(fragment, laporanNilaiAkademik);
                    }

                    //onBackPressed();
                }
            }

            return false;
        });
    }

    private boolean loadFragment(Fragment fragment, String title) {
        //switching fragment
        if (fragment != null) {
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.nav_main_ortu_host_fragment, fragment)
                    .commit();
            this.getSupportActionBar().setTitle(title);
            if (drawer.isOpen()) drawer.close();
            return true;
        }
        return false;
    }

    @Override
    public void onBackStackChanged() {
        shouldDisplayHomeUp();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        for (Fragment fragment : getSupportFragmentManager().getFragments()) {
            fragment.onActivityResult(requestCode, resultCode, data);
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