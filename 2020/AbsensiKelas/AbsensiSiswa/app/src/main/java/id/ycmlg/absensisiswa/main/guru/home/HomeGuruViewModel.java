package id.ycmlg.absensisiswa.main.guru.home;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;

public class HomeGuruViewModel extends ViewModel {

    private MutableLiveData<String> mText;

    public HomeGuruViewModel() {
        mText = new MutableLiveData<>();
        mText.setValue("This is home fragment");
    }

    public LiveData<String> getText() {
        return mText;
    }
}