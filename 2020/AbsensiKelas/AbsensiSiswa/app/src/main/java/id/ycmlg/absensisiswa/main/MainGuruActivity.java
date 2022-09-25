package id.ycmlg.absensisiswa.main;

import android.Manifest;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.snackbar.Snackbar;
import com.karumi.dexter.Dexter;
import com.karumi.dexter.listener.multi.CompositeMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.DialogOnAnyDeniedMultiplePermissionsListener;
import com.karumi.dexter.listener.multi.MultiplePermissionsListener;
import com.karumi.dexter.listener.multi.SnackbarOnAnyDeniedMultiplePermissionsListener;

import id.ycmlg.absensisiswa.R;
import id.ycmlg.absensisiswa.data.LocalUserService;
import id.ycmlg.absensisiswa.main.chat.chatservices.AppService;
import id.ycmlg.absensisiswa.main.guru.about.AboutGuruFragment;
import id.ycmlg.absensisiswa.main.guru.home.HomeGuruFragment;

public class MainGuruActivity extends AppCompatActivity implements BottomNavigationView.OnNavigationItemSelectedListener {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_guru);

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

        //loading the default fragment
        loadFragment(new HomeGuruFragment(), "Home");

        //getting bottom navigation view and attaching the listener
        BottomNavigationView bottomNavigationView = findViewById(R.id.navigation_guru);
        bottomNavigationView.setOnNavigationItemSelectedListener(this);
        bottomNavigationView.setSelectedItemId(R.id.bottom_navigation_home);
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        //Log.d("onNavItem:", "nav item selected.");
        Fragment fragment = null;
        String title = null;

        switch (item.getItemId()) {
            case R.id.bottom_navigation_home:
                fragment = new HomeGuruFragment();
                title = "Home";
                break;

            /*case R.id.bottom_navigation_history:
                fragment = new HistoryGuruFragment();
                title = "History";
                break;*/

            case R.id.bottom_navigation_about:
                fragment = new AboutGuruFragment();
                title = "About";
                break;

            default:
                //Log.d("onNavItem:", "item not defined, id:" + item.getItemId());
                fragment = new HomeGuruFragment();
                break;
        }

        return loadFragment(fragment, title);
    }

    private boolean loadFragment(Fragment fragment, String title) {
        //switching fragment
        if (fragment != null) {
            getSupportFragmentManager()
                    .beginTransaction()
                    .replace(R.id.fragment_container_guru, fragment)
                    .commit();
            this.getSupportActionBar().setTitle(title);
            return true;
        }
        return false;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        for (Fragment fragment : getSupportFragmentManager().getFragments()) {
            fragment.onActivityResult(requestCode, resultCode, data);
        }
    }

    @Override
    public void onPointerCaptureChanged(boolean hasCapture) {}

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