package id.ycmlg.absensisiswa.main.guru.history;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentActivity;
import androidx.viewpager2.adapter.FragmentStateAdapter;

public class HistoryGuruViewPagerAdapter extends FragmentStateAdapter {
    private static final int CARD_ITEM_SIZE = 2;
    private static String param = "";

    public HistoryGuruViewPagerAdapter(@NonNull FragmentActivity fragmentActivity) {
        super(fragmentActivity);
    }
    @NonNull
    @Override public Fragment createFragment(int position) {
        if (position == 0) {
            return PendingFragment.newInstance(param, position);
        } else {
            return TerkirimFragment.newInstance(param, position);
        }
    }
    @Override public int getItemCount() {
        return CARD_ITEM_SIZE;
    }
}
