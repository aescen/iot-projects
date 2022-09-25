package id.ycmlg.absensisiswa.main.util;

public class MenuModel {
    public String menuName, path;
    public boolean hasChildren, isGroup;

    public MenuModel(String menuName, boolean isGroup, boolean hasChildren, String path) {

        this.menuName = menuName;
        this.path = path;
        this.isGroup = isGroup;
        this.hasChildren = hasChildren;
    }
}
